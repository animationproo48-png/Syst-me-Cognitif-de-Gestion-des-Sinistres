# backend/routers/advisor.py

from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from backend.database import get_db
from backend.models import EscaladeDB, SinistreDB, ClientDB, ConseillerDB

router = APIRouter(prefix="/api/v1", tags=["Advisor"])


@router.get("/escalades/queue")
async def get_escalades_queue(db: Session = Depends(get_db)):
    """Retourne la file d'escalades en attente."""
    escalades = db.query(EscaladeDB).filter(EscaladeDB.status == "en_attente").all()

    results = []
    for e in escalades:
        sinistre = db.query(SinistreDB).filter(SinistreDB.id == e.sinistre_id).first()
        client = db.query(ClientDB).filter(ClientDB.id == sinistre.client_id).first() if sinistre else None
        conseiller = db.query(ConseillerDB).filter(ConseillerDB.id == e.conseiller_id).first() if e.conseiller_id else None

        results.append({
            "escalade_id": str(e.id),
            "status": e.status,
            "raison": e.raison_escalade,
            "cci_score": e.cci_score_trigger,
            "date_escalade": e.date_escalade,
            "sinistre": {
                "id": str(sinistre.id) if sinistre else None,
                "numero": sinistre.numero_sinistre if sinistre else None,
                "type": sinistre.type_sinistre if sinistre else None,
                "status": sinistre.status_dossier if sinistre else None,
            },
            "client": {
                "id": str(client.id) if client else None,
                "matricule": client.matricule if client else None,
                "nom": client.nom if client else None,
                "prenom": client.prenom if client else None,
                "telephone": client.telephone if client else None,
            },
            "conseiller": {
                "id": str(conseiller.id) if conseiller else None,
                "nom": conseiller.nom if conseiller else None,
                "prenom": conseiller.prenom if conseiller else None,
                "email": conseiller.email if conseiller else None,
            } if conseiller else None
        })

    return {"count": len(results), "items": results}


@router.get("/conseillers")
async def list_conseillers(db: Session = Depends(get_db)):
    """Liste des conseillers."""
    conseillers = db.query(ConseillerDB).all()
    return [
        {
            "id": str(c.id),
            "nom": c.nom,
            "prenom": c.prenom,
            "email": c.email,
            "statut": c.statut,
            "nombre_dossiers_actifs": c.nombre_dossiers_actifs,
            "capacite_max": c.capacite_max
        }
        for c in conseillers
    ]
