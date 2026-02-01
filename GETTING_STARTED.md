# 🚀 GUIDE DE DÉMARRAGE - Comment Utiliser le Système

## ⚡ Démarrage Ultra-Rapide (5 minutes)

### 1️⃣ Cloner le Projet
```bash
git clone https://github.com/animationproo48-png/Syst-me-Cognitif-de-Gestion-des-Sinistres.git
cd "Syst-me-Cognitif-de-Gestion-des-Sinistres"
```

### 2️⃣ Configuration des API Keys
Créer un fichier `.env` à la racine avec vos clés (voir `.env` existant pour le template):
```bash
WHISPER_API_KEY=[Your key]
GROQ_API_KEY=[Your key]
OPENAI_API_KEY=[Your key]
```

### 3️⃣ Lancer le Backend
```bash
cd backend
pip install -r requirements.txt
python main.py
```
✅ API disponible sur: `http://localhost:8000`

### 4️⃣ Lancer le Frontend Client (dans un autre terminal)
```bash
cd frontend-client
npm install
npm run dev
```
✅ Client disponible sur: `http://localhost:3000`

### 5️⃣ Lancer le Frontend Advisor (dans un 3ème terminal)
```bash
cd frontend-advisor
npm install
npm run dev
```
✅ Dashboard conseiller sur: `http://localhost:3001`

---

## 📋 Configuration Détaillée

### Backend (FastAPI)

**Dossier:** `backend/`

**Requirements:**
```bash
cd backend
pip install -r requirements.txt
```

**Lancer le serveur:**
```bash
python main.py
```

**Endpoints disponibles:**
- `POST /api/claims` - Créer un sinistre
- `GET /api/claims/{id}` - Récupérer un sinistre
- `GET /api/claims` - Lister les sinistres
- `WebSocket /ws/conversation/{session_id}` - Conversation vocale en temps réel

**Base de données:**
- Créée automatiquement: `data/claims_crm.db`
- Contient: sinistres, clients, historique

---

### Frontend Client (Next.js)

**Dossier:** `frontend-client/`

**Démarrer:**
```bash
cd frontend-client
npm install  # Première fois uniquement
npm run dev  # Lancer dev server
```

**Fonctionnalités:**
- 📞 Appel complet (TTS + auto-recording)
- 💬 Messagerie textuelle
- 📊 Dashboard client
- 🎤 Enregistrement audio en temps réel

**Accès:** `http://localhost:3000`

---

### Frontend Advisor (Next.js)

**Dossier:** `frontend-advisor/`

**Démarrer:**
```bash
cd frontend-advisor
npm install  # Première fois uniquement
npm run dev  # Lancer dev server (port 3001)
```

**Fonctionnalités:**
- 👨‍💼 Dashboard conseiller
- 📊 Liste des sinistres avec CCI score
- 📋 Détails clients & polices
- 🎯 Filtrage par priorité/complexité
- 📈 Statistiques en temps réel

**Accès:** `http://localhost:3001`

---

## 🧪 Test du Système

### Test 1: Interface Client

1. Ouvrir `http://localhost:3000`
2. Cliquer sur "📞 Appel Complet"
3. Parler: "Bonjour, j'ai eu un accrochage hier. L'autre a rayé mon aile."
4. Système répond automatiquement
5. Voir le résultat dans le Dashboard Advisor

### Test 2: Dashboard Conseiller

1. Ouvrir `http://localhost:3001`
2. Voir la liste des sinistres avec scores CCI
3. Cliquer sur un sinistre pour voir les détails
4. Voir la politique d'assurance du client
5. Voir la transcription et l'analyse cognitive

### Test 3: API Directe

```bash
# Créer un sinistre
curl -X POST http://localhost:8000/api/claims \
  -H "Content-Type: application/json" \
  -d '{"description": "Accident hier, rayure sur aile"}'

# Lister les sinistres
curl http://localhost:8000/api/claims
```

---

## 🗂️ Structure du Projet

```
Inssurance Advanced/
├── backend/                          # API FastAPI
│   ├── main.py                       # Serveur principal
│   ├── requirements.txt              # Dépendances Python
│   └── ...
├── frontend-client/                  # Interface client (Next.js)
│   ├── pages/index.js                # Page principale
│   ├── package.json
│   └── ...
├── frontend-advisor/                 # Dashboard conseiller (Next.js)
│   ├── pages/index.js                # Dashboard
│   ├── package.json
│   └── ...
├── modules/                          # 8 modules Python
│   ├── cognitive_engine.py
│   ├── complexity_calculator.py
│   ├── decision_engine.py
│   ├── stt_module.py
│   ├── tts_module.py
│   ├── crm_system.py
│   ├── summary_generator.py
│   └── conversation_manager.py
├── data/                             # Données
│   ├── claims_crm.db                 # Base de données SQLite
│   ├── temp_audio/                   # Fichiers audio temporaires
│   └── audio_responses/              # Réponses enregistrées
├── .env                              # Configuration (créer vôtre)
├── .gitignore
└── README.md                         # Documentation

```

---

## 🔌 Flux de Conversation Complet

### Côté Client

1. **Accueil** - Choisir mode (Appel Complet ou Messages)
2. **Enregistrement** - "📞 Appel Complet" = TTS + auto-recording
3. **Bot parle** - "Bonjour, comment puis-je vous aider?"
4. **Client parle** - 10 secondes d'enregistrement auto
5. **Envoi** - Enregistrement envoyé au backend via WebSocket
6. **Attente** - Spinner pendant traitement
7. **Réponse** - Bot répond vocalement + affiche transcription
8. **Répétition** - Boucle jusqu'à "fin"

### Côté Backend

1. **Reçoit audio** - Via WebSocket
2. **STT** - Transcription Whisper → texte
3. **Cognitive Engine** - Analyse le texte
4. **CCI Calculation** - Score de complexité (0-100)
5. **Decision Engine** - < 40 = auto, > 60 = escalade
6. **Summary Generator** - 3 niveaux de résumé
7. **TTS** - Génère réponse audio
8. **CRM Save** - Enregistre tout dans la DB
9. **WebSocket Send** - Renvoie réponse au client

### Côté Advisor

1. **Dashboard charge** - Via `http://localhost:3001`
2. **Liste sinistres** - Tous avec CCI scores
3. **Filtres** - Par priorité/complexité/date
4. **Click sinistre** - Voir détails complets
5. **Modal** - Client info + policy + CCI breakdown
6. **Timeline** - Historique conversation
7. **Actions** - Approuver, Rejeter, Escalader

---

## 🎯 Scénarios d'Utilisation

### Scénario 1: Sinistre Simple

**Client parle:**
> "Bonjour, j'ai eu un accrochage hier. L'autre conducteur a rayé mon aile. Nous avons fait un constat amiable."

**Système:**
- ✅ Transcription: Capturée
- ✅ Analyse: Auto simple (95% confiance)
- ✅ CCI Score: 28/100
- ✅ Décision: Traitement autonome
- ✅ Réponse: "Votre dossier sera traité en 24-48h"
- ✅ CRM: Sinistre sauvegardé

**Temps:** ~8 secondes

---

### Scénario 2: Sinistre Complexe

**Client parle:**
> "Euh... il y a eu un accident il y a quelques jours. Je crois qu'il y avait 3 voitures. Je ne sais pas qui a commencé. Je n'ai pas tous les papiers. Je suis stressé."

**Système:**
- ✅ Transcription: Capturée
- ⚠️ Détection: 5 hésitations, stress détecté
- 📊 CCI Score: 72/100
- 🔴 Décision: Escalade conseiller
- 📋 Brief généré automatiquement
- ✅ Réponse: "Un conseiller va vous rappeler"
- ✅ CRM: Tout enregistré avec drapeaux

**Advisor reçoit:**
- Sinistre avec score 72 en haut de liste
- Brief avec 3 ambiguïtés critiques
- Transcription complète
- 5 actions recommandées

---

## 🐛 Troubleshooting

### Problème: "Port déjà utilisé"

```bash
# Windows - Tuer le processus sur le port
netstat -ano | findstr :8000
taskkill /PID [PID] /F

# Linux/Mac
lsof -i :8000
kill -9 [PID]
```

### Problème: "API keys manquantes"

Vérifier le fichier `.env`:
```bash
# ❌ INCORRECT
GROQ_API_KEY=[Your key]

# ✅ CORRECT
GROQ_API_KEY=gsk_xxxxx...
```

### Problème: "WebSocket connexion échouée"

1. Vérifier que backend est lancé: `http://localhost:8000`
2. Vérifier les logs: `python main.py` devrait montrer les connexions
3. Attendre 2-3 secondes pour la connexion

### Problème: "Pas de son"

1. Vérifier les permissions du navigateur (Microphone)
2. Vérifier gTTS est installé: `pip install gtts`
3. Tester dans la console: Voir les logs du TTS

---

## 📊 Monitoring

### Logs du Backend

```bash
# Voir les logs en temps réel
python main.py

# Outputs:
# 📝 INFO: WebSocket connection opened: session_abc123
# 🎙️ AUDIO: Received 32KB from client
# 📤 STT: Whisper transcription completed
# 🧠 COGNITIVE: Analysis complete - score 45/100
# 💾 CRM: Claim saved - id: claim_xyz789
# 📤 TTS: Response sent to client
# 📝 INFO: WebSocket connection closed
```

### Base de Données

```bash
# Inspecter les sinistres
sqlite3 data/claims_crm.db "SELECT * FROM claims;"

# Exporter JSON
sqlite3 -json data/claims_crm.db "SELECT * FROM claims;" > claims.json
```

### Dashboard Browser

- Client: `http://localhost:3000/` → Voir transcriptions
- Advisor: `http://localhost:3001/` → Voir CCI scores
- API: `http://localhost:8000/docs` → Swagger interactive

---

## 🚀 Déploiement en Production

### Docker

```bash
# Build backend
docker build -t claims-backend ./backend

# Build client
docker build -t claims-client ./frontend-client

# Run
docker run -p 8000:8000 claims-backend
docker run -p 3000:3000 claims-client
```

### Cloud (AWS)

```bash
# Deploy backend to Lambda
serverless deploy

# Deploy frontend to CloudFront
aws s3 sync ./frontend-client/out s3://my-bucket/
```

### Production Checklist

- [ ] Certificat SSL configuré
- [ ] API keys sécurisées (AWS Secrets Manager)
- [ ] CORS configuré correctement
- [ ] Base de données sauvegardée
- [ ] Monitoring actif (CloudWatch)
- [ ] Alertes configurées
- [ ] Load balancer en place
- [ ] GDPR compliance vérifié

---

## 📞 Support

**Questions?**
- 📧 Email: animationproo48@gmail.com
- 🐙 GitHub Issues: https://github.com/animationproo48-png/Syst-me-Cognitif-de-Gestion-des-Sinistres/issues
- 📚 Docs: Voir `README.md` et `PRESENTATION_HACKATHON.md`

---

**Version:** 1.0 MVP | Date: February 1, 2026

🎉 **Prêt à démarrer? Suivez les 5 étapes ci-dessus!**
