# 🔧 Plan d'Implémentation CRM Production

## Phase 1: Database Setup (2-3 heures)

### Tâche 1.1 - Installation PostgreSQL
```bash
# Windows (Chocolatey)
choco install postgresql

# ou télécharger: https://www.postgresql.org/download/windows/

# Connexion
psql -U postgres -d insurance_db
```

### Tâche 1.2 - Créer Schéma BDD
Exécuter le script `CRM_ARCHITECTURE.md` section "Schéma PostgreSQL" dans pgAdmin ou psql

### Tâche 1.3 - Seed Data (Données de test)
```python
# Créer script: backend/seeds/seed_clients.py
# Importer 10-20 clients de test avec:
# - Matricules variés (XX-123-XX format)
# - Contrats actifs
# - 2-3 sinistres en cours par client
```

---

## Phase 2: Backend API CRUD (4-5 heures)

### Tâche 2.1 - Dépendances
```bash
cd backend
pip install sqlalchemy psycopg2-binary alembic
```

### Tâche 2.2 - Modèles SQLAlchemy
Créer `backend/database.py`:
```python
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker

DATABASE_URL = "postgresql://user:password@localhost/insurance_db"
engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

Base = declarative_base()

# Models pour chaque table
class ClientDB(Base):
    __tablename__ = "clients"
    id = Column(String, primary_key=True)
    matricule = Column(String, unique=True)
    nom = Column(String)
    # ... autres colonnes

class SinistreDB(Base):
    __tablename__ = "sinistres"
    id = Column(String, primary_key=True)
    client_id = Column(String, ForeignKey("clients.id"))
    # ... autres colonnes
```

### Tâche 2.3 - Endpoints CRUD
Créer `backend/routers/clients.py`:
```python
@router.get("/clients/{matricule}")
async def get_client(matricule: str, db: Session = Depends(get_db)):
    client = db.query(ClientDB).filter(ClientDB.matricule == matricule).first()
    if not client:
        raise HTTPException(status_code=404)
    return ClientSchema.from_orm(client)

@router.post("/sinistres")
async def create_sinistre(sinistre: SinistreCreate, db: Session = Depends(get_db)):
    db_sinistre = SinistreDB(**sinistre.dict())
    db.add(db_sinistre)
    db.commit()
    return SinistreSchema.from_orm(db_sinistre)

@router.put("/sinistres/{sinistre_id}")
async def update_sinistre(sinistre_id: str, update: SinistreUpdate, db: Session = Depends(get_db)):
    # Update logic...
    pass

@router.get("/sinistres/{sinistre_id}/suivi")
async def suivi_dossier(sinistre_id: str, db: Session = Depends(get_db)):
    # Retourner état actuel
    pass
```

### Tâche 2.4 - Conversation Endpoints
Créer `backend/routers/conversation.py`:
```python
@router.post("/conversation/authenticate")
async def authenticate(matricule: str, db: Session = Depends(get_db)):
    # Vérifier matricule et retourner client
    pass

@router.post("/conversation/{sinistre_id}/message")
async def add_message(sinistre_id: str, msg: MessageConversation, db: Session = Depends(get_db)):
    # Ajouter message à historique
    # Évaluer si escalade nécessaire
    # Retourner réponse bot
    pass
```

---

## Phase 3: Conversation Manager (2-3 heures)

### Tâche 3.1 - Intégrer conversation_manager_crm.py
- ✅ Fichier déjà créé: `modules/conversation_manager_crm.py`
- Importer dans backend/main.py
- Instancier par session

### Tâche 3.2 - WebSocket Integration
```python
# Dans backend/main.py
@app.websocket("/ws/conversation/{session_id}")
async def websocket_endpoint(websocket: WebSocket, session_id: str):
    await websocket.accept()
    
    conv_manager = ConversationManager(session_id)
    
    # Étape 1: Greeting
    greeting = conv_manager.get_greeting()
    await websocket.send_json({
        "phase": "AUTHENTIFICATION",
        "message": greeting["message"],
        "audio_url": "..."  # Générer TTS
    })
    
    while True:
        data = await websocket.receive_text()
        
        if current_phase == AUTHENTIFICATION:
            result = conv_manager.verifier_matricule(data)
            if result["valide"]:
                # Passer à phase suivante
        elif current_phase == DESCRIPTION:
            result = conv_manager.analyser_description(data)
            # Continuer...
```

### Tâche 3.3 - Tests unitaires
```python
# tests/test_conversation.py
def test_matricule_valide():
    manager = ConversationManager("test-session")
    result = manager.verifier_matricule("XX-123-XX", mock_clients_db)
    assert result["valide"] == True

def test_escalade_trigger():
    # Tester que CCI > 60 trigger escalade
    pass
```

---

## Phase 4: Frontend Mise à Jour (3-4 heures)

### Tâche 4.1 - Suivi Dossier Client
Créer `frontend-client/pages/suivi.js`:
```javascript
export default function SuiviDossier() {
  const [dossiers, setDossiers] = useState([]);
  
  useEffect(() => {
    // GET /api/sinistres?client_id=X
    fetch(`/api/sinistres?client_id=${clientId}`)
      .then(r => r.json())
      .then(data => setDossiers(data));
  }, []);
  
  return (
    <div>
      {dossiers.map(dos => (
        <DossierCard
          numero={dos.numero_sinistre}
          status={dos.status_dossier}
          dateCreation={dos.date_creation}
          actions={dos.actions_en_cours}
          remboursement={dos.remboursement}
        />
      ))}
    </div>
  );
}
```

### Tâche 4.2 - Dashboard Conseiller Avancé
Créer `frontend-advisor/pages/dashboard.js`:
```javascript
export default function DashboardConseiller() {
  const [queue, setQueue] = useState([]);
  const [myDossiers, setMyDossiers] = useState([]);
  
  // Afficher:
  // - Queue escalade (dossiers en attente conseiller)
  // - Mes dossiers assignés
  // - Filtres par status/CCI
  // - Actions rapides (accepter, rejeter, demander docs)
}
```

### Tâche 4.3 - Mise à Jour Flux Conversation
Modifier `frontend-client/pages/index.js` pour:
- Phase 1: Demander matricule au lieu de description directe
- Charger données client au backend
- Afficher confirmer identité
- Passer à description

---

## Phase 5: Tests & Déploiement (2-3 heures)

### Tâche 5.1 - Tests Intégration
```bash
cd backend
pytest tests/

# Checker:
# ✅ POST /api/clients retourne 201
# ✅ GET /api/clients/{matricule} retourne 200
# ✅ POST /sinistres crée et retourne numero
# ✅ WebSocket conversation complete flow
# ✅ Escalade trigger CCI > 60
```

### Tâche 5.2 - Perf PostgreSQL
```sql
-- Vérifier indexes existent
SELECT * FROM pg_indexes WHERE tablename = 'sinistres';

-- Tester requête lente
EXPLAIN ANALYZE
SELECT * FROM sinistres WHERE client_id = 'X' AND status_dossier = 'en_cours';
```

### Tâche 5.3 - Deploy Docker
```dockerfile
# Créer backend/Dockerfile
FROM python:3.10
RUN pip install -r requirements.txt
CMD ["python", "main.py"]

# Créer docker-compose.yml
services:
  postgres:
    image: postgres:13
    environment:
      POSTGRES_DB: insurance_db
  backend:
    build: ./backend
    depends_on:
      - postgres
  frontend-client:
    build: ./frontend-client
  frontend-advisor:
    build: ./frontend-advisor
```

---

## Checklist de Finalisation

### Backend
- [ ] PostgreSQL installé et schéma créé
- [ ] Modèles SQLAlchemy complets
- [ ] CRUD endpoints opérationnels
- [ ] ConversationManager intégré
- [ ] WebSocket phase AUTHENTIFICATION → DECISION
- [ ] Escalade automatique CCI > 60
- [ ] Historique conversation persisté
- [ ] Tests unitaires > 80% couverture

### Frontend
- [ ] Phase matricule implémentée
- [ ] Chargement données client depuis API
- [ ] Suivi dossier avec refresh temps réel
- [ ] Dashboard conseiller avec queue
- [ ] Transfert WebSocket vers conseiller

### Données
- [ ] 20+ clients de test avec matricules
- [ ] 5+ sinistres en cours par client
- [ ] Remboursements test
- [ ] Documents test uploadés

### Déploiement
- [ ] Docker Compose opérationnel
- [ ] PostgreSQL backup/restore testé
- [ ] RGPD anonymisation implémentée
- [ ] Logs audit complets

---

## Commandes Rapides

```bash
# Démarrer tout
docker-compose up -d

# Tests backend
cd backend && pytest -v

# Logs
docker logs insurance-backend
docker logs insurance-postgres

# Reset BDD
docker exec insurance-postgres psql -U postgres -d insurance_db -c "DROP SCHEMA public CASCADE; CREATE SCHEMA public;"
```

---

## Ressources

- PostgreSQL: https://www.postgresql.org/docs/
- SQLAlchemy: https://docs.sqlalchemy.org/
- Alembic (migrations): https://alembic.sqlalchemy.org/
- Docker Compose: https://docs.docker.com/compose/
