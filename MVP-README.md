# 🚀 MVP Insurance - Plateforme de Gestion Cognitive des Sinistres

Architecture moderne **FastAPI + React** pour pitch investisseurs.

## 📊 Architecture

```
backend/              - FastAPI REST API + WebSocket
├── main.py           - Serveur principal
└── requirements.txt  - Dépendances Python

frontend-client/      - Interface client (React)
├── pages/index.js    - Page d'accueil & dialogue
└── package.json      - Dépendances Node

frontend-advisor/     - Dashboard expert (React)
├── pages/index.js    - Dashboard temps réel
└── package.json      - Dépendances Node
```

## 🎯 Fonctionnalités

### 👤 **Client Side** (port 3000)
- 🎙️ Dialogue conversationnel naturel
- 💬 Méthode LAMA (Listen, Acknowledge, Make statement, Ask)
- 🎨 Interface moderne & épurée
- ✨ Animations fluides (Framer Motion)
- 🔄 WebSocket temps réel

### 👨‍💼 **Advisor Dashboard** (port 3001)
- 📊 Métriques temps réel (KPIs)
- 📈 Graphiques interactifs (Recharts)
- 🎯 Vue des sinistres avec complexité
- 🚨 Alertes d'escalade
- ⚡ Refresh auto toutes les 5s

### ⚙️ **Backend** (port 8000)
- 🔌 API REST complète
- 📡 WebSocket pour dialogue temps réel
- 🧠 Intégration modules Python existants
- 📚 Documentation auto (Swagger/OpenAPI)
- 💾 Gestion CRM & statistiques

## 🚀 Démarrage Rapide

### Windows
```bash
# Double-cliquez sur:
start-mvp.bat
```

### Linux/Mac
```bash
chmod +x start-mvp.sh
./start-mvp.sh
```

### Manuel
```bash
# Terminal 1: Backend
cd backend
pip install -r requirements.txt
python main.py

# Terminal 2: Frontend Client
cd frontend-client
npm install
npm run dev

# Terminal 3: Frontend Advisor
cd frontend-advisor
npm install
npm run dev
```

## 🌐 URLs

| Service | URL | 
|---------|-----|
| Client | http://localhost:3000 |
| Advisor | http://localhost:3001 |
| Backend API | http://localhost:8000 |
| API Docs | http://localhost:8000/docs |

## 📝 API Endpoints

### Déclarations
```
POST   /api/claims              - Créer un sinistre
GET    /api/claims              - Lister tous les sinistres
GET    /api/claims/{id}         - Détails sinistre
```

### Conversation Temps Réel
```
WS     /ws/conversation/{sid}   - WebSocket dialogue
```

### Statistiques
```
GET    /api/statistics          - Métriques globales
```

## 🎨 Design

- **Palette**: Slate/Blue moderne (dark mode)
- **Animations**: Framer Motion pour fluidité
- **Framework CSS**: Tailwind CSS
- **Charts**: Recharts pour visualisations
- **Icons**: React Icons

## 📦 Dépendances Principales

### Backend
- FastAPI (API moderne)
- Uvicorn (serveur ASGI)
- Pydantic (validation données)

### Frontend
- Next.js 14 (framework React)
- Tailwind CSS (styles)
- Framer Motion (animations)
- Recharts (graphiques)
- Axios (requêtes HTTP)

## 🔧 Configuration

Modifier les ports dans:
- `backend/main.py` : `uvicorn.run(app, host="0.0.0.0", port=8000)`
- `frontend-client/package.json` : `"dev": "next dev -p 3000"`
- `frontend-advisor/package.json` : `"dev": "next dev -p 3001"`

## 📋 Prérequis

- Python 3.9+
- Node.js 16+
- npm ou yarn

## 🎯 Pour Investisseurs

Cette architecture démontre:
- ✅ **Technologie moderne** (FastAPI, React)
- ✅ **Scalabilité** (microservices, WebSocket)
- ✅ **UX premium** (design professionnel, animations)
- ✅ **API-first** (réutilisable, extensible)
- ✅ **Temps réel** (WebSocket, live updates)
- ✅ **Monitoring** (dashboard expert)

## 📞 Support

Pour toute question, consultez la documentation API:
`http://localhost:8000/docs`
