# backend/database.py

from sqlalchemy import create_engine, event, text
from sqlalchemy.orm import sessionmaker, declarative_base
from sqlalchemy.pool import QueuePool
import os
from dotenv import load_dotenv
import logging

load_dotenv()

logger = logging.getLogger(__name__)

# Configuration Database (PostgreSQL for production, SQLite for development)
DATABASE_URL = os.getenv(
    "DATABASE_URL",
    "sqlite:///./insurance.db"  # Default to SQLite for development
)

# Engine configuration based on database type
if "postgresql" in DATABASE_URL:
    # Production PostgreSQL with connection pooling
    engine = create_engine(
        DATABASE_URL,
        poolclass=QueuePool,
        pool_size=10,
        max_overflow=20,
        pool_pre_ping=True,
        pool_recycle=3600,
        echo=False,
        connect_args={"connect_timeout": 10}
    )
elif "sqlite" in DATABASE_URL:
    # Development SQLite (no connection pooling)
    engine = create_engine(
        DATABASE_URL,
        connect_args={"check_same_thread": False},
        echo=False
    )
else:
    # Fallback for other databases
    engine = create_engine(DATABASE_URL, echo=False)

# Session factory
SessionLocal = sessionmaker(
    autocommit=False,
    autoflush=False,
    bind=engine,
    expire_on_commit=False
)

Base = declarative_base()


def get_db():
    """Dépendance FastAPI pour session DB"""
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()


def init_db():
    """Initialiser la base de données"""
    try:
        # Import des modèles APRÈS déclaration de Base
        from backend.models.db_models import (
            ClientDB, ContratDB, SinistreDB, HistoriqueConversationDB,
            ActionRecommandeeDB, RemboursementDB, ConseillerDB, EscaladeDB
        )
        
        # Créer les tables
        Base.metadata.create_all(bind=engine)
        logger.info("Database initialized successfully")
        return True
    except Exception as e:
        logger.error(f"Database init error: {e}")
        return False


def get_db_connection():
    """Tester la connexion DB"""
    try:
        with engine.connect() as conn:
            result = conn.execute(text("SELECT 1"))
            return True
    except Exception as e:
        logger.error(f"Connexion DB failed: {e}")
        return False
