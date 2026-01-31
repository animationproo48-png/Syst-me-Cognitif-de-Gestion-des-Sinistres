"""
Modèles de données Pydantic pour le système de gestion cognitive des sinistres.
Représente le Digital Twin d'un sinistre dans le CRM.
"""

from pydantic import BaseModel, Field
from typing import List, Optional, Dict, Any
from datetime import datetime
from enum import Enum


class ClaimType(str, Enum):
    """Types de sinistres supportés"""
    AUTO = "automobile"
    HOME = "habitation"
    HEALTH = "santé"
    LIFE = "vie"
    LIABILITY = "responsabilité_civile"
    TRAVEL = "voyage"
    UNKNOWN = "indéterminé"


class ClaimState(str, Enum):
    """États possibles d'un sinistre"""
    RECEIVED = "reçu"
    ANALYZING = "en_analyse"
    PENDING_DOCS = "documents_manquants"
    AUTONOMOUS = "traitement_autonome"
    ESCALATED = "escaladé_conseiller"
    RESOLVED = "résolu"
    REJECTED = "rejeté"


class ComplexityLevel(str, Enum):
    """Niveaux de complexité"""
    SIMPLE = "simple"
    MODERATE = "modéré"
    COMPLEX = "complexe"
    CRITICAL = "critique"


class Party(BaseModel):
    """Représente une partie impliquée dans le sinistre"""
    name: Optional[str] = None
    role: str  # assuré, tiers, témoin, expert, etc.
    contact: Optional[str] = None
    involvement: Optional[str] = None


class Document(BaseModel):
    """Document mentionné ou requis"""
    type: str  # constat, facture, rapport médical, etc.
    status: str  # mentionné, reçu, manquant
    description: Optional[str] = None
    required: bool = True


class AmbiguityFlag(BaseModel):
    """Zones d'ambiguïté ou d'incertitude"""
    category: str  # temporelle, factuelle, contractuelle, émotionnelle
    description: str
    severity: int = Field(ge=1, le=5)  # 1=faible, 5=critique
    impact_on_decision: str


class TranscriptMetadata(BaseModel):
    """Métadonnées de la transcription audio"""
    original_transcript: str
    normalized_transcript: str
    language: str
    confidence_score: float = Field(ge=0.0, le=1.0)
    emotional_markers: List[str] = Field(default_factory=list)
    hesitations: int = 0
    duration_seconds: Optional[float] = None


class ComplexityBreakdown(BaseModel):
    """Décomposition détaillée du score de complexité"""
    guarantees_score: float = 0.0
    third_party_score: float = 0.0
    missing_docs_score: float = 0.0
    ambiguity_score: float = 0.0
    emotional_score: float = 0.0
    inconsistency_score: float = 0.0
    total_score: float = 0.0
    level: ComplexityLevel = ComplexityLevel.SIMPLE
    explanation: str = ""


class CognitiveClaimStructure(BaseModel):
    """Structure cognitive du sinistre extraite de la transcription"""
    claim_type: ClaimType
    claim_type_confidence: float = Field(ge=0.0, le=1.0)
    
    # Éléments factuels
    date_incident: Optional[str] = None
    location: Optional[str] = None
    parties_involved: List[Party] = Field(default_factory=list)
    damages_description: str = ""
    
    # Éléments documentaires
    mentioned_documents: List[Document] = Field(default_factory=list)
    missing_information: List[str] = Field(default_factory=list)
    
    # Analyse cognitive
    facts: List[str] = Field(default_factory=list)
    assumptions: List[str] = Field(default_factory=list)
    ambiguities: List[AmbiguityFlag] = Field(default_factory=list)
    
    # Timeline
    timeline_events: List[Dict[str, str]] = Field(default_factory=list)
    
    # Métadonnées émotionnelles
    emotional_stress_level: int = Field(default=0, ge=0, le=10)
    emotional_keywords: List[str] = Field(default_factory=list)


class InteractionLog(BaseModel):
    """Log d'une interaction avec le système"""
    timestamp: datetime = Field(default_factory=datetime.now)
    interaction_type: str  # audio_input, system_response, escalation, etc.
    content: str
    metadata: Dict[str, Any] = Field(default_factory=dict)


class ClaimDigitalTwin(BaseModel):
    """Le Digital Twin complet d'un sinistre - Cœur du CRM"""
    
    # Identifiants
    claim_id: str
    created_at: datetime = Field(default_factory=datetime.now)
    last_updated: datetime = Field(default_factory=datetime.now)
    
    # État actuel
    current_state: ClaimState = ClaimState.RECEIVED
    
    # Données sources
    transcript_metadata: Optional[TranscriptMetadata] = None
    cognitive_structure: Optional[CognitiveClaimStructure] = None
    
    # Analyse de complexité
    complexity: Optional[ComplexityBreakdown] = None
    
    # Historique et traçabilité
    interaction_history: List[InteractionLog] = Field(default_factory=list)
    state_history: List[Dict[str, Any]] = Field(default_factory=list)
    
    # Décision et escalade
    is_escalated: bool = False
    escalation_reason: Optional[str] = None
    assigned_advisor: Optional[str] = None
    
    # Métadonnées
    confidence_level: float = Field(default=0.0, ge=0.0, le=1.0)
    risk_indicators: List[str] = Field(default_factory=list)
    tags: List[str] = Field(default_factory=list)
    
    def add_interaction(self, interaction_type: str, content: str, metadata: Dict = None):
        """Ajoute une interaction à l'historique"""
        log = InteractionLog(
            interaction_type=interaction_type,
            content=content,
            metadata=metadata or {}
        )
        self.interaction_history.append(log)
        self.last_updated = datetime.now()
    
    def change_state(self, new_state: ClaimState, reason: str = ""):
        """Change l'état du sinistre avec traçabilité"""
        self.state_history.append({
            "timestamp": datetime.now().isoformat(),
            "from_state": self.current_state.value,
            "to_state": new_state.value,
            "reason": reason
        })
        self.current_state = new_state
        self.last_updated = datetime.now()
    
    def escalate(self, reason: str, advisor: str = "Conseiller Expert"):
        """Escalade le sinistre à un conseiller humain"""
        self.is_escalated = True
        self.escalation_reason = reason
        self.assigned_advisor = advisor
        self.change_state(ClaimState.ESCALATED, reason)


class ClientSummary(BaseModel):
    """Résumé pour le client (clair et actionnable)"""
    claim_id: str
    status: str
    next_steps: List[str]
    documents_required: List[str]
    estimated_processing_time: str
    contact_info: str
    message: str


class AdvisorBrief(BaseModel):
    """Brief structuré pour le conseiller (expertise)"""
    claim_id: str
    claim_type: str
    complexity_score: float
    complexity_level: str
    
    # Vue structurée
    structured_facts: List[str]
    unresolved_ambiguities: List[Dict[str, Any]]
    risk_flags: List[str]
    
    # Recommandations
    suggested_actions: List[str]
    priority_level: str
    estimated_effort: str
    
    # Contexte
    emotional_context: str
    client_stress_level: int


class ManagementSummary(BaseModel):
    """Résumé pour le management (KPIs et décision)"""
    claim_id: str
    claim_type: str
    complexity_score: float
    escalation_reason: str
    risk_indicators: List[str]
    processing_status: str
    estimated_cost_impact: str
    requires_attention: bool
