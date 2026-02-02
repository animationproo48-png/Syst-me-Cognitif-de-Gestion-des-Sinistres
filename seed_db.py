#!/usr/bin/env python
"""
Seed test data into database
Run from project root: python seed_db.py
"""
import sys
from pathlib import Path

# Setup paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

from backend.database import SessionLocal
from backend.models.db_models import ClientDB, ContratDB, ConseillerDB
import uuid
from datetime import datetime, timedelta

print("🌱 Seeding test data...")

db = SessionLocal()

try:
    # Check if data already exists
    existing_clients = db.query(ClientDB).count()
    if existing_clients > 0:
        print(f"⚠️  Database already contains {existing_clients} clients. Skipping seed...")
        db.close()
        sys.exit(0)
    
    # Create test clients
    clients_data = [
        {
            "matricule": "AB-4521-22",
            "nom": "Ahmed",
            "prenom": "Ben Ali",
            "email": "ahmed.benali@email.com",
            "telephone": "06 12 34 56 78",
            "civilite": "Mr",
            "date_naissance": datetime(1985, 5, 15).date(),
            "adresse": "123 Rue de la Paix",
            "ville": "Casablanca",
            "code_postal": "20000",
            "pays": "Maroc",
            "statut": "actif"
        },
        {
            "matricule": "FC-7834-19",
            "nom": "Fatima",
            "prenom": "Choudhury",
            "email": "fatima.c@email.com",
            "telephone": "06 98 76 54 32",
            "civilite": "Mme",
            "date_naissance": datetime(1990, 3, 22).date(),
            "adresse": "456 Boulevard Mohamed V",
            "ville": "Fès",
            "code_postal": "30000",
            "pays": "Maroc",
            "statut": "actif"
        },
        {
            "matricule": "JK-1234-20",
            "nom": "Jamal",
            "prenom": "Karim",
            "email": "jamal.karim@email.com",
            "telephone": "06 55 44 33 22",
            "civilite": "Mr",
            "date_naissance": datetime(1988, 7, 10).date(),
            "adresse": "789 Avenue Hassan II",
            "ville": "Rabat",
            "code_postal": "10000",
            "pays": "Maroc",
            "statut": "actif"
        },
        {
            "matricule": "LM-5678-21",
            "nom": "Leila",
            "prenom": "Mansouri",
            "email": "leila.mansouri@email.com",
            "telephone": "06 11 22 33 44",
            "civilite": "Mme",
            "date_naissance": datetime(1992, 11, 5).date(),
            "adresse": "321 Rue de l'Indépendance",
            "ville": "Marrakech",
            "code_postal": "40000",
            "pays": "Maroc",
            "statut": "actif"
        },
        {
            "matricule": "NO-9012-22",
            "nom": "Nadia",
            "prenom": "Okacha",
            "email": "nadia.okacha@email.com",
            "telephone": "06 77 88 99 00",
            "civilite": "Mme",
            "date_naissance": datetime(1995, 2, 14).date(),
            "adresse": "654 Boulevard du Commerce",
            "ville": "Agadir",
            "code_postal": "80000",
            "pays": "Maroc",
            "statut": "actif"
        }
    ]
    
    for client_data in clients_data:
        client = ClientDB(
            id=uuid.uuid4(),
            **client_data,
            date_creation=datetime.now(),
            date_modification=datetime.now()
        )
        db.add(client)
        
        # Create contract for each client
        contrat = ContratDB(
            id=uuid.uuid4(),
            numero_contrat=f"CTR-{client_data['matricule']}",
            client_id=client.id,
            type_assurance="automobile_comprehensive",
            date_debut=datetime.now().date(),
            date_fin=(datetime.now() + timedelta(days=365)).date(),
            statut="actif",
            garantie_collision=True,
            garantie_vol=True,
            garantie_incendie=True,
            garantie_responsabilite=True,
            garantie_assistance=True,
            franchise_collision=1000,
            franchise_vol=500,
            franchise_incendie=500,
            limite_responsabilite=1000000,
            limite_collision=500000,
            limite_vol=300000,
            date_creation=datetime.now(),
            date_modification=datetime.now()
        )
        db.add(contrat)
    
    db.commit()
    client_count = db.query(ClientDB).count()
    print(f"✅ Created {client_count} test clients with contracts")
    
    # Create test advisors
    conseillers_data = [
        {
            "nom": "Conseil",
            "prenom": "Ahmed",
            "email": "conseil.ahmed@insurance.com",
            "telephone": "05 12 34 56 78",
            "statut": "disponible",
            "nombre_dossiers_actifs": 0,
            "capacite_max": 5,
            "specialites": "sinistres_automobiles,reclamations"
        },
        {
            "nom": "Expert",
            "prenom": "Fatima",
            "email": "expert.fatima@insurance.com",
            "telephone": "05 98 76 54 32",
            "statut": "disponible",
            "nombre_dossiers_actifs": 0,
            "capacite_max": 8,
            "specialites": "evaluations_dommages,negociations"
        },
        {
            "nom": "Support",
            "prenom": "Khalid",
            "email": "support.khalid@insurance.com",
            "telephone": "05 55 44 33 22",
            "statut": "disponible",
            "nombre_dossiers_actifs": 0,
            "capacite_max": 10,
            "specialites": "assistance_clients,suivi_dossiers"
        }
    ]
    
    for conseiller_data in conseillers_data:
        conseiller = ConseillerDB(
            id=uuid.uuid4(),
            **conseiller_data,
            date_creation=datetime.now(),
            date_modification=datetime.now()
        )
        db.add(conseiller)
    
    db.commit()
    conseiller_count = db.query(ConseillerDB).count()
    print(f"✅ Created {conseiller_count} test advisors")
    
    print("\n📊 Database seed complete!")
    print("✅ Ready for testing")
    
except Exception as e:
    db.rollback()
    print(f"❌ Error: {e}")
    import traceback
    traceback.print_exc()
    sys.exit(1)
finally:
    db.close()
