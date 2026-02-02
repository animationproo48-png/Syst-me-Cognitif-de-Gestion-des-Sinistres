# 📋 PLAN D'IMPLÉMENTATION DÉTAILLÉ - CRM PRODUCTION

**Date:** 2 février 2026  
**Durée Estimée:** 12-15 heures (développement complet)  
**Ordre Strict:** Auth → Description → Details → Docs → Decision → Transfer/Suivi

---

## ✅ ÉTAPE 0: PRÉPARATION ENVIRONMENT

### 0.1 Installer PostgreSQL
```bash
# Windows - Chocolatey
choco install postgresql

# Ou télécharger: https://www.postgresql.org/download/windows/
# Installation: Default settings, password: "insurance123"
# Port: 5432 (default)

# Vérifier installation
psql --version
```

### 0.2 Créer Database
```bash
# Connexion en tant que superuser
psql -U postgres

# Dans psql:
CREATE DATABASE insurance_db;
CREATE USER insurance_user WITH PASSWORD 'insurance_pwd_secure';
GRANT ALL PRIVILEGES ON DATABASE insurance_db TO insurance_user;
\q

# Tester connexion
psql -U insurance_user -d insurance_db -h localhost
```

### 0.3 Installer Dépendances Python
```bash
cd "c:\Users\HP\Inssurance Advanced\backend"

pip install --upgrade pip

pip install \
  fastapi==0.104.1 \
  uvicorn==0.24.0 \
  websockets==12.0 \
  sqlalchemy==2.0.23 \
  psycopg2-binary==2.9.9 \
  alembic==1.13.0 \
  pydantic==2.5.0 \
  pydantic-settings==2.1.0 \
  python-multipart==0.0.6 \
  aiofiles==23.2.1 \
  elevenlabs==0.2.23 \
  requests==2.31.0 \
  python-dotenv==1.0.0 \
  pytest==7.4.3 \
  pytest-asyncio==0.23.2 \
  groq==0.4.2

# Vérifier
pip list | grep -E "fastapi|sqlalchemy|psycopg"
```

---

## ✅ ÉTAPE 1: DATABASE SCHEMA

### 1.1 Créer le Schéma PostgreSQL Complet
```sql
-- Exécuter dans psql ou DBeaver

-- ============================================
-- TABLE: clients
-- ============================================
CREATE TABLE clients (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    matricule VARCHAR(20) UNIQUE NOT NULL,
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    telephone VARCHAR(20) NOT NULL,
    civilite VARCHAR(10) CHECK (civilite IN ('M', 'Mme', 'Mlle')),
    date_naissance DATE,
    adresse VARCHAR(255),
    ville VARCHAR(100),
    code_postal VARCHAR(10),
    pays VARCHAR(100) DEFAULT 'Maroc',
    statut VARCHAR(20) DEFAULT 'actif' CHECK (statut IN ('actif', 'suspendu', 'fermé')),
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    notes TEXT
);

CREATE INDEX idx_clients_matricule ON clients(matricule);
CREATE INDEX idx_clients_email ON clients(email);

-- ============================================
-- TABLE: contrats
-- ============================================
CREATE TABLE contrats (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    numero_contrat VARCHAR(50) UNIQUE NOT NULL,
    type_assurance VARCHAR(50) NOT NULL, -- 'auto', 'habitation', 'responsabilite'
    date_debut DATE NOT NULL,
    date_fin DATE,
    statut VARCHAR(20) DEFAULT 'actif' CHECK (statut IN ('actif', 'suspendu', 'fermé')),
    
    -- Garanties (auto example)
    garantie_collision BOOLEAN DEFAULT FALSE,
    garantie_vol BOOLEAN DEFAULT FALSE,
    garantie_incendie BOOLEAN DEFAULT FALSE,
    garantie_responsabilite BOOLEAN DEFAULT TRUE,
    garantie_assistance BOOLEAN DEFAULT TRUE,
    
    -- Franchises
    franchise_collision DECIMAL(10,2) DEFAULT 500,
    franchise_vol DECIMAL(10,2) DEFAULT 500,
    franchise_incendie DECIMAL(10,2) DEFAULT 500,
    
    -- Limites couverture
    limite_responsabilite DECIMAL(12,2) DEFAULT 50000,
    limite_collision DECIMAL(12,2) DEFAULT 50000,
    limite_vol DECIMAL(12,2) DEFAULT 50000,
    
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_contrats_client_id ON contrats(client_id);
CREATE INDEX idx_contrats_statut ON contrats(statut);

-- ============================================
-- TABLE: sinistres
-- ============================================
CREATE TABLE sinistres (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    client_id UUID NOT NULL REFERENCES clients(id) ON DELETE CASCADE,
    numero_sinistre VARCHAR(50) UNIQUE NOT NULL,
    type_sinistre VARCHAR(50) NOT NULL CHECK (type_sinistre IN 
        ('collision', 'vol', 'incendie', 'dégâts', 'blessure', 'autre')),
    
    date_sinistre DATE NOT NULL,
    heure_sinistre TIME,
    lieu_sinistre VARCHAR(255),
    description TEXT NOT NULL,
    
    -- CCI Scoring
    cci_score INTEGER DEFAULT 0,
    cci_justification TEXT,
    
    -- Status
    status_dossier VARCHAR(30) DEFAULT 'nouveau' CHECK (status_dossier IN (
        'nouveau', 'en_cours', 'expert', 'validation', 'escalade', 
        'en_attente_client', 'fermé'
    )),
    
    type_traitement VARCHAR(20) DEFAULT 'autonome' CHECK (type_traitement IN (
        'autonome', 'escalade', 'expert'
    )),
    
    -- Responsabilité
    tiers_implique BOOLEAN DEFAULT FALSE,
    tiers_nom VARCHAR(100),
    tiers_responsable_incertain BOOLEAN DEFAULT FALSE,
    responsabilite_assuree DECIMAL(3,1) DEFAULT 100, -- en %
    
    -- Assignation
    conseiller_id UUID,
    date_escalade TIMESTAMP,
    
    -- Documents
    documents_complets BOOLEAN DEFAULT FALSE,
    
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_sinistres_client_id ON sinistres(client_id);
CREATE INDEX idx_sinistres_status ON sinistres(status_dossier);
CREATE INDEX idx_sinistres_type ON sinistres(type_sinistre);
CREATE INDEX idx_sinistres_conseiller ON sinistres(conseiller_id);

-- ============================================
-- TABLE: historique_conversation
-- ============================================
CREATE TABLE historique_conversation (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sinistre_id UUID NOT NULL REFERENCES sinistres(id) ON DELETE CASCADE,
    phase_conversation VARCHAR(50) NOT NULL CHECK (phase_conversation IN (
        'authentification', 'description', 'sinistre_details', 'documents',
        'decision', 'transfert', 'suivi'
    )),
    
    -- Message user
    message_user TEXT,
    stt_confidence DECIMAL(3,2),
    audio_url_user VARCHAR(255),
    
    -- Réponse bot
    message_bot TEXT,
    audio_url_bot VARCHAR(255),
    
    -- Contexte
    contexte_json JSONB,
    
    date_message TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_historique_sinistre ON historique_conversation(sinistre_id);
CREATE INDEX idx_historique_phase ON historique_conversation(phase_conversation);

-- ============================================
-- TABLE: actions_recommandees
-- ============================================
CREATE TABLE actions_recommandees (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sinistre_id UUID NOT NULL REFERENCES sinistres(id) ON DELETE CASCADE,
    action VARCHAR(255) NOT NULL,
    description TEXT,
    date_limite DATE,
    priorite VARCHAR(10) CHECK (priorite IN ('urgente', 'haute', 'normal', 'basse')),
    status VARCHAR(20) DEFAULT 'en_attente' CHECK (status IN (
        'en_attente', 'en_cours', 'completée', 'expirée'
    )),
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_completion TIMESTAMP
);

CREATE INDEX idx_actions_sinistre ON actions_recommandees(sinistre_id);

-- ============================================
-- TABLE: remboursements
-- ============================================
CREATE TABLE remboursements (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sinistre_id UUID NOT NULL REFERENCES sinistres(id) ON DELETE CASCADE,
    
    montant_reclame DECIMAL(12,2) NOT NULL,
    montant_accepte DECIMAL(12,2),
    franchise DECIMAL(10,2),
    montant_net DECIMAL(12,2),
    
    status VARCHAR(20) DEFAULT 'en_attente' CHECK (status IN (
        'en_attente', 'accepté', 'payé', 'rejeté', 'partiellement_accepté'
    )),
    
    motif_rejet TEXT,
    date_paiement DATE,
    reference_paiement VARCHAR(100),
    
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_remboursements_sinistre ON remboursements(sinistre_id);
CREATE INDEX idx_remboursements_status ON remboursements(status);

-- ============================================
-- TABLE: conseillers
-- ============================================
CREATE TABLE conseillers (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    nom VARCHAR(100) NOT NULL,
    prenom VARCHAR(100) NOT NULL,
    email VARCHAR(120) UNIQUE NOT NULL,
    telephone VARCHAR(20),
    statut VARCHAR(20) DEFAULT 'disponible' CHECK (statut IN (
        'disponible', 'occupe', 'pause', 'hors_ligne'
    )),
    nombre_dossiers_actifs INTEGER DEFAULT 0,
    capacite_max INTEGER DEFAULT 5,
    specialites VARCHAR(255), -- JSON stringifié: ['collision', 'vol', 'incendie']
    date_creation TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_modification TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

CREATE INDEX idx_conseillers_statut ON conseillers(statut);

-- ============================================
-- TABLE: escalades
-- ============================================
CREATE TABLE escalades (
    id UUID PRIMARY KEY DEFAULT gen_random_uuid(),
    sinistre_id UUID NOT NULL REFERENCES sinistres(id) ON DELETE CASCADE,
    conseiller_id UUID REFERENCES conseillers(id),
    
    raison_escalade TEXT NOT NULL,
    cci_score_trigger INTEGER,
    details JSONB,
    
    status VARCHAR(20) DEFAULT 'en_attente' CHECK (status IN (
        'en_attente', 'acceptée', 'en_cours', 'fermée'
    )),
    
    date_escalade TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_transfert TIMESTAMP,
    date_completion TIMESTAMP
);

CREATE INDEX idx_escalades_sinistre ON escalades(sinistre_id);
CREATE INDEX idx_escalades_conseiller ON escalades(conseiller_id);
```

---

## ✅ ÉTAPE 2: MODÈLES SQLAlchemy

### 2.1 Créer `backend/database.py`
```python
# backend/database.py

from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import NullPool
import os
from dotenv import load_dotenv

load_dotenv()

# Configuration PostgreSQL
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "postgresql://insurance_user:insurance_pwd_secure@localhost:5432/insurance_db"
)

print(f"📊 Connexion DB: {DATABASE_URL.split('@')[1]}")

# Engine avec pool optimisé
engine = create_engine(
    DATABASE_URL,
    pool_size=10,
    max_overflow=20,
    pool_pre_ping=True,  # Vérifier connexion avant utilisation
    echo=False  # Mettre True pour debug SQL
)

SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

Base = declarative_base()

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

def init_db():
    """Créer toutes les tables"""
    Base.metadata.create_all(bind=engine)
    print("✅ Tables créées/vérifiées")
```

### 2.2 Créer `backend/models/db_models.py`
```python
# backend/models/db_models.py

from sqlalchemy import Column, String, Integer, Boolean, DateTime, Numeric, ForeignKey, Text, Date, Time, CheckConstraint, Index, JSON
from sqlalchemy.orm import relationship
from sqlalchemy.dialects.postgresql import UUID
from sqlalchemy.sql import func
from datetime import datetime
import uuid
from database import Base

# ============================================================
# CLIENT
# ============================================================
class ClientDB(Base):
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
    date_creation = Column(DateTime, default=func.now())
    date_modification = Column(DateTime, default=func.now(), onupdate=func.now())
    notes = Column(Text)

    # Relations
    contrats = relationship("ContratDB", back_populates="client", cascade="all, delete-orphan")
    sinistres = relationship("SinistreDB", back_populates="client", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<ClientDB {self.matricule} - {self.nom}>"


# ============================================================
# CONTRAT
# ============================================================
class ContratDB(Base):
    __tablename__ = "contrats"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
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

    franchise_collision = Column(Numeric(10,2), default=500)
    franchise_vol = Column(Numeric(10,2), default=500)
    franchise_incendie = Column(Numeric(10,2), default=500)

    limite_responsabilite = Column(Numeric(12,2), default=50000)
    limite_collision = Column(Numeric(12,2), default=50000)
    limite_vol = Column(Numeric(12,2), default=50000)

    date_creation = Column(DateTime, default=func.now())
    date_modification = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relations
    client = relationship("ClientDB", back_populates="contrats")

    def __repr__(self):
        return f"<ContratDB {self.numero_contrat}>"


# ============================================================
# SINISTRE
# ============================================================
class SinistreDB(Base):
    __tablename__ = "sinistres"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    client_id = Column(UUID(as_uuid=True), ForeignKey("clients.id"), nullable=False)
    numero_sinistre = Column(String(50), unique=True, nullable=False)
    type_sinistre = Column(String(50), nullable=False)

    date_sinistre = Column(Date, nullable=False)
    heure_sinistre = Column(Time)
    lieu_sinistre = Column(String(255))
    description = Column(Text, nullable=False)

    cci_score = Column(Integer, default=0)
    cci_justification = Column(Text)

    status_dossier = Column(String(30), default="nouveau")
    type_traitement = Column(String(20), default="autonome")

    tiers_implique = Column(Boolean, default=False)
    tiers_nom = Column(String(100))
    tiers_responsable_incertain = Column(Boolean, default=False)
    responsabilite_assuree = Column(Numeric(3,1), default=100)

    conseiller_id = Column(UUID(as_uuid=True), ForeignKey("conseillers.id"))
    date_escalade = Column(DateTime)

    documents_complets = Column(Boolean, default=False)

    date_creation = Column(DateTime, default=func.now(), index=True)
    date_modification = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relations
    client = relationship("ClientDB", back_populates="sinistres")
    historique = relationship("HistoriqueConversationDB", back_populates="sinistre", cascade="all, delete-orphan")
    actions = relationship("ActionRecommandeeDB", back_populates="sinistre", cascade="all, delete-orphan")
    remboursements = relationship("RemboursementDB", back_populates="sinistre", cascade="all, delete-orphan")
    escalades = relationship("EscaladeDB", back_populates="sinistre", cascade="all, delete-orphan")

    def __repr__(self):
        return f"<SinistreDB {self.numero_sinistre}>"


# ============================================================
# HISTORIQUE CONVERSATION
# ============================================================
class HistoriqueConversationDB(Base):
    __tablename__ = "historique_conversation"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sinistre_id = Column(UUID(as_uuid=True), ForeignKey("sinistres.id"), nullable=False)
    phase_conversation = Column(String(50), nullable=False)

    message_user = Column(Text)
    stt_confidence = Column(Numeric(3,2))
    audio_url_user = Column(String(255))

    message_bot = Column(Text)
    audio_url_bot = Column(String(255))

    contexte_json = Column(JSON)

    date_message = Column(DateTime, default=func.now(), index=True)

    # Relations
    sinistre = relationship("SinistreDB", back_populates="historique")

    def __repr__(self):
        return f"<HistoriqueConversationDB {self.phase_conversation}>"


# ============================================================
# ACTIONS RECOMMANDEES
# ============================================================
class ActionRecommandeeDB(Base):
    __tablename__ = "actions_recommandees"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sinistre_id = Column(UUID(as_uuid=True), ForeignKey("sinistres.id"), nullable=False)
    action = Column(String(255), nullable=False)
    description = Column(Text)
    date_limite = Column(Date)
    priorite = Column(String(10))
    status = Column(String(20), default="en_attente")
    date_creation = Column(DateTime, default=func.now())
    date_completion = Column(DateTime)

    # Relations
    sinistre = relationship("SinistreDB", back_populates="actions")

    def __repr__(self):
        return f"<ActionRecommandeeDB {self.action}>"


# ============================================================
# REMBOURSEMENTS
# ============================================================
class RemboursementDB(Base):
    __tablename__ = "remboursements"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sinistre_id = Column(UUID(as_uuid=True), ForeignKey("sinistres.id"), nullable=False)

    montant_reclame = Column(Numeric(12,2), nullable=False)
    montant_accepte = Column(Numeric(12,2))
    franchise = Column(Numeric(10,2))
    montant_net = Column(Numeric(12,2))

    status = Column(String(20), default="en_attente")
    motif_rejet = Column(Text)
    date_paiement = Column(Date)
    reference_paiement = Column(String(100))

    date_creation = Column(DateTime, default=func.now())
    date_modification = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relations
    sinistre = relationship("SinistreDB", back_populates="remboursements")

    def __repr__(self):
        return f"<RemboursementDB {self.montant_reclame}€>"


# ============================================================
# CONSEILLERS
# ============================================================
class ConseillerDB(Base):
    __tablename__ = "conseillers"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    nom = Column(String(100), nullable=False)
    prenom = Column(String(100), nullable=False)
    email = Column(String(120), unique=True, nullable=False)
    telephone = Column(String(20))
    statut = Column(String(20), default="disponible")
    nombre_dossiers_actifs = Column(Integer, default=0)
    capacite_max = Column(Integer, default=5)
    specialites = Column(String(255))
    date_creation = Column(DateTime, default=func.now())
    date_modification = Column(DateTime, default=func.now(), onupdate=func.now())

    # Relations
    escalades = relationship("EscaladeDB", back_populates="conseiller")

    def __repr__(self):
        return f"<ConseillerDB {self.prenom} {self.nom}>"


# ============================================================
# ESCALADES
# ============================================================
class EscaladeDB(Base):
    __tablename__ = "escalades"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    sinistre_id = Column(UUID(as_uuid=True), ForeignKey("sinistres.id"), nullable=False)
    conseiller_id = Column(UUID(as_uuid=True), ForeignKey("conseillers.id"))

    raison_escalade = Column(Text, nullable=False)
    cci_score_trigger = Column(Integer)
    details = Column(JSON)

    status = Column(String(20), default="en_attente")

    date_escalade = Column(DateTime, default=func.now())
    date_transfert = Column(DateTime)
    date_completion = Column(DateTime)

    # Relations
    sinistre = relationship("SinistreDB", back_populates="escalades")
    conseiller = relationship("ConseillerDB", back_populates="escalades")

    def __repr__(self):
        return f"<EscaladeDB {self.raison_escalade}>"
```

---

## ✅ ÉTAPE 3: SCHÉMAS PYDANTIC

### 3.1 Créer `backend/schemas/schemas.py`
```python
# backend/schemas/schemas.py

from pydantic import BaseModel, EmailStr, Field
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
    
    class Config:
        from_attributes = True

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
    franchise_collision: Decimal = 500
    franchise_vol: Decimal = 500
    franchise_incendie: Decimal = 500

class ContratResponse(ContratBase):
    id: uuid.UUID
    client_id: uuid.UUID
    statut: str
    date_creation: datetime
    
    class Config:
        from_attributes = True

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
    pass

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
    
    class Config:
        from_attributes = True

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
    
    class Config:
        from_attributes = True

# ============================================================
# SUIVI DOSSIER RESPONSE
# ============================================================
class ActionTimelineItem(BaseModel):
    action: str
    date: Optional[datetime] = None
    status: str
    details: Optional[dict] = None

class TimelineResponse(BaseModel):
    actions: List[ActionTimelineItem]

class SuiviDossierResponse(BaseModel):
    numero_sinistre: str
    type_sinistre: TypeSinistreEnum
    date_declaration: date
    status_dossier: StatusDossierEnum
    
    timeline_actions: List[ActionTimelineItem]
    remboursement: RemboursementResponse
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
# ESCALADE SCHEMAS
# ============================================================
class EscaladeRequest(BaseModel):
    sinistre_id: uuid.UUID
    raison: str
    cci_score: int

class EscaladeResponse(BaseModel):
    escalade_id: uuid.UUID
    conseiller_id: Optional[uuid.UUID] = None
    status: str
    date_escalade: datetime
```

---

## ✅ ÉTAPE 4: ENDPOINTS API

### 4.1 Créer `backend/routers/clients.py`
```python
# backend/routers/clients.py

from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session
from sqlalchemy import func
from decimal import Decimal
from uuid import UUID
from datetime import datetime, date

from database import get_db
from models.db_models import ClientDB, ContratDB, SinistreDB, RemboursementDB, ConseillerDB, EscaladeDB, ActionRecommandeeDB
from schemas.schemas import ClientResponse, ClientCreate, SinistreResponse, SuiviDossierResponse, ActionTimelineItem, RemboursementResponse

router = APIRouter(prefix="/api/v1", tags=["Clients"])

# ============================================================
# CLIENTS - Lookup par matricule
# ============================================================
@router.get("/clients/{matricule}", response_model=ClientResponse)
async def get_client_by_matricule(matricule: str, db: Session = Depends(get_db)):
    """
    Récupère un client par son matricule
    → Utilisé en PHASE 1: AUTHENTIFICATION
    """
    client = db.query(ClientDB).filter(ClientDB.matricule == matricule).first()
    
    if not client:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Client avec matricule {matricule} non trouvé"
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
# SINISTRES - Lookup dossiers actifs
# ============================================================
@router.get("/clients/{client_id}/sinistres", response_model=list[SinistreResponse])
async def get_client_sinistres(client_id: UUID, db: Session = Depends(get_db)):
    """
    Récupère tous les sinistres d'un client
    → Utilisé pour déterminer si c'est un nouveau sinistre ou suivi
    """
    sinistres = db.query(SinistreDB).filter(
        SinistreDB.client_id == client_id,
        SinistreDB.status_dossier != "fermé"
    ).all()
    
    return sinistres


@router.post("/sinistres", response_model=SinistreResponse)
async def create_sinistre(sinistre: dict, db: Session = Depends(get_db)):
    """
    Créer un nouveau sinistre
    → Utilisé en PHASE 5: DECISION (après analyse complète)
    """
    # Générer numéro sinistre unique
    client_id = sinistre.get("client_id")
    numero_sinistre = f"SINS-{sinistre.get('numero_base')}-{datetime.now().strftime('%y%m%d%H%M')}"
    
    db_sinistre = SinistreDB(
        numero_sinistre=numero_sinistre,
        **{k: v for k, v in sinistre.items() if k not in ["numero_sinistre"]}
    )
    
    db.add(db_sinistre)
    db.commit()
    db.refresh(db_sinistre)
    return db_sinistre


# ============================================================
# SUIVI DOSSIER - Endpoint clé pour PHASE 7
# ============================================================
@router.get("/sinistres/{sinistre_id}/suivi", response_model=SuiviDossierResponse)
async def suivi_dossier(sinistre_id: UUID, db: Session = Depends(get_db)):
    """
    Récupère l'état complet d'un dossier
    → Utilisé en PHASE 7: SUIVI
    
    Retourne:
    - Timeline des actions
    - Status remboursement
    - Garanties applicable
    - Actions en attente du client
    """
    sinistre = db.query(SinistreDB).filter(SinistreDB.id == sinistre_id).first()
    
    if not sinistre:
        raise HTTPException(status_code=404, detail="Sinistre non trouvé")
    
    # Récupérer remboursement
    remboursement = db.query(RemboursementDB).filter(
        RemboursementDB.sinistre_id == sinistre_id
    ).first()
    
    # Récupérer actions recommandées
    actions = db.query(ActionRecommandeeDB).filter(
        ActionRecommandeeDB.sinistre_id == sinistre_id,
        ActionRecommandeeDB.status != "completée"
    ).all()
    
    # Construire timeline
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
        timeline_actions.append(
            ActionTimelineItem(
                action=f"Assigné à {conseiller.prenom} {conseiller.nom}",
                date=escalade.date_escalade,
                status="✅ Complété",
                details={"conseiller": conseiller.telephone}
            )
        )
    
    # Ajouter actions en attente
    for action in actions:
        timeline_actions.append(
            ActionTimelineItem(
                action=action.action,
                date=action.date_limite,
                status=f"⏳ {action.status}",
                details={"description": action.description}
            )
        )
    
    # Garanties applicables (de contrat)
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
    
    remb_response = RemboursementResponse(
        montant_reclame=remboursement.montant_reclame if remboursement else 0,
        montant_accepte=remboursement.montant_accepte if remboursement else None,
        franchise=remboursement.franchise if remboursement else None,
        status=remboursement.status if remboursement else "en_attente"
    ) if remboursement else RemboursementResponse(
        montant_reclame=Decimal(0),
        status="en_attente"
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
```

### 4.2 Créer `backend/routers/conversation.py`
```python
# backend/routers/conversation.py

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.orm import Session
from sqlalchemy import desc
from uuid import UUID
import json
from datetime import datetime

from database import get_db
from models.db_models import ClientDB, SinistreDB, HistoriqueConversationDB, RemboursementDB, ActionRecommandeeDB
from schemas.schemas import MessageRequest, ConversationPhaseResponse
from modules.conversation_manager_crm import ConversationManager

router = APIRouter(prefix="/api/v1", tags=["Conversation"])

# Stocker les managers par session
active_conversations = {}


# ============================================================
# CONVERSATION - Authentification (PHASE 1)
# ============================================================
@router.post("/conversation/authenticate")
async def authenticate(matricule: str, db: Session = Depends(get_db)):
    """
    Vérifier le matricule et retourner les données client
    → PHASE 1: AUTHENTIFICATION
    """
    client = db.query(ClientDB).filter(ClientDB.matricule == matricule).first()
    
    if not client:
        return {
            "valide": False,
            "message": f"Matricule {matricule} non trouvé",
            "client": None
        }
    
    # Chercher sinistres actifs
    active_sinistres = db.query(SinistreDB).filter(
        SinistreDB.client_id == client.id,
        SinistreDB.status_dossier != "fermé"
    ).all()
    
    return {
        "valide": True,
        "message": f"Client trouvé: {client.nom} {client.prenom}",
        "client": {
            "id": str(client.id),
            "nom": client.nom,
            "prenom": client.prenom,
            "email": client.email,
            "telephone": client.telephone
        },
        "dossiers_actifs": len(active_sinistres),
        "sinistres": [
            {
                "numero": s.numero_sinistre,
                "type": s.type_sinistre,
                "status": s.status_dossier
            }
            for s in active_sinistres
        ]
    }


# ============================================================
# WEBSOCKET - Conversation complète
# ============================================================
@router.websocket("/ws/conversation/{session_id}")
async def websocket_conversation_endpoint(websocket: WebSocket, session_id: str, db: Session = Depends(get_db)):
    """
    WebSocket pour la conversation bidirectionnelle
    → Gère les 7 phases: AUTH → DESCRIPTION → DETAILS → DOCS → DECISION → TRANSFER → SUIVI
    """
    await websocket.accept()
    
    try:
        # Initialiser le manager
        conv_manager = ConversationManager(session_id)
        active_conversations[session_id] = conv_manager
        
        # PHASE 1: AUTHENTIFICATION
        # ────────────────────────
        greeting = conv_manager.get_greeting()
        await websocket.send_json({
            "phase": "AUTHENTIFICATION",
            "message": greeting["message"],
            "audio_url": greeting.get("audio_url"),
            "action": "demander_matricule"
        })
        
        client_id = None
        sinistre_id = None
        contexte = {"matricule": None, "client_data": None}
        
        while True:
            data = await websocket.receive_text()
            user_input = json.loads(data)
            
            current_phase = conv_manager.current_phase
            
            # === PHASE 1: AUTHENTIFICATION ===
            if current_phase == "AUTHENTIFICATION":
                matricule = user_input.get("text", "").strip()
                result = conv_manager.verifier_matricule(matricule, db)
                
                if result["valide"]:
                    client_data = result.get("client_data")
                    client_id = client_data["id"]
                    contexte["matricule"] = matricule
                    contexte["client_data"] = client_data
                    
                    # Vérifier sinistres existants
                    existing_sinistres = db.query(SinistreDB).filter(
                        SinistreDB.client_id == client_id,
                        SinistreDB.status_dossier != "fermé"
                    ).all()
                    
                    if len(existing_sinistres) > 0:
                        # PHASE 7: SUIVI (dossier existant)
                        conv_manager.current_phase = "SUIVI"
                        response = {
                            "phase": "SUIVI",
                            "message": conv_manager.suivi_dossier(existing_sinistres, db),
                            "audio_url": None,
                            "action": "afficher_dossiers",
                            "sinistres": [{"numero": s.numero_sinistre, "type": s.type_sinistre} for s in existing_sinistres]
                        }
                    else:
                        # PHASE 2: DESCRIPTION (nouveau sinistre)
                        conv_manager.current_phase = "DESCRIPTION"
                        response = {
                            "phase": "DESCRIPTION",
                            "message": conv_manager.ask_description(),
                            "audio_url": None,
                            "action": "demander_description"
                        }
                else:
                    response = {
                        "phase": "AUTHENTIFICATION",
                        "message": "Matricule invalide. Réessayez ou contactez le support.",
                        "audio_url": None,
                        "action": "demander_matricule"
                    }
                
                await websocket.send_json(response)
            
            # === PHASE 2: DESCRIPTION ===
            elif current_phase == "DESCRIPTION":
                description = user_input.get("text", "")
                result = conv_manager.analyser_description(description)
                
                sinistre_type = result.get("type_sinistre")
                cci_score = result.get("cci_score", 0)
                contexte.update({
                    "description": description,
                    "type_sinistre": sinistre_type,
                    "cci_score": cci_score,
                    "entities": result.get("entities", {})
                })
                
                conv_manager.current_phase = "SINISTRE_DETAILS"
                response = {
                    "phase": "SINISTRE_DETAILS",
                    "message": conv_manager.poser_questions_details(sinistre_type),
                    "audio_url": None,
                    "action": "poser_questions",
                    "type_sinistre": sinistre_type,
                    "cci_score": cci_score
                }
                
                await websocket.send_json(response)
            
            # === PHASE 3: SINISTRE_DETAILS ===
            elif current_phase == "SINISTRE_DETAILS":
                details = user_input.get("text", "")
                contexte["details_reponses"] = details
                
                # Mettre à jour CCI
                cci_increment = conv_manager.calculer_cci_incremental(details)
                contexte["cci_score"] = contexte.get("cci_score", 0) + cci_increment
                
                conv_manager.current_phase = "DOCUMENTS"
                response = {
                    "phase": "DOCUMENTS",
                    "message": conv_manager.demander_documents(),
                    "audio_url": None,
                    "action": "demander_documents",
                    "cci_score": contexte["cci_score"]
                }
                
                await websocket.send_json(response)
            
            # === PHASE 4: DOCUMENTS ===
            elif current_phase == "DOCUMENTS":
                documents_response = user_input.get("text", "")
                contexte["documents_status"] = documents_response
                
                # Évaluer si documents complets
                documents_complets = "envoie" in documents_response.lower() or "email" in documents_response.lower()
                
                conv_manager.current_phase = "DECISION"
                
                # === PHASE 5: DECISION (Autonome vs Escalade) ===
                final_cci = contexte.get("cci_score", 0)
                
                if final_cci > 60:  # SEUIL ESCALADE
                    # PHASE 6: TRANSFERT
                    conv_manager.current_phase = "TRANSFERT"
                    
                    # Créer le sinistre et l'escalade
                    sinistre_data = {
                        "client_id": client_id,
                        "numero_sinistre": f"SINS-{contexte['client_data']['matricule']}-{datetime.now().strftime('%y%m%d%H%M')}",
                        "type_sinistre": contexte["type_sinistre"],
                        "date_sinistre": datetime.now().date(),
                        "lieu_sinistre": contexte.get("entities", {}).get("lieu", "Non spécifié"),
                        "description": contexte["description"],
                        "cci_score": final_cci,
                        "status_dossier": "escalade",
                        "type_traitement": "escalade",
                        "documents_complets": documents_complets
                    }
                    
                    db_sinistre = SinistreDB(**sinistre_data)
                    db.add(db_sinistre)
                    db.flush()
                    
                    # Créer remboursement
                    remboursement = RemboursementDB(
                        sinistre_id=db_sinistre.id,
                        montant_reclame=3000.00  # À calculer réellement
                    )
                    db.add(remboursement)
                    
                    db.commit()
                    sinistre_id = str(db_sinistre.id)
                    
                    response = {
                        "phase": "TRANSFERT",
                        "message": conv_manager.preparer_transfert(sinistre_id),
                        "audio_url": None,
                        "action": "transferer_conseiller",
                        "sinistre_numero": sinistre_data["numero_sinistre"],
                        "cci_score": final_cci,
                        "raison_escalade": "CCI > 60: Dossier complexe"
                    }
                    
                else:  # AUTONOME
                    conv_manager.current_phase = "SUIVI"
                    
                    # Créer le sinistre en autonome
                    sinistre_data = {
                        "client_id": client_id,
                        "numero_sinistre": f"SINS-{contexte['client_data']['matricule']}-{datetime.now().strftime('%y%m%d%H%M')}",
                        "type_sinistre": contexte["type_sinistre"],
                        "date_sinistre": datetime.now().date(),
                        "lieu_sinistre": contexte.get("entities", {}).get("lieu", "Non spécifié"),
                        "description": contexte["description"],
                        "cci_score": final_cci,
                        "status_dossier": "en_cours",
                        "type_traitement": "autonome",
                        "documents_complets": documents_complets
                    }
                    
                    db_sinistre = SinistreDB(**sinistre_data)
                    db.add(db_sinistre)
                    db.flush()
                    
                    # Créer remboursement
                    remboursement = RemboursementDB(
                        sinistre_id=db_sinistre.id,
                        montant_reclame=3000.00
                    )
                    db.add(remboursement)
                    
                    # Créer actions recommandées
                    action1 = ActionRecommandeeDB(
                        sinistre_id=db_sinistre.id,
                        action="Appel expert automobile",
                        priorite="normal",
                        status="en_attente"
                    )
                    action2 = ActionRecommandeeDB(
                        sinistre_id=db_sinistre.id,
                        action="Fixer rendez-vous",
                        priorite="normal",
                        status="en_attente"
                    )
                    db.add_all([action1, action2])
                    
                    db.commit()
                    sinistre_id = str(db_sinistre.id)
                    
                    response = {
                        "phase": "SUIVI",
                        "message": conv_manager.suivi_message_autonome(sinistre_data["numero_sinistre"]),
                        "audio_url": None,
                        "action": "fin_conversation_autonome",
                        "sinistre_numero": sinistre_data["numero_sinistre"],
                        "cci_score": final_cci,
                        "type_traitement": "autonome"
                    }
                
                await websocket.send_json(response)
    
    except WebSocketDisconnect:
        print(f"❌ Client déconnecté: {session_id}")
        active_conversations.pop(session_id, None)
    except Exception as e:
        print(f"❌ Erreur WebSocket: {e}")
        await websocket.send_json({
            "phase": "ERROR",
            "message": "Une erreur s'est produite. Veuillez réessayer.",
            "error": str(e)
        })
```

---

## ✅ ÉTAPE 5: CONVERSATION MANAGER (Mis à jour)

### 5.1 Mettre à jour `modules/conversation_manager_crm.py`

[Voir le fichier existant - mettre à jour avec méthodes manquantes]

```python
# Ajouter ces méthodes à conversation_manager_crm.py

def ask_description(self):
    """Demander description du sinistre"""
    return "Merci! Pouvez-vous me décrire ce qui s'est passé?"

def suivi_dossier(self, sinistres, db):
    """Afficher options de suivi"""
    if len(sinistres) == 1:
        return f"Je vois que vous avez un dossier en cours: {sinistres[0].numero_sinistre}. C'est celui-ci?"
    else:
        return f"Vous avez {len(sinistres)} dossiers. Lequel voulez-vous suivre?"

def suivi_message_autonome(self, numero_sinistre):
    """Message de fin pour dossier autonome"""
    return f"""Parfait Ahmed! J'ai tous les éléments. Voici votre numéro: {numero_sinistre}
    
Vous allez recevoir un email avec les détails. L'expert vous contactera sous 48h.
Vous pouvez suivre votre dossier sur le portail avec votre matricule.

À bientôt!"""

def preparer_transfert(self, sinistre_id):
    """Message de transfert vers conseiller"""
    return """Je vais vous transférer vers l'un de nos conseillers.
    
Il va mieux vous accompagner pour ce dossier. Merci de patienter quelques secondes..."""

def calculer_cci_incremental(self, reponse):
    """Calculer l'incrément CCI basé sur la réponse"""
    cci = 0
    if "oui" in reponse.lower():
        cci += 10
    if "blessure" in reponse.lower() or "mal" in reponse.lower():
        cci += 15
    if "document" in reponse.lower() or "constat" in reponse.lower():
        cci += 10
    return cci
```

---

## ✅ ÉTAPE 6: DONNÉES DE TEST (Seed Data)

### 6.1 Créer `backend/seeds/seed_clients.py`
```python
# backend/seeds/seed_clients.py

from sqlalchemy.orm import Session
from models.db_models import ClientDB, ContratDB, ConseillerDB
from database import SessionLocal
from datetime import date, timedelta
import uuid

def seed_clients(db: Session):
    """Créer clients de test"""
    
    clients_data = [
        {
            "matricule": "AB-4521-22",
            "nom": "Ben Said",
            "prenom": "Ahmed",
            "email": "ahmed.bensaid@email.com",
            "telephone": "+212612345678",
            "civilite": "M",
            "date_naissance": date(1985, 5, 15),
            "adresse": "123 Rue de Paris",
            "ville": "Casablanca",
            "code_postal": "20000",
        },
        {
            "matricule": "FC-7834-19",
            "nom": "Dupont",
            "prenom": "Marie",
            "email": "marie.dupont@email.com",
            "telephone": "+212612345679",
            "civilite": "Mme",
            "date_naissance": date(1990, 3, 22),
            "adresse": "456 Rue de Lyon",
            "ville": "Rabat",
            "code_postal": "10000",
        },
        # ... 18 autres clients
    ]
    
    for client_data in clients_data:
        existing = db.query(ClientDB).filter(ClientDB.matricule == client_data["matricule"]).first()
        if not existing:
            client = ClientDB(**client_data)
            db.add(client)
            db.flush()
            
            # Ajouter contrat
            contrat = ContratDB(
                client_id=client.id,
                numero_contrat=f"CONT-{client_data['matricule']}-2024",
                type_assurance="auto",
                date_debut=date.today() - timedelta(days=365),
                garantie_collision=True,
                garantie_vol=True,
                garantie_incendie=True,
                garantie_responsabilite=True,
                garantie_assistance=True,
                franchise_collision=500,
                franchise_vol=500,
                franchise_incendie=500
            )
            db.add(contrat)
    
    db.commit()
    print("✅ Clients de test créés")


def seed_conseillers(db: Session):
    """Créer conseillers de test"""
    
    conseillers_data = [
        {
            "nom": "Dupont",
            "prenom": "Marie",
            "email": "marie.conseiller@lemonfox.fr",
            "telephone": "+212612340001",
            "specialites": "['collision', 'vol']",
        },
        {
            "nom": "Martin",
            "prenom": "Jean",
            "email": "jean.conseiller@lemonfox.fr",
            "telephone": "+212612340002",
            "specialites": "['incendie', 'dégâts']",
        },
        {
            "nom": "Bernard",
            "prenom": "Sophie",
            "email": "sophie.conseiller@lemonfox.fr",
            "telephone": "+212612340003",
            "specialites": "['blessure', 'responsabilite']",
        },
    ]
    
    for conseiller_data in conseillers_data:
        existing = db.query(ConseillerDB).filter(ConseillerDB.email == conseiller_data["email"]).first()
        if not existing:
            conseiller = ConseillerDB(**conseiller_data)
            db.add(conseiller)
    
    db.commit()
    print("✅ Conseillers de test créés")


if __name__ == "__main__":
    db = SessionLocal()
    try:
        seed_clients(db)
        seed_conseillers(db)
        print("✅ Seed complété avec succès!")
    finally:
        db.close()
```

### 6.2 Exécuter le seed
```bash
cd backend
python seeds/seed_clients.py
```

---

## ✅ ÉTAPE 7: MAIN.PY - Intégrer tout

### 7.1 Créer/Mettre à jour `backend/main.py`
```python
# backend/main.py

from fastapi import FastAPI, CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse
import os
from pathlib import Path

from database import init_db
from routers import clients, conversation

# Initialiser FastAPI
app = FastAPI(
    title="Insurance CRM API",
    description="API pour le CRM d'assurance avec gestion de conversation",
    version="1.0.0"
)

# CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialiser DB
@app.on_event("startup")
async def startup():
    print("🚀 Démarrage serveur...")
    init_db()
    print("✅ Database initialisée")

# Routes API
app.include_router(clients.router)
app.include_router(conversation.router)

# Health check
@app.get("/health")
async def health():
    return {"status": "✅ Online", "version": "1.0.0"}

# Audio serving
audio_dir = Path("data/audio_responses")
audio_dir.mkdir(parents=True, exist_ok=True)

@app.get("/audio/{filename}")
async def get_audio(filename: str):
    file_path = audio_dir / filename
    if file_path.exists():
        return FileResponse(file_path, media_type="audio/mpeg")
    return {"error": "Audio not found"}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
```

---

## ✅ ÉTAPE 8: TESTS

### 8.1 Créer `backend/tests/test_conversation.py`
```python
# backend/tests/test_conversation.py

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

from main import app
from database import get_db, Base
from models.db_models import ClientDB, ContratDB
from datetime import date

# Setup test DB
SQLALCHEMY_DATABASE_URL = "sqlite:///./test.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base.metadata.create_all(bind=engine)

def override_get_db():
    try:
        db = TestingSessionLocal()
        yield db
    finally:
        db.close()

app.dependency_overrides[get_db] = override_get_db

client = TestClient(app)

@pytest.fixture(autouse=True)
def setup_test_data():
    """Créer données de test avant chaque test"""
    db = TestingSessionLocal()
    
    # Créer client
    test_client = ClientDB(
        matricule="TEST-0001-01",
        nom="Test",
        prenom="Client",
        email="test@test.com",
        telephone="0612345678"
    )
    db.add(test_client)
    db.flush()
    
    # Créer contrat
    contrat = ContratDB(
        client_id=test_client.id,
        numero_contrat="CONT-TEST-2024",
        type_assurance="auto",
        date_debut=date.today(),
        garantie_collision=True
    )
    db.add(contrat)
    db.commit()
    
    yield db
    
    db.close()
    Base.metadata.drop_all(bind=engine)


def test_authenticate_valid_matricule():
    """Test authentification avec matricule valide"""
    response = client.post("/api/v1/conversation/authenticate?matricule=TEST-0001-01")
    assert response.status_code == 200
    assert response.json()["valide"] == True
    assert response.json()["client"]["nom"] == "Test"


def test_authenticate_invalid_matricule():
    """Test authentification avec matricule invalide"""
    response = client.post("/api/v1/conversation/authenticate?matricule=INVALID-0000-00")
    assert response.status_code == 200
    assert response.json()["valide"] == False


def test_health():
    """Test health check"""
    response = client.get("/health")
    assert response.status_code == 200
    assert response.json()["status"] == "✅ Online"


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
```

### 8.2 Exécuter les tests
```bash
cd backend
pytest tests/ -v
```

---

## ✅ ÉTAPE 9: LANCER LE SERVEUR

```bash
cd "c:\Users\HP\Inssurance Advanced\backend"

# Install dependencies
pip install -r requirements.txt

# Run seed
python seeds/seed_clients.py

# Start server
python main.py

# Vérifier: http://localhost:8000/health
```

---

## ✅ ÉTAPE 10: FRONTEND - Modifications React

Mettre à jour [frontend-client/pages/index.js] pour:
1. Demander matricule d'abord
2. Connecter WebSocket `/ws/conversation/{session_id}`
3. Afficher phases progressivement
4. Gérer audio à chaque phase

---

## 📊 CHECKLIST IMPLÉMENTATION

- [ ] PostgreSQL installé et schéma créé
- [ ] `backend/database.py` créé
- [ ] `backend/models/db_models.py` créé
- [ ] `backend/schemas/schemas.py` créé
- [ ] `backend/routers/clients.py` créé
- [ ] `backend/routers/conversation.py` créé
- [ ] `backend/main.py` mis à jour
- [ ] `backend/seeds/seed_clients.py` créé et exécuté
- [ ] Dépendances Python installées
- [ ] Tests unitaires passent
- [ ] Serveur démarre sans erreur sur port 8000
- [ ] WebSocket fonctionne
- [ ] Frontend connecté et conversation fluide

---

**Durée estimée:** 12-15 heures  
**Prêt à commencer?** ✅

