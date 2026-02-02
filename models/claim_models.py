"""
Modèles de données Pydantic CRM Production.
Digital Twin complet d'un sinistre avec gestion client, contrat, remboursement.
"""

from pydantic import BaseModel, EmailStr, Field
from typing import Optional, List, Dict, Any
from datetime import datetime
from enum import Enum
import uuid

# ==================== ENUMS ====================

class CiviliteEnum(str, Enum):
    M = "Monsieur"
    MME = "Madame"
    MLLE = "Mademoiselle"

class TypeSinistreEnum(str, Enum):
    COLLISION = "collision"
    VOL = "vol"
    INCENDIE = "incendie"
    DEGATS = "dégâts"
    BLESSURE = "blessure"
    DOMMAGE_MATERIEL = "dommage_materiel"

class StatusDossierEnum(str, Enum):
    NOUVEAU = "nouveau"
    EN_COURS = "en_cours"
    EXPERT = "expert"
    VALIDATION = "validation"
    ESCALADE = "escalade"
    EN_ATTENTE_CLIENT = "en_attente_client"
    FERME = "fermé"

class TypeTraitementEnum(str, Enum):
    AUTONOME = "autonome"
    ESCALADE = "escalade"
    EXPERT = "expert"

class StatusRemboursementEnum(str, Enum):
    EN_ATTENTE = "en_attente"
    ACCEPTE = "accepté"
    PAYE = "payé"
    REJETE = "rejeté"

class ConversationPhaseEnum(str, Enum):
    AUTHENTIFICATION = "authentification"
    DESCRIPTION = "description"
    SINISTRE_DETAILS = "sinistre_details"
    CONSTAT = "constat"
    DOCUMENTS = "documents"
    DECISION = "decision"
    TRANSFERT = "transfert"
    SUIVI = "suivi"

# ==================== MODELS ====================

# --- CLIENT ---
class ClientBase(BaseModel):
    matricule: str = Field(..., min_length=5, max_length=20, description="Matricule unique assuré")
    civilite: Optional[CiviliteEnum] = None
    nom: str = Field(..., min_length=2, max_length=100)
    prenom: str = Field(..., min_length=2, max_length=100)
    date_naissance: Optional[datetime] = None
    email: Optional[EmailStr] = None
    telephone: Optional[str] = Field(None, max_length=20)
    adresse: Optional[str] = None
    code_postal: Optional[str] = Field(None, max_length=10)
    ville: Optional[str] = None

class ClientCreate(ClientBase):
    pass

class ClientUpdate(BaseModel):
    civilite: Optional[CiviliteEnum] = None
    nom: Optional[str] = None
    prenom: Optional[str] = None
    email: Optional[EmailStr] = None
    telephone: Optional[str] = None
    adresse: Optional[str] = None
    code_postal: Optional[str] = None
    ville: Optional[str] = None

class Client(ClientBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    date_creation: datetime
    statut: str = "actif"

    class Config:
        from_attributes = True

# --- CONTRAT ---
class ContratBase(BaseModel):
    numero_contrat: str
    type_contrat: str = Field(..., description="auto, habitation, etc")
    date_souscription: datetime
    date_expiration: datetime
    statut: str = "actif"
    garanties: List[str] = []
    franchise_tiers: float = 0
    franchise_tiers_collision: float = 0
    couverture_dommage_materiel: bool = True
    couverture_tiers: bool = True
    couverture_rc_civile: bool = True

class Contrat(ContratBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    client_id: str
    date_creation: datetime

    class Config:
        from_attributes = True

# --- SINISTRE (DOSSIER) ---
class SinistreBase(BaseModel):
    client_id: str
    contrat_id: str
    date_sinistre: datetime
    type_sinistre: TypeSinistreEnum
    description: str
    lieu: Optional[str] = None
    tiers_implique: bool = False
    nom_tiers: Optional[str] = None
    contact_tiers: Optional[str] = None
    tiers_responsable: Optional[bool] = None
    constat_amiable: bool = False
    numero_constat: Optional[str] = None
    police_intervenue: bool = False
    numero_proces_verbal: Optional[str] = None
    estimation_dommage: Optional[float] = None
    photo_urls: List[str] = []

class SinistreCreate(SinistreBase):
    pass

class SinistreUpdate(BaseModel):
    description: Optional[str] = None
    type_sinistre: Optional[TypeSinistreEnum] = None
    tiers_implique: Optional[bool] = None
    constat_amiable: Optional[bool] = None
    police_intervenue: Optional[bool] = None
    estimation_dommage: Optional[float] = None
    photo_urls: Optional[List[str]] = None
    cci_score: Optional[int] = None
    status_dossier: Optional[StatusDossierEnum] = None
    type_traitement: Optional[TypeTraitementEnum] = None

class Sinistre(SinistreBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    numero_sinistre: str
    cci_score: int = 0
    status_dossier: StatusDossierEnum = StatusDossierEnum.NOUVEAU
    type_traitement: Optional[TypeTraitementEnum] = None
    conseiller_affecte_id: Optional[str] = None
    date_creation: datetime
    date_modification: datetime
    date_fermeture: Optional[datetime] = None

    class Config:
        from_attributes = True

# --- HISTORIQUE CONVERSATION ---
class MessageConversation(BaseModel):
    sinistre_id: str
    role: str = Field(..., description="bot, user, system")
    texte: str
    texte_stt: Optional[str] = None
    confiance_stt: Optional[float] = Field(None, ge=0, le=1)
    audio_url: Optional[str] = None
    timestamp: datetime = Field(default_factory=datetime.utcnow)
    metadata: Optional[Dict[str, Any]] = None

class HistoriqueConversation(MessageConversation):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))

    class Config:
        from_attributes = True

# --- REMBOURSEMENT ---
class RemboursementBase(BaseModel):
    sinistre_id: str
    montant_reclame: float
    franchise_appliquee: float = 0
    montant_accepte: Optional[float] = None
    motif_rejet: Optional[str] = None
    moyen_paiement: Optional[str] = None

class RemboursementCreate(RemboursementBase):
    pass

class RemboursementUpdate(BaseModel):
    montant_accepte: Optional[float] = None
    montant_reclame: Optional[float] = None
    statut: Optional[StatusRemboursementEnum] = None
    date_paiement: Optional[datetime] = None

class Remboursement(RemboursementBase):
    id: str = Field(default_factory=lambda: str(uuid.uuid4()))
    statut: StatusRemboursementEnum = StatusRemboursementEnum.EN_ATTENTE
    date_acceptation: Optional[datetime] = None
    date_paiement: Optional[datetime] = None
    date_creation: datetime

    class Config:
        from_attributes = True


# --- TRANSCRIPTION METADATA ---
class TranscriptMetadata(BaseModel):
    original_transcript: str
    normalized_transcript: Optional[str] = None
    language: Optional[str] = None
    confidence_score: Optional[float] = None
    emotional_markers: Optional[List[str]] = None
    hesitations: Optional[int] = None
    duration_seconds: Optional[float] = None

# --- CONTEXTE CONVERSATION ---
class ContexteConversation(BaseModel):
    sinistre_id: str
    client_id: str
    phase_actuelle: ConversationPhaseEnum = ConversationPhaseEnum.AUTHENTIFICATION
    data_collectee: Dict[str, Any] = {}
    messages: List[MessageConversation] = []
    cci_score: int = 0
    decision: Optional[TypeTraitementEnum] = None
    timestamp_debut: datetime = Field(default_factory=datetime.utcnow)

# --- SUIVI DOSSIER (CLIENT VIEW) ---
class ActionDossier(BaseModel):
    id: str
    type_action: str
    description: str
    priorite: str
    statut: str
    date: datetime

class SuiviDossierClient(BaseModel):
    numero_sinistre: str
    date_sinistre: datetime
    status_dossier: StatusDossierEnum
    description_breve: str
    type_sinistre: TypeSinistreEnum
    actions_en_cours: List[ActionDossier] = []
    remboursement: Optional[Remboursement] = None
    dernier_message: Optional[str] = None
    dernier_contact: Optional[datetime] = None

# --- ESCALADE ---
class EscaladeRequest(BaseModel):
    sinistre_id: str
    raison: str
    cci_score: int
    messages_context: List[MessageConversation] = []

class EscaladeResponse(BaseModel):
    escalade_id: str
    sinistre_id: str
    timestamp: datetime
    status: str = "en_attente"
    conseiller_assigne: Optional[str] = None
    message_client: str = "Je vais vous transférer vers un conseiller spécialisé..."
