# backend/routers/operations.py

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import func
from uuid import UUID
from datetime import datetime, date
from typing import Optional

from backend.database import get_db
from backend.models import ClientDB, SinistreDB, ContratDB, RemboursementDB, EscaladeDB, ConseillerDB

router = APIRouter(prefix="/api/v1", tags=["Operations"])


# =========================
# Helpers
# =========================

def _uuid(value):
    return str(value) if value else None


def _dt(value):
    if not value:
        return None
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    return str(value)


def _sinistre_to_dict(s: SinistreDB, client: Optional[ClientDB] = None):
    return {
        "id": _uuid(s.id),
        "numero_sinistre": s.numero_sinistre,
        "client_id": _uuid(s.client_id),
        "type_sinistre": s.type_sinistre,
        "date_sinistre": _dt(s.date_sinistre),
        "lieu_sinistre": s.lieu_sinistre,
        "description": s.description,
        "cci_score": s.cci_score,
        "status_dossier": s.status_dossier,
        "type_traitement": s.type_traitement,
        "tiers_implique": s.tiers_implique,
        "tiers_nom": s.tiers_nom,
        "tiers_responsable_incertain": s.tiers_responsable_incertain,
        "documents_complets": s.documents_complets,
        "date_creation": _dt(s.date_creation),
        "date_modification": _dt(s.date_modification),
        "client": {
            "id": _uuid(client.id),
            "matricule": client.matricule,
            "nom": client.nom,
            "prenom": client.prenom,
            "telephone": client.telephone,
            "email": client.email,
        } if client else None
    }


def _contrat_to_dict(c: ContratDB, client: Optional[ClientDB] = None):
    return {
        "id": _uuid(c.id),
        "client_id": _uuid(c.client_id),
        "numero_contrat": c.numero_contrat,
        "type_assurance": c.type_assurance,
        "date_debut": _dt(c.date_debut),
        "date_fin": _dt(c.date_fin),
        "statut": c.statut,
        "garantie_collision": c.garantie_collision,
        "garantie_vol": c.garantie_vol,
        "garantie_incendie": c.garantie_incendie,
        "garantie_responsabilite": c.garantie_responsabilite,
        "garantie_assistance": c.garantie_assistance,
        "franchise_collision": float(c.franchise_collision or 0),
        "franchise_vol": float(c.franchise_vol or 0),
        "franchise_incendie": float(c.franchise_incendie or 0),
        "limite_responsabilite": float(c.limite_responsabilite or 0),
        "limite_collision": float(c.limite_collision or 0),
        "limite_vol": float(c.limite_vol or 0),
        "date_creation": _dt(c.date_creation),
        "date_modification": _dt(c.date_modification),
        "client": {
            "id": _uuid(client.id),
            "matricule": client.matricule,
            "nom": client.nom,
            "prenom": client.prenom,
            "telephone": client.telephone,
            "email": client.email,
        } if client else None
    }


def _remboursement_to_dict(r: RemboursementDB, sinistre: Optional[SinistreDB] = None, client: Optional[ClientDB] = None):
    return {
        "id": _uuid(r.id),
        "sinistre_id": _uuid(r.sinistre_id),
        "montant_reclame": float(r.montant_reclame or 0),
        "montant_accepte": float(r.montant_accepte or 0) if r.montant_accepte is not None else None,
        "franchise": float(r.franchise or 0) if r.franchise is not None else None,
        "montant_net": float(r.montant_net or 0) if r.montant_net is not None else None,
        "status": r.status,
        "motif_rejet": r.motif_rejet,
        "date_paiement": _dt(r.date_paiement),
        "reference_paiement": r.reference_paiement,
        "date_creation": _dt(r.date_creation),
        "date_modification": _dt(r.date_modification),
        "sinistre": _sinistre_to_dict(sinistre, client) if sinistre else None
    }


def _escalade_to_dict(e: EscaladeDB, sinistre: Optional[SinistreDB] = None, client: Optional[ClientDB] = None, conseiller: Optional[ConseillerDB] = None):
    return {
        "id": _uuid(e.id),
        "sinistre_id": _uuid(e.sinistre_id),
        "conseiller_id": _uuid(e.conseiller_id),
        "raison_escalade": e.raison_escalade,
        "cci_score_trigger": e.cci_score_trigger,
        "status": e.status,
        "date_escalade": _dt(e.date_escalade),
        "date_transfert": _dt(e.date_transfert),
        "date_completion": _dt(e.date_completion),
        "sinistre": _sinistre_to_dict(sinistre, client) if sinistre else None,
        "conseiller": {
            "id": _uuid(conseiller.id),
            "nom": conseiller.nom,
            "prenom": conseiller.prenom,
            "email": conseiller.email,
            "statut": conseiller.statut
        } if conseiller else None
    }


# =========================
# SINISTRES CRUD
# =========================
@router.get("/sinistres")
async def list_sinistres(skip: int = 0, limit: int = 200, db: Session = Depends(get_db)):
    sinistres = db.query(SinistreDB).order_by(SinistreDB.date_creation.desc()).offset(skip).limit(limit).all()
    results = []
    for s in sinistres:
        client = db.query(ClientDB).filter(ClientDB.id == s.client_id).first()
        results.append(_sinistre_to_dict(s, client))
    return results


@router.get("/sinistres/{sinistre_id}")
async def get_sinistre(sinistre_id: UUID, db: Session = Depends(get_db)):
    sinistre = db.query(SinistreDB).filter(SinistreDB.id == sinistre_id).first()
    if not sinistre:
        raise HTTPException(status_code=404, detail="Sinistre non trouvé")
    client = db.query(ClientDB).filter(ClientDB.id == sinistre.client_id).first()
    return _sinistre_to_dict(sinistre, client)


@router.post("/sinistres")
async def create_sinistre(payload: dict, db: Session = Depends(get_db)):
    client_id = payload.get("client_id")
    if not client_id:
        raise HTTPException(status_code=400, detail="client_id requis")

    client = db.query(ClientDB).filter(ClientDB.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")

    numero_sinistre = payload.get("numero_sinistre") or f"SINS-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
    date_sinistre = payload.get("date_sinistre") or datetime.utcnow().date().isoformat()

    sinistre = SinistreDB(
        client_id=client.id,
        numero_sinistre=numero_sinistre,
        type_sinistre=payload.get("type_sinistre", "collision"),
        date_sinistre=datetime.fromisoformat(date_sinistre).date(),
        lieu_sinistre=payload.get("lieu_sinistre"),
        description=payload.get("description", ""),
        cci_score=int(payload.get("cci_score", 0) or 0),
        status_dossier=payload.get("status_dossier", "nouveau"),
        type_traitement=payload.get("type_traitement", "autonome"),
        tiers_implique=bool(payload.get("tiers_implique", False)),
        tiers_nom=payload.get("tiers_nom"),
        tiers_responsable_incertain=bool(payload.get("tiers_responsable_incertain", False)),
        documents_complets=bool(payload.get("documents_complets", False))
    )
    db.add(sinistre)
    db.commit()
    db.refresh(sinistre)
    return _sinistre_to_dict(sinistre, client)


@router.put("/sinistres/{sinistre_id}")
async def update_sinistre(sinistre_id: UUID, payload: dict, db: Session = Depends(get_db)):
    sinistre = db.query(SinistreDB).filter(SinistreDB.id == sinistre_id).first()
    if not sinistre:
        raise HTTPException(status_code=404, detail="Sinistre non trouvé")

    for field in [
        "type_sinistre", "lieu_sinistre", "description", "cci_score", "status_dossier",
        "type_traitement", "tiers_implique", "tiers_nom", "tiers_responsable_incertain",
        "documents_complets"
    ]:
        if field in payload:
            setattr(sinistre, field, payload.get(field))

    if "date_sinistre" in payload and payload.get("date_sinistre"):
        sinistre.date_sinistre = datetime.fromisoformat(payload.get("date_sinistre")).date()

    db.commit()
    db.refresh(sinistre)
    client = db.query(ClientDB).filter(ClientDB.id == sinistre.client_id).first()
    return _sinistre_to_dict(sinistre, client)


@router.delete("/sinistres/{sinistre_id}")
async def delete_sinistre(sinistre_id: UUID, db: Session = Depends(get_db)):
    sinistre = db.query(SinistreDB).filter(SinistreDB.id == sinistre_id).first()
    if not sinistre:
        raise HTTPException(status_code=404, detail="Sinistre non trouvé")
    db.delete(sinistre)
    db.commit()
    return {"message": "Sinistre supprimé"}


# =========================
# CONTRATS CRUD
# =========================
@router.get("/contrats")
async def list_contrats(skip: int = 0, limit: int = 200, db: Session = Depends(get_db)):
    contrats = db.query(ContratDB).order_by(ContratDB.date_creation.desc()).offset(skip).limit(limit).all()
    results = []
    for c in contrats:
        client = db.query(ClientDB).filter(ClientDB.id == c.client_id).first()
        results.append(_contrat_to_dict(c, client))
    return results


@router.post("/contrats")
async def create_contrat(payload: dict, db: Session = Depends(get_db)):
    client_id = payload.get("client_id")
    if not client_id:
        raise HTTPException(status_code=400, detail="client_id requis")

    client = db.query(ClientDB).filter(ClientDB.id == client_id).first()
    if not client:
        raise HTTPException(status_code=404, detail="Client non trouvé")

    contrat = ContratDB(
        client_id=client.id,
        numero_contrat=payload.get("numero_contrat"),
        type_assurance=payload.get("type_assurance", "auto"),
        date_debut=datetime.fromisoformat(payload.get("date_debut")).date() if payload.get("date_debut") else datetime.utcnow().date(),
        date_fin=datetime.fromisoformat(payload.get("date_fin")).date() if payload.get("date_fin") else None,
        statut=payload.get("statut", "actif"),
        garantie_collision=bool(payload.get("garantie_collision", False)),
        garantie_vol=bool(payload.get("garantie_vol", False)),
        garantie_incendie=bool(payload.get("garantie_incendie", False)),
        garantie_responsabilite=bool(payload.get("garantie_responsabilite", True)),
        garantie_assistance=bool(payload.get("garantie_assistance", True)),
        franchise_collision=payload.get("franchise_collision", 500),
        franchise_vol=payload.get("franchise_vol", 500),
        franchise_incendie=payload.get("franchise_incendie", 500),
        limite_responsabilite=payload.get("limite_responsabilite", 50000),
        limite_collision=payload.get("limite_collision", 50000),
        limite_vol=payload.get("limite_vol", 50000)
    )
    db.add(contrat)
    db.commit()
    db.refresh(contrat)
    return _contrat_to_dict(contrat, client)


@router.put("/contrats/{contrat_id}")
async def update_contrat(contrat_id: UUID, payload: dict, db: Session = Depends(get_db)):
    contrat = db.query(ContratDB).filter(ContratDB.id == contrat_id).first()
    if not contrat:
        raise HTTPException(status_code=404, detail="Contrat non trouvé")

    for field in [
        "numero_contrat", "type_assurance", "statut",
        "garantie_collision", "garantie_vol", "garantie_incendie",
        "garantie_responsabilite", "garantie_assistance",
        "franchise_collision", "franchise_vol", "franchise_incendie",
        "limite_responsabilite", "limite_collision", "limite_vol"
    ]:
        if field in payload:
            setattr(contrat, field, payload.get(field))

    if "date_debut" in payload and payload.get("date_debut"):
        contrat.date_debut = datetime.fromisoformat(payload.get("date_debut")).date()
    if "date_fin" in payload and payload.get("date_fin"):
        contrat.date_fin = datetime.fromisoformat(payload.get("date_fin")).date()

    db.commit()
    db.refresh(contrat)
    client = db.query(ClientDB).filter(ClientDB.id == contrat.client_id).first()
    return _contrat_to_dict(contrat, client)


@router.delete("/contrats/{contrat_id}")
async def delete_contrat(contrat_id: UUID, db: Session = Depends(get_db)):
    contrat = db.query(ContratDB).filter(ContratDB.id == contrat_id).first()
    if not contrat:
        raise HTTPException(status_code=404, detail="Contrat non trouvé")
    db.delete(contrat)
    db.commit()
    return {"message": "Contrat supprimé"}


# =========================
# REMBOURSEMENTS CRUD
# =========================
@router.get("/remboursements")
async def list_remboursements(skip: int = 0, limit: int = 200, db: Session = Depends(get_db)):
    remboursements = db.query(RemboursementDB).order_by(RemboursementDB.date_creation.desc()).offset(skip).limit(limit).all()
    results = []
    for r in remboursements:
        sinistre = db.query(SinistreDB).filter(SinistreDB.id == r.sinistre_id).first()
        client = db.query(ClientDB).filter(ClientDB.id == sinistre.client_id).first() if sinistre else None
        results.append(_remboursement_to_dict(r, sinistre, client))
    return results


@router.post("/remboursements")
async def create_remboursement(payload: dict, db: Session = Depends(get_db)):
    sinistre_id = payload.get("sinistre_id")
    if not sinistre_id:
        raise HTTPException(status_code=400, detail="sinistre_id requis")

    sinistre = db.query(SinistreDB).filter(SinistreDB.id == sinistre_id).first()
    if not sinistre:
        raise HTTPException(status_code=404, detail="Sinistre non trouvé")

    remboursement = RemboursementDB(
        sinistre_id=sinistre.id,
        montant_reclame=payload.get("montant_reclame", 0),
        montant_accepte=payload.get("montant_accepte"),
        franchise=payload.get("franchise"),
        montant_net=payload.get("montant_net"),
        status=payload.get("status", "en_attente"),
        motif_rejet=payload.get("motif_rejet"),
        date_paiement=datetime.fromisoformat(payload.get("date_paiement")).date() if payload.get("date_paiement") else None,
        reference_paiement=payload.get("reference_paiement")
    )
    db.add(remboursement)
    db.commit()
    db.refresh(remboursement)
    client = db.query(ClientDB).filter(ClientDB.id == sinistre.client_id).first()
    return _remboursement_to_dict(remboursement, sinistre, client)


@router.put("/remboursements/{remboursement_id}")
async def update_remboursement(remboursement_id: UUID, payload: dict, db: Session = Depends(get_db)):
    remboursement = db.query(RemboursementDB).filter(RemboursementDB.id == remboursement_id).first()
    if not remboursement:
        raise HTTPException(status_code=404, detail="Remboursement non trouvé")

    for field in [
        "montant_reclame", "montant_accepte", "franchise", "montant_net",
        "status", "motif_rejet", "reference_paiement"
    ]:
        if field in payload:
            setattr(remboursement, field, payload.get(field))

    if "date_paiement" in payload and payload.get("date_paiement"):
        remboursement.date_paiement = datetime.fromisoformat(payload.get("date_paiement")).date()

    db.commit()
    db.refresh(remboursement)
    sinistre = db.query(SinistreDB).filter(SinistreDB.id == remboursement.sinistre_id).first()
    client = db.query(ClientDB).filter(ClientDB.id == sinistre.client_id).first() if sinistre else None
    return _remboursement_to_dict(remboursement, sinistre, client)


@router.delete("/remboursements/{remboursement_id}")
async def delete_remboursement(remboursement_id: UUID, db: Session = Depends(get_db)):
    remboursement = db.query(RemboursementDB).filter(RemboursementDB.id == remboursement_id).first()
    if not remboursement:
        raise HTTPException(status_code=404, detail="Remboursement non trouvé")
    db.delete(remboursement)
    db.commit()
    return {"message": "Remboursement supprimé"}


# =========================
# ESCALADES CRUD
# =========================
@router.get("/escalades")
async def list_escalades(skip: int = 0, limit: int = 200, db: Session = Depends(get_db)):
    escalades = db.query(EscaladeDB).order_by(EscaladeDB.date_escalade.desc()).offset(skip).limit(limit).all()
    results = []
    for e in escalades:
        sinistre = db.query(SinistreDB).filter(SinistreDB.id == e.sinistre_id).first()
        client = db.query(ClientDB).filter(ClientDB.id == sinistre.client_id).first() if sinistre else None
        conseiller = db.query(ConseillerDB).filter(ConseillerDB.id == e.conseiller_id).first() if e.conseiller_id else None
        results.append(_escalade_to_dict(e, sinistre, client, conseiller))
    return results


@router.post("/escalades")
async def create_escalade(payload: dict, db: Session = Depends(get_db)):
    sinistre_id = payload.get("sinistre_id")
    if not sinistre_id:
        raise HTTPException(status_code=400, detail="sinistre_id requis")

    sinistre = db.query(SinistreDB).filter(SinistreDB.id == sinistre_id).first()
    if not sinistre:
        raise HTTPException(status_code=404, detail="Sinistre non trouvé")

    escalade = EscaladeDB(
        sinistre_id=sinistre.id,
        conseiller_id=payload.get("conseiller_id"),
        raison_escalade=payload.get("raison_escalade", "CCI élevé"),
        cci_score_trigger=payload.get("cci_score_trigger"),
        status=payload.get("status", "en_attente"),
        date_escalade=datetime.utcnow()
    )
    db.add(escalade)
    db.commit()
    db.refresh(escalade)
    client = db.query(ClientDB).filter(ClientDB.id == sinistre.client_id).first()
    conseiller = db.query(ConseillerDB).filter(ConseillerDB.id == escalade.conseiller_id).first() if escalade.conseiller_id else None
    return _escalade_to_dict(escalade, sinistre, client, conseiller)


@router.put("/escalades/{escalade_id}")
async def update_escalade(escalade_id: UUID, payload: dict, db: Session = Depends(get_db)):
    escalade = db.query(EscaladeDB).filter(EscaladeDB.id == escalade_id).first()
    if not escalade:
        raise HTTPException(status_code=404, detail="Escalade non trouvée")

    for field in ["conseiller_id", "raison_escalade", "cci_score_trigger", "status"]:
        if field in payload:
            setattr(escalade, field, payload.get(field))

    if "date_transfert" in payload and payload.get("date_transfert"):
        escalade.date_transfert = datetime.fromisoformat(payload.get("date_transfert"))
    if "date_completion" in payload and payload.get("date_completion"):
        escalade.date_completion = datetime.fromisoformat(payload.get("date_completion"))

    db.commit()
    db.refresh(escalade)
    sinistre = db.query(SinistreDB).filter(SinistreDB.id == escalade.sinistre_id).first()
    client = db.query(ClientDB).filter(ClientDB.id == sinistre.client_id).first() if sinistre else None
    conseiller = db.query(ConseillerDB).filter(ConseillerDB.id == escalade.conseiller_id).first() if escalade.conseiller_id else None
    return _escalade_to_dict(escalade, sinistre, client, conseiller)


@router.delete("/escalades/{escalade_id}")
async def delete_escalade(escalade_id: UUID, db: Session = Depends(get_db)):
    escalade = db.query(EscaladeDB).filter(EscaladeDB.id == escalade_id).first()
    if not escalade:
        raise HTTPException(status_code=404, detail="Escalade non trouvée")
    db.delete(escalade)
    db.commit()
    return {"message": "Escalade supprimée"}


# =========================
# ANALYTICS OVERVIEW
# =========================
@router.get("/analytics/overview")
async def analytics_overview(db: Session = Depends(get_db)):
    clients_total = db.query(func.count(ClientDB.id)).scalar() or 0
    sinistres_total = db.query(func.count(SinistreDB.id)).scalar() or 0
    escalades_total = db.query(func.count(EscaladeDB.id)).scalar() or 0
    remboursements_total = db.query(func.count(RemboursementDB.id)).scalar() or 0

    cci_avg = db.query(func.avg(SinistreDB.cci_score)).scalar() or 0
    cci_min = db.query(func.min(SinistreDB.cci_score)).scalar() or 0
    cci_max = db.query(func.max(SinistreDB.cci_score)).scalar() or 0

    # Sinistres by status
    sinistres_by_status = db.query(SinistreDB.status_dossier, func.count(SinistreDB.id)).group_by(SinistreDB.status_dossier).all()
    sinistres_by_type = db.query(SinistreDB.type_sinistre, func.count(SinistreDB.id)).group_by(SinistreDB.type_sinistre).all()

    # Escalades by status
    escalades_by_status = db.query(EscaladeDB.status, func.count(EscaladeDB.id)).group_by(EscaladeDB.status).all()

    # Remboursements by status
    remboursements_by_status = db.query(RemboursementDB.status, func.count(RemboursementDB.id)).group_by(RemboursementDB.status).all()
    remb_sum_reclame = db.query(func.sum(RemboursementDB.montant_reclame)).scalar() or 0
    remb_sum_accepte = db.query(func.sum(RemboursementDB.montant_accepte)).scalar() or 0
    remb_sum_net = db.query(func.sum(RemboursementDB.montant_net)).scalar() or 0

    # Sinistres by day (last 14 days)
    last_days = db.query(func.date(SinistreDB.date_creation), func.count(SinistreDB.id))\
        .group_by(func.date(SinistreDB.date_creation))\
        .order_by(func.date(SinistreDB.date_creation).desc())\
        .limit(14).all()
    sinistres_by_day = [
        {"date": str(day[0]), "count": day[1]} for day in reversed(last_days)
    ]

    # CCI buckets
    cci_values = [row[0] for row in db.query(SinistreDB.cci_score).all() if row[0] is not None]
    buckets = {"0-20": 0, "21-40": 0, "41-60": 0, "61-80": 0, "81-100": 0}
    for value in cci_values:
        if value <= 20:
            buckets["0-20"] += 1
        elif value <= 40:
            buckets["21-40"] += 1
        elif value <= 60:
            buckets["41-60"] += 1
        elif value <= 80:
            buckets["61-80"] += 1
        else:
            buckets["81-100"] += 1

    # Cognitive insights for recent sinistres
    recent_sinistres = db.query(SinistreDB).order_by(SinistreDB.date_creation.desc()).limit(8).all()
    cognitive_cards = []
    for s in recent_sinistres:
        client = db.query(ClientDB).filter(ClientDB.id == s.client_id).first()
        facts = 0
        facts += 1 if s.lieu_sinistre else 0
        facts += 1 if s.date_sinistre else 0
        facts += 1 if s.tiers_implique is not None else 0
        facts += 1 if s.documents_complets is not None else 0
        facts += 1 if s.description else 0

        propositions = 0
        if s.description:
            propositions = max(1, len([seg for seg in s.description.replace("?", ".").replace("!", ".").split(".") if seg.strip()]))

        confidence = min(98, 60 + (facts * 6) + (s.cci_score or 0) // 5)

        cognitive_cards.append({
            "sinistre_id": _uuid(s.id),
            "numero_sinistre": s.numero_sinistre,
            "client": f"{client.nom} {client.prenom}" if client else "",
            "facts": facts,
            "propositions": propositions,
            "ambiguities": 0,
            "contradictions": 0,
            "confidence": confidence,
            "cci_score": s.cci_score or 0,
            "status": s.status_dossier,
            "type": s.type_sinistre,
            "date": _dt(s.date_creation)
        })

    return {
        "kpis": {
            "clients_total": clients_total,
            "sinistres_total": sinistres_total,
            "escalades_total": escalades_total,
            "remboursements_total": remboursements_total,
            "cci_avg": round(float(cci_avg), 2),
            "cci_min": int(cci_min),
            "cci_max": int(cci_max)
        },
        "sinistres_by_status": [{"name": s[0], "value": s[1]} for s in sinistres_by_status],
        "sinistres_by_type": [{"name": s[0], "value": s[1]} for s in sinistres_by_type],
        "sinistres_by_day": sinistres_by_day,
        "cci_buckets": [{"range": k, "value": v} for k, v in buckets.items()],
        "escalades_by_status": [{"name": s[0], "value": s[1]} for s in escalades_by_status],
        "remboursements_by_status": [{"name": s[0], "value": s[1]} for s in remboursements_by_status],
        "remboursements_sum": {
            "reclame": float(remb_sum_reclame),
            "accepte": float(remb_sum_accepte or 0),
            "net": float(remb_sum_net or 0)
        },
        "cognitive_cards": cognitive_cards
    }
