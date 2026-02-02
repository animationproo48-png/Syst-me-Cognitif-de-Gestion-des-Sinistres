# backend/models/db_models.py

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Numeric, ForeignKey, Text, Date, Time, Index, JSON, func
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from datetime import datetime
import uuid
from database import Base


class ClientDB(Base):
    """Modèle Client"""
    __tablename__ = "clients"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    matricule = Column(String(20), unique=True, nullable=False, index=True)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    telephone = Column(String(20), nullable=False)
    civilite = Column(String(10))
    date_naissance = Column(Date)
    adresse = Column(String(255))
    ville = Column(String(100))
    code_postal = Column(String(10))
    pays = Column(String(100), default="Maroc")
    statut = Column(String(20), default="actif")
    date_creation = Column(DateTime, default=func.now(), index=True)
    date_modification = Column(DateTime, default=func.now(), onupdate=func.now())

    contrats = relationship("ContratDB", back_populates="client", cascade="all, delete-orphan")
    sinistres = relationship("SinistreDB", back_populates="client", cascade="all, delete-orphan")


class ContratDB(Base):
    """Modèle Contrat"""
    __tablename__ = "contrats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    numero_contrat = Column(String(50), unique=True, nullable=False)
    type_assurance = Column(String(50), nullable=False)
    date_debut = Column(Date, nullable=False)
    date_fin = Column(Date)
    statut = Column(String(20), default="actif")

    garantie_collision = Column(Boolean, default=False)
    garantie_vol = Column(Boolean, default=False)
    garantie_incendie = Column(Boolean, default=False)
    garantie_responsabilite = Column(Boolean, default=True)
    garantie_assistance = Column(Boolean, default=True)

    franchise_collision = Column(Numeric(10, 2), default=500)
    franchise_vol = Column(Numeric(10, 2), default=500)
    franchise_incendie = Column(Numeric(10, 2), default=500)

    limite_responsabilite = Column(Numeric(12, 2), default=50000)
    limite_collision = Column(Numeric(12, 2), default=50000)
    limite_vol = Column(Numeric(12, 2), default=50000)

    date_creation = Column(DateTime, default=func.now())
    date_modification = Column(DateTime, default=func.now(), onupdate=func.now())

    client = relationship("ClientDB", back_populates="contrats")


class SinistreDB(Base):
    """Modèle Sinistre"""
    __tablename__ = "sinistres"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False, index=True)
    numero_sinistre = Column(String(50), unique=True, nullable=False, index=True)
    type_sinistre = Column(String(50), nullable=False, index=True)

    date_sinistre = Column(Date, nullable=False)
    heure_sinistre = Column(Time)
    lieu_sinistre = Column(String(255))
    description = Column(Text, nullable=False)

    cci_score = Column(Integer, default=0)
    cci_justification = Column(Text)

    status_dossier = Column(String(30), default="nouveau", index=True)
    type_traitement = Column(String(20), default="autonome")

    tiers_implique = Column(Boolean, default=False)
    tiers_nom = Column(String(100))
    tiers_responsable_incertain = Column(Boolean, default=False)
    responsabilite_assuree = Column(Numeric(3, 1), default=100)

    conseiller_id = Column(UUID(as_uuid=True), ForeignKey("conseillers.id"), index=True)
    date_escalade = Column(DateTime)

    documents_complets = Column(Boolean, default=False)

    date_creation = Column(DateTime, default=func.now(), index=True)
    date_modification = Column(DateTime, default=func.now(), onupdate=func.now())

    client = relationship("ClientDB", back_populates="sinistres")
    historique = relationship("HistoriqueConversationDB", back_populates="sinistre", cascade="all, delete-orphan")
    actions = relationship("ActionRecommandeeDB", back_populates="sinistre", cascade="all, delete-orphan")
    remboursements = relationship("RemboursementDB", back_populates="sinistre", cascade="all, delete-orphan")
    escalades = relationship("EscaladeDB", back_populates="sinistre", cascade="all, delete-orphan")


class HistoriqueConversationDB(Base):
    """Modèle Historique Conversation"""
    __tablename__ = "historique_conversation"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sinistre_id = Column(UUID(as_uuid=True), ForeignKey("sinistres.id"), nullable=False, index=True)
    phase_conversation = Column(String(50), nullable=False)

    message_user = Column(Text)
    stt_confidence = Column(Numeric(3, 2))
    audio_url_user = Column(String(255))

    message_bot = Column(Text)
    audio_url_bot = Column(String(255))

    contexte_json = Column(JSON)

    date_message = Column(DateTime, default=func.now(), index=True)

    sinistre = relationship("SinistreDB", back_populates="historique")


class ActionRecommandeeDB(Base):
    """Modèle Actions Recommandées"""
    __tablename__ = "actions_recommandees"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sinistre_id = Column(UUID(as_uuid=True), ForeignKey("sinistres.id"), nullable=False, index=True)
    action = Column(String(255), nullable=False)
    description = Column(Text)
    date_limite = Column(Date)
    priorite = Column(String(10), default="normal")
    status = Column(String(20), default="en_attente")
    date_creation = Column(DateTime, default=func.now())
    date_completion = Column(DateTime)

    sinistre = relationship("SinistreDB", back_populates="actions")


class RemboursementDB(Base):
    """Modèle Remboursement"""
    __tablename__ = "remboursements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sinistre_id = Column(UUID(as_uuid=True), ForeignKey("sinistres.id"), nullable=False, index=True)

    montant_reclame = Column(Numeric(12, 2), nullable=False)
    montant_accepte = Column(Numeric(12, 2))
    franchise = Column(Numeric(10, 2))
    montant_net = Column(Numeric(12, 2))

    status = Column(String(20), default="en_attente")
    motif_rejet = Column(Text)
    date_paiement = Column(Date)
    reference_paiement = Column(String(100))

    date_creation = Column(DateTime, default=func.now())
    date_modification = Column(DateTime, default=func.now(), onupdate=func.now())

    sinistre = relationship("SinistreDB", back_populates="remboursements")


class ConseillerDB(Base):
    """Modèle Conseiller"""
    __tablename__ = "conseillers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    telephone = Column(String(20))
    statut = Column(String(20), default="disponible", index=True)
    nombre_dossiers_actifs = Column(Integer, default=0)
    capacite_max = Column(Integer, default=5)
    specialites = Column(String(255))
    date_creation = Column(DateTime, default=func.now())
    date_modification = Column(DateTime, default=func.now(), onupdate=func.now())

    escalades = relationship("EscaladeDB", back_populates="conseiller")


class EscaladeDB(Base):
    """Modèle Escalade"""
    __tablename__ = "escalades"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sinistre_id = Column(UUID(as_uuid=True), ForeignKey("sinistres.id"), nullable=False, index=True)
    conseiller_id = Column(UUID(as_uuid=True), ForeignKey("conseillers.id"), index=True)

    raison_escalade = Column(Text, nullable=False)
    cci_score_trigger = Column(Integer)
    details = Column(JSON)

    status = Column(String(20), default="en_attente")

    date_escalade = Column(DateTime, default=func.now())
    date_transfert = Column(DateTime)
    date_completion = Column(DateTime)

    sinistre = relationship("SinistreDB", back_populates="escalades")
    conseiller = relationship("ConseillerDB", back_populates="escalades")
