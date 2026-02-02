# backend/seeds/seed_data.py

from sqlalchemy.orm import Session
from backend.models import ClientDB, ContratDB, ConseillerDB, SinistreDB, RemboursementDB
from backend.database import SessionLocal
from datetime import date, timedelta
import logging

logger = logging.getLogger(__name__)


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
        {
            "matricule": "JK-1234-20",
            "nom": "Martin",
            "prenom": "Jean",
            "email": "jean.martin@email.com",
            "telephone": "+212612345680",
            "civilite": "M",
            "date_naissance": date(1980, 7, 10),
            "adresse": "789 Rue de Marseille",
            "ville": "Fès",
            "code_postal": "30000",
        },
        {
            "matricule": "LM-5678-21",
            "nom": "Garcia",
            "prenom": "Isabella",
            "email": "isabella.garcia@email.com",
            "telephone": "+212612345681",
            "civilite": "Mme",
            "date_naissance": date(1992, 12, 5),
            "adresse": "321 Rue de Toulouse",
            "ville": "Tangier",
            "code_postal": "90000",
        },
        {
            "matricule": "NO-9012-22",
            "nom": "Thibault",
            "prenom": "Pierre",
            "email": "pierre.thibault@email.com",
            "telephone": "+212612345682",
            "civilite": "M",
            "date_naissance": date(1988, 9, 20),
            "adresse": "654 Rue de Nice",
            "ville": "Marrakech",
            "code_postal": "40000",
        },
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
    logger.info("✅ Clients seed completed")


def seed_conseillers(db: Session):
    """Créer conseillers de test"""
    conseillers_data = [
        {
            "nom": "Dupont",
            "prenom": "Marie",
            "email": "marie.conseiller@lemonfox.fr",
            "telephone": "+212612340001",
            "specialites": "collision,vol",
        },
        {
            "nom": "Martin",
            "prenom": "Jean",
            "email": "jean.conseiller@lemonfox.fr",
            "telephone": "+212612340002",
            "specialites": "incendie,dégâts",
        },
        {
            "nom": "Bernard",
            "prenom": "Sophie",
            "email": "sophie.conseiller@lemonfox.fr",
            "telephone": "+212612340003",
            "specialites": "blessure,responsabilite",
        },
    ]
    
    for conseiller_data in conseillers_data:
        existing = db.query(ConseillerDB).filter(ConseillerDB.email == conseiller_data["email"]).first()
        if not existing:
            conseiller = ConseillerDB(**conseiller_data)
            db.add(conseiller)
    
    db.commit()
    logger.info("✅ Conseillers seed completed")


def seed_all():
    """Exécuter tous les seeds"""
    db = SessionLocal()
    try:
        logger.info("🌱 Starting seed...")
        seed_clients(db)
        seed_conseillers(db)
        logger.info("✅ All seeds completed successfully!")
    except Exception as e:
        logger.error(f"❌ Seed error: {e}")
        db.rollback()
    finally:
        db.close()


if __name__ == "__main__":
    import sys
    logging.basicConfig(level=logging.INFO)
    seed_all()
