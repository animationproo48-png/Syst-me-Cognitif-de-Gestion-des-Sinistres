#!/usr/bin/env python
"""
Complete Insurance CRM Backend Startup
Handles: Database init, seed, and server start
Run from project root: python start_backend.py
"""
import sys
import os
import subprocess
from pathlib import Path
from sqlalchemy import text

# Setup paths
project_root = Path(__file__).parent
sys.path.insert(0, str(project_root))
sys.path.insert(0, str(project_root / "backend"))

def init_database():
    """Initialize database schema"""
    print("[*] Initializing database schema...")
    from backend.database import engine, Base
    from backend.models import db_models
    
    try:
        Base.metadata.create_all(bind=engine)
        with engine.connect() as conn:
            conn.execute(text("SELECT 1"))
        print("[OK] Database initialized")
        return True
    except Exception as e:
        print(f"[ERROR] Database init failed: {e}")
        return False

def seed_database():
    """Seed test data"""
    print("\n[*] Seeding test data...")
    from backend.database import SessionLocal
    from backend.models.db_models import ClientDB, ContratDB, ConseillerDB
    import uuid
    from datetime import datetime, timedelta
    
    db = SessionLocal()
    try:
        # Check if already seeded
        if db.query(ClientDB).count() > 0:
            print("[!] Database already seeded")
            return True
        
        # Create clients
        clients_data = [
            ("AB-4521-22", "Ahmed", "Ben Ali", "ahmed.benali@email.com", "06 12 34 56 78"),
            ("FC-7834-19", "Fatima", "Choudhury", "fatima.c@email.com", "06 98 76 54 32"),
            ("JK-1234-20", "Jamal", "Karim", "jamal.karim@email.com", "06 55 44 33 22"),
            ("LM-5678-21", "Leila", "Mansouri", "leila.mansouri@email.com", "06 11 22 33 44"),
            ("NO-9012-22", "Nadia", "Okacha", "nadia.okacha@email.com", "06 77 88 99 00"),
        ]
        
        for matricule, nom, prenom, email, telephone in clients_data:
            client = ClientDB(
                id=uuid.uuid4(),
                matricule=matricule,
                nom=nom,
                prenom=prenom,
                email=email,
                telephone=telephone,
                civilite="Mr" if nom in ["Ahmed", "Jamal"] else "Mme",
                statut="actif",
                date_creation=datetime.now(),
                date_modification=datetime.now()
            )
            db.add(client)
            
            # Create contract
            contrat = ContratDB(
                id=uuid.uuid4(),
                numero_contrat=f"CTR-{matricule}",
                client_id=client.id,
                type_assurance="automobile_comprehensive",
                date_debut=datetime.now().date(),
                date_fin=(datetime.now() + timedelta(days=365)).date(),
                statut="actif",
                garantie_collision=True,
                garantie_vol=True,
                garantie_responsabilite=True,
                garantie_assistance=True,
                date_creation=datetime.now(),
                date_modification=datetime.now()
            )
            db.add(contrat)
        
        # Create conseillers
        conseillers_data = [
            ("Ahmed", "Conseil", "conseil.ahmed@insurance.com", "05 12 34 56 78"),
            ("Fatima", "Expert", "expert.fatima@insurance.com", "05 98 76 54 32"),
            ("Khalid", "Support", "support.khalid@insurance.com", "05 55 44 33 22"),
        ]
        
        for prenom, nom, email, telephone in conseillers_data:
            conseiller = ConseillerDB(
                id=uuid.uuid4(),
                nom=nom,
                prenom=prenom,
                email=email,
                telephone=telephone,
                statut="disponible",
                nombre_dossiers_actifs=0,
                capacite_max=10,
                date_creation=datetime.now(),
                date_modification=datetime.now()
            )
            db.add(conseiller)
        
        db.commit()
        print(f"[OK] Seeded 5 clients and 3 advisors")
        return True
    except Exception as e:
        db.rollback()
        print(f"[ERROR] Seed failed: {e}")
        return False
    finally:
        db.close()

def main():
    """Main startup sequence"""
    print("\n" + "="*60)
    print("[*] INSURANCE CRM BACKEND STARTUP")
    print("="*60 + "\n")
    
    # Step 1: Initialize database
    if not init_database():
        sys.exit(1)
    
    # Step 2: Seed test data
    if not seed_database():
        sys.exit(1)
    
    print("\n" + "="*60)
    print("[OK] BACKEND READY")
    print("="*60)
    print("\n[*] Test endpoints:")
    print("  - Health check: http://localhost:8000/health")
    print("  - Get client AB-4521-22: http://localhost:8000/api/v1/clients/AB-4521-22")
    print("  - Authenticate: POST http://localhost:8000/api/v1/conversation/authenticate")
    print("  - WebSocket: ws://localhost:8000/ws/conversation/{session_id}")
    print("\n[*] Starting server...\n")
    
    # Step 3: Start server
    os.chdir(str(project_root / "backend"))
    os.system("python -m uvicorn main:app --host 0.0.0.0 --port 8000 --reload")

if __name__ == "__main__":
    main()
