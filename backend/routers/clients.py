# backend/routers/clients.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import desc
from uuid import UUID
from datetime import datetime

from backend.database import get_db
from backend.models import ClientDB, SinistreDB, RemboursementDB, ContratDB, ActionRecommandeeDB, ConseillerDB, EscaladeDB
from backend.schemas.schemas import ClientResponse, ClientCreate, SinistreResponse, SuiviDossierResponse, ActionTimelineItem, RemboursementResponse

router = APIRouter(prefix="/api/v1", tags=["Clients"])


# ============================================================
# GET CLIENT BY MATRICULE (PHASE 1: AUTH)
# ============================================================
@router.get("/clients/{matricule}", response_model=ClientResponse)
async def get_client_by_matricule(matricule: str, db: Session = Depends(get_db)):
    """Récupère client par matricule pour PHASE 1: AUTHENTIFICATION"""
    client = db.query(ClientDB).filter(ClientDB.matricule == matricule).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client {matricule} non trouvé"
        )
    
    return client


@router.post("/clients", response_model=ClientResponse)
async def create_client(client: ClientCreate, db: Session = Depends(get_db)):
    """Créer un nouveau client"""
    existing = db.query(ClientDB).filter(ClientDB.matricule == client.matricule).first()
    if existing:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail="Matricule déjà existant"
        )
    
    db_client = ClientDB(**client.dict())
    db.add(db_client)
    db.commit()
    db.refresh(db_client)
    return db_client


# ============================================================
# GET CLIENT DOSSIERS ACTIFS
# ============================================================
@router.get("/clients/{client_id}/sinistres", response_model=list[SinistreResponse])
async def get_client_sinistres(client_id: UUID, db: Session = Depends(get_db)):
    """Récupère sinistres actifs du client"""
    sinistres = db.query(SinistreDB).filter(
        SinistreDB.client_id == client_id,
        SinistreDB.status_dossier != "fermé"
    ).order_by(desc(SinistreDB.date_creation)).all()
    
    return sinistres


# ============================================================
# CREATE SINISTRE (PHASE 5: DECISION)
# ============================================================
@router.post("/sinistres", response_model=SinistreResponse)
async def create_sinistre(
    client_id: UUID,
    type_sinistre: str,
    date_sinistre: str,
    lieu_sinistre: str,
    description: str,
    cci_score: int = 0,
    db: Session = Depends(get_db)
):
    """Créer sinistre après PHASE 5"""
    from datetime import datetime as dt
    
    # Générer numéro sinistre
    client = db.query(ClientDB).filter(ClientDB.id == client_id).first()
    numero_sinistre = f"SINS-{client.matricule}-{dt.now().strftime('%y%m%d%H%M%S')}"
    
    db_sinistre = SinistreDB(
        client_id=client_id,
        numero_sinistre=numero_sinistre,
        type_sinistre=type_sinistre,
        date_sinistre=dt.fromisoformat(date_sinistre).date(),
        lieu_sinistre=lieu_sinistre,
        description=description,
        cci_score=cci_score,
        status_dossier="en_cours",
        type_traitement="autonome"
    )
    
    db.add(db_sinistre)
    db.flush()
    
    # Créer remboursement par défaut
    remboursement = RemboursementDB(
        sinistre_id=db_sinistre.id,
        montant_reclame=0,
        status="en_attente"
    )
    db.add(remboursement)
    
    db.commit()
    db.refresh(db_sinistre)
    return db_sinistre


# ============================================================
# SUIVI DOSSIER (PHASE 7)
# ============================================================
@router.get("/sinistres/{sinistre_id}/suivi", response_model=SuiviDossierResponse)
async def suivi_dossier(sinistre_id: UUID, db: Session = Depends(get_db)):
    """Récupère état complet dossier - PHASE 7: SUIVI"""
    sinistre = db.query(SinistreDB).filter(SinistreDB.id == sinistre_id).first()
    
    if not sinistre:
        raise HTTPException(status_code=404, detail="Sinistre non trouvé")
    
    # Remboursement
    remboursement = db.query(RemboursementDB).filter(
        RemboursementDB.sinistre_id == sinistre_id
    ).first()
    
    # Actions
    actions = db.query(ActionRecommandeeDB).filter(
        ActionRecommandeeDB.sinistre_id == sinistre_id,
        ActionRecommandeeDB.status != "completée"
    ).all()
    
    # Timeline
    timeline_actions = [
        ActionTimelineItem(
            action="Déclaration reçue",
            date=sinistre.date_creation,
            status="✅ Complété",
            details={}
        ),
    ]
    
    # Ajouter escalade si applicable
    escalade = db.query(EscaladeDB).filter(EscaladeDB.sinistre_id == sinistre_id).first()
    if escalade and escalade.date_transfert:
        conseiller = db.query(ConseillerDB).filter(ConseillerDB.id == escalade.conseiller_id).first()
        if conseiller:
            timeline_actions.append(
                ActionTimelineItem(
                    action=f"Assigné à {conseiller.prenom} {conseiller.nom}",
                    date=escalade.date_escalade,
                    status="✅ Complété",
                    details={"conseiller": conseiller.telephone}
                )
            )
    
    # Actions en attente
    for action in actions:
        timeline_actions.append(
            ActionTimelineItem(
                action=action.action,
                date=action.date_limite,
                status=f"⏳ {action.status}",
                details={"description": action.description}
            )
        )
    
    # Garanties
    client = db.query(ClientDB).filter(ClientDB.id == sinistre.client_id).first()
    contrat = db.query(ContratDB).filter(ContratDB.client_id == client.id).first()
    
    garanties_applicables = []
    if contrat:
        if contrat.garantie_collision:
            garanties_applicables.append({
                "garantie": "Dommages Collision",
                "couverture": "80%",
                "franchise": float(contrat.franchise_collision),
                "limite": float(contrat.limite_collision)
            })
        if contrat.garantie_vol:
            garanties_applicables.append({
                "garantie": "Vol",
                "couverture": "80%",
                "franchise": float(contrat.franchise_vol),
                "limite": float(contrat.limite_vol)
            })
        if contrat.garantie_assistance:
            garanties_applicables.append({
                "garantie": "Assistance 24h",
                "couverture": "Incluse",
                "dépannage": "Gratuit"
            })
    
    remb_response = None
    if remboursement:
        remb_response = RemboursementResponse(
            id=remboursement.id,
            montant_reclame=remboursement.montant_reclame,
            montant_accepte=remboursement.montant_accepte,
            franchise=remboursement.franchise,
            status=remboursement.status,
            date_paiement=remboursement.date_paiement
        )
    
    return SuiviDossierResponse(
        numero_sinistre=sinistre.numero_sinistre,
        type_sinistre=sinistre.type_sinistre,
        date_declaration=sinistre.date_creation.date(),
        status_dossier=sinistre.status_dossier,
        timeline_actions=timeline_actions,
        remboursement=remb_response,
        garanties_applicables=garanties_applicables,
        actions_client=[{"action": a.action, "date_limite": a.date_limite} for a in actions],
        messages_recents=[]
    )


# ============================================================
# CRUD OPERATIONS FOR ADVISOR DASHBOARD
# ============================================================
@router.get("/clients", response_model=list[ClientResponse])
async def list_all_clients(skip: int = 0, limit: int = 100, db: Session = Depends(get_db)):
    """Liste tous les clients (pour dashboard advisor)"""
    clients = db.query(ClientDB).offset(skip).limit(limit).all()
    return clients


@router.put("/clients/{client_id}", response_model=ClientResponse)
async def update_client(client_id: UUID, client_update: ClientCreate, db: Session = Depends(get_db)):
    """Mettre à jour un client"""
    db_client = db.query(ClientDB).filter(ClientDB.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    for key, value in client_update.dict(exclude_unset=True).items():
        setattr(db_client, key, value)
    
    db.commit()
    db.refresh(db_client)
    return db_client


@router.delete("/clients/{client_id}")
async def delete_client(client_id: UUID, db: Session = Depends(get_db)):
    """Supprimer un client"""
    db_client = db.query(ClientDB).filter(ClientDB.id == client_id).first()
    if not db_client:
        raise HTTPException(status_code=404, detail="Client non trouvé")
    
    db.delete(db_client)
    db.commit()
    return {"message": f"Client {db_client.matricule} supprimé"}
