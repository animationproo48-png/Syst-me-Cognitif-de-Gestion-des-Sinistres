# backend/schemas/schemas.py

from pydantic import BaseModel, EmailStr, Field, ConfigDict
from datetime import datetime, date, time
from typing import Optional, List
from decimal import Decimal
from enum import Enum
import uuid


# ============================================================
# ENUMS
# ============================================================
class StatusDossierEnum(str, Enum):
    NOUVEAU = "nouveau"
    EN_COURS = "en_cours"
    EXPERT = "expert"
    VALIDATION = "validation"
    ESCALADE = "escalade"
    EN_ATTENTE_CLIENT = "en_attente_client"
    FERMÉ = "fermé"


class TypeTraitementEnum(str, Enum):
    AUTONOME = "autonome"
    ESCALADE = "escalade"
    EXPERT = "expert"


class TypeSinistreEnum(str, Enum):
    COLLISION = "collision"
    VOL = "vol"
    INCENDIE = "incendie"
    DÉGÂTS = "dégâts"
    BLESSURE = "blessure"
    AUTRE = "autre"


class StatusRemboursementEnum(str, Enum):
    EN_ATTENTE = "en_attente"
    ACCEPTÉ = "accepté"
    PAYÉ = "payé"
    REJETÉ = "rejeté"


# ============================================================
# CLIENT SCHEMAS
# ============================================================
class ClientBase(BaseModel):
    matricule: str
    nom: str
    prenom: str
    email: EmailStr
    telephone: str
    civilite: Optional[str] = None
    date_naissance: Optional[date] = None
    adresse: Optional[str] = None
    ville: Optional[str] = None
    code_postal: Optional[str] = None


class ClientCreate(ClientBase):
    pass


class ClientUpdate(BaseModel):
    nom: Optional[str] = None
    email: Optional[EmailStr] = None
    telephone: Optional[str] = None
    adresse: Optional[str] = None


class ClientResponse(ClientBase):
    id: uuid.UUID
    statut: str
    date_creation: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# CONTRAT SCHEMAS
# ============================================================
class ContratBase(BaseModel):
    numero_contrat: str
    type_assurance: str
    date_debut: date
    date_fin: Optional[date] = None
    garantie_collision: bool = False
    garantie_vol: bool = False
    garantie_incendie: bool = False
    garantie_responsabilite: bool = True
    garantie_assistance: bool = True
    franchise_collision: Decimal = Decimal(500)
    franchise_vol: Decimal = Decimal(500)
    franchise_incendie: Decimal = Decimal(500)


class ContratResponse(ContratBase):
    id: uuid.UUID
    client_id: uuid.UUID
    statut: str
    date_creation: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# SINISTRE SCHEMAS
# ============================================================
class SinistreBase(BaseModel):
    type_sinistre: TypeSinistreEnum
    date_sinistre: date
    heure_sinistre: Optional[time] = None
    lieu_sinistre: str
    description: str
    tiers_implique: bool = False
    tiers_nom: Optional[str] = None


class SinistreCreate(SinistreBase):
    client_id: uuid.UUID


class SinistreUpdate(BaseModel):
    description: Optional[str] = None
    tiers_implique: Optional[bool] = None
    documents_complets: Optional[bool] = None
    status_dossier: Optional[StatusDossierEnum] = None


class SinistreResponse(SinistreBase):
    id: uuid.UUID
    numero_sinistre: str
    client_id: uuid.UUID
    cci_score: int
    status_dossier: StatusDossierEnum
    type_traitement: TypeTraitementEnum
    date_creation: datetime

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# REMBOURSEMENT SCHEMAS
# ============================================================
class RemboursementBase(BaseModel):
    montant_reclame: Decimal
    franchise: Optional[Decimal] = None


class RemboursementResponse(RemboursementBase):
    id: uuid.UUID
    montant_accepte: Optional[Decimal] = None
    montant_net: Optional[Decimal] = None
    status: StatusRemboursementEnum
    date_paiement: Optional[date] = None

    model_config = ConfigDict(from_attributes=True)


# ============================================================
# SUIVI DOSSIER RESPONSE
# ============================================================
class ActionTimelineItem(BaseModel):
    action: str
    date: Optional[datetime] = None
    status: str
    details: Optional[dict] = None


class SuiviDossierResponse(BaseModel):
    numero_sinistre: str
    type_sinistre: TypeSinistreEnum
    date_declaration: date
    status_dossier: StatusDossierEnum
    timeline_actions: List[ActionTimelineItem]
    remboursement: Optional[RemboursementResponse] = None
    garanties_applicables: List[dict]
    actions_client: List[dict]
    messages_recents: List[dict]


# ============================================================
# CONVERSATION SCHEMAS
# ============================================================
class MessageRequest(BaseModel):
    text: Optional[str] = None
    audio_url: Optional[str] = None
    stt_confidence: Optional[float] = None


class ConversationPhaseResponse(BaseModel):
    phase: str
    message: str
    audio_url: Optional[str] = None
    data: Optional[dict] = None
    next_phase: Optional[str] = None


# ============================================================
# CONSEILLER SCHEMAS
# ============================================================
class ConseillerResponse(BaseModel):
    id: uuid.UUID
    nom: str
    prenom: str
    email: str
    telephone: Optional[str]
    statut: str
    nombre_dossiers_actifs: int
    capacite_max: int

    model_config = ConfigDict(from_attributes=True)
