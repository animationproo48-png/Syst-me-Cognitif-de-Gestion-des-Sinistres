# 🎙️ Système Cognitif de Gestion des Sinistres

## 🎯 Vue d'Ensemble

Système d'intelligence artificielle conversationnel pour la gestion autonome et cognitive des déclarations de sinistres d'assurance, avec interface vocale avancée (STT/TTS premium), moteur de décision intelligent, WebSocket temps réel et CRM simulé.

**Conçu pour:** Hackathon / MVP démonstration  
**Niveau de maturité:** Production-ready architecture  
**Langues supportées:** Français, Arabe Marocain (Darija), Arabe Standard (extensible)  
**Technologies vocales:** LemonFox STT, ElevenLabs Premium TTS, Groq LLM

---

## 🏗️ Architecture

### Modules Principaux

```
Insurance Advanced/
├── backend/
│   └── main.py                  # FastAPI WebSocket server (port 8000)
├── frontend-client/             # React/Next.js UI client (port 3000)
├── frontend-advisor/            # React/Next.js UI conseiller (port 3001)
├── models/
│   └── claim_models.py          # Modèles Pydantic (Digital Twin)
├── modules/
│   ├── stt_module.py            # Speech-to-Text (LemonFox API + Groq)
│   ├── tts_module.py            # Text-to-Speech (ElevenLabs Premium)
│   ├── cognitive_engine.py      # Moteur de compréhension cognitive
│   ├── complexity_calculator.py # Calcul CCI (Claim Complexity Index)
│   ├── decision_engine.py       # Décision & escalade intelligente
│   ├── summary_generator.py     # Résumés multi-niveaux
│   ├── conversation_manager.py  # Gestion conversation multi-tours
│   └── crm_system.py            # Simulation CRM (SQLite)
├── data/
│   ├── claims_crm.db            # Base de données CRM
│   ├── temp_audio/              # Fichiers audio temporaires
│   └── audio_responses/         # Réponses audio ElevenLabs (MP3)
├── app.py                       # Interface Streamlit (legacy)
├── requirements.txt             # Dépendances Python backend
└── README.md                    # Ce fichier
```
Premium (Production-Ready)**
- 🎤 **STT Avancé:** LemonFox API avec détection automatique Darija/Français
- 🔊 **TTS Premium:** ElevenLabs voices (7 voix disponibles, model Flash V2.5)
- 🌍 **Support Multilingue:** Français natif, Darija→Français (traduction Groq)
- 🎯 **Voix par défaut:** George (voix chaleureuse, storyteller britannique)
- ⚡ **Latence:** 75ms (11x plus rapide que model V2), -50% de coût
- 📱 **Streaming Audio:** WebSocket temps réel, lecture progressive côté client

### 2️⃣ **Conversation Interactive Multi-Tours**
- 💬 Flux conversationnel naturel guidé par phases
- 🔄 WebSocket bidirectionnel (FastAPI ↔ React)
- 📝 Collecte progressive: Type sinistre → Immatriculation → Nom/Prénom → CIN
- 🎙️ Audio automatique à chaque réponse (ElevenLabs)
- 🧠 Contexte persistant pendant toute la conversation

### 3️⃣ **Moteur Cognitif**
- Extraction structurée des faits vs suppositions
- Identification automatique du type de sinistre
- Détection d'ambiguïtés et incohérences
- Analyse du stress émotionnel
- Traduction contextuelle Darija→Français (regex détection caractères arabes)

### 4️⃣ **Indice de Complexité (CCI)**
- Score 0-100 déterministe et expliquable
- 6 dimensions analysées:
  - Garanties impliquées
  - Tiers impliqués
  - Documents manquants
  - Ambiguïtés
  - Stress émotionnel
  - Incohérences narratives

### 5️⃣ **Décision Intelligente**
- Autonomie vs Escalade basée sur règles expertes
- Brief structuré pour conseillers en cas d'escalade
- Recommandations d'actions contextuelles

### 6️⃣ **Résumés Multi-Niveaux**
- **Client:** Clair, rassurant, actionnable
- **Conseiller:** Structuré, technique, avec drapeaux de risque
- **Management:** KPIs, impact financier, risques

### 7️⃣ **CRM Simulé**
- Persistance SQLite
- Digital Twin complet de chaque sinistre
- Historique des interactions traçable
- Dashboard temps réel
- Synchronisation backend ↔ frontends

### 8️⃣ **Architecture React/Next.js**
- **Frontend Client:** Interface utilisateur moderne (port 3000)
- **Frontend Advisor:** Dashboard conseiller (port 3001)
- **Backend API:** FastAPI WebSocket + REST (port 8000)
- **Audio Streaming:** Endpoint `/audio/{filename}` pour MP3 ElevenLabs
- **État Temps Réel:** WebSocket pour messages et audio
### 6️⃣ **CRM Simulé**
- Persistance SQLite
- Digital Twin complet de chaque sinistre
- Historique des interactions traçable
- Dashboard temps réel

---

## 🚀 Installation & Lancement

### Prérequis
- Python 3.10+
- pip
- (Optionnel) FFmpeg pour traitement audio avancé

### Installation

```bash
# 1. Naviguer vers le dossier
cd "c:\Users\HP\Inssurance Advanced"

# 2. Créer environnement virtuel (recommandé)
python -m venv venv
.\venv\Scripts\activate

# 3. Installer dépendances
pip install -r requirements.txt

# 4. (Optionnel) Configurer OpenAI API pour LLM
# Créer un fichier .env:
echo OPENAI_API_KEY=votre_clé_ici > .env
```

### Lancement

```bash
streamlit run app.py
```

L'application sera accessible sur `http://localhost:8501`

---

## ⚛️ Lancer la version React (Next.js)

### 1️⃣ Backend (FastAPI)
```bash
cd backend
pip install -r requirements.txt
python main.py
```
✅ API: http://localhost:8000
OBLIGATOIRE)

Créer un fichier `.env` à la racine du projet :
```bash
# APIs Vocales (REQUIS)
WHISPER_API_KEY=YOUR_LEMONFOX_KEY           # STT LemonFox
GROQ_API_KEY=YOUR_GROQ_KEY                  # Traduction Darija
ELEVENLABS_API_KEY=YOUR_ELEVENLABS_KEY      # TTS Premium

# APIs LLM (Optionnel pour enrichissement)
OPENAI_API_KEY=YOUR_OPENAI_KEY
GEMINI_API_KEY=YOUR_GEMINI_KEY
```

### 🎤 Voix ElevenLabs Disponibles

Le système utilise **7 voix premium multilingues** (FR/EN/AR supporté):
🎯 Mode Conversationnel (React - Recommandé)

#### Flux Utilisateur Client (Port 3000)

1. **Accéder** à http://localhost:3000
2. **Cliquer** sur "🎙️ Commencer" pour démarrer la conversation
3. **Écouter** le message de bienvenue (voix ElevenLabs George)
4. **Parler** quand le micro s'active automatiquement:
   - Décrire le sinistre en **Français** ou **Darija**
   - Le système transcrit automatiquement (LemonFox STT)
   - Si Darija détecté → traduction Groq → réponse en français
5. **Suivre** les questions guidées:
   - Type de sinistre identifié
   - Immatriculation du véhicule
   - Nom et prénom
   - CIN (Carte Identité Nationale)
6. **Recevoir** la confirmation avec:
   - Résumé complet
   - Numéro de sinistre
   - Prochaines étapes
   - Tout en **audio naturel** (ElevenLabs)

#### Flux Conseiller (Port 3001)

1. **Accéder** à http://localhost:3001
2. **Visualiser** les sinistres en temps réel
3. **Recevoir** les cas escaladés avec brief détaillé
4. **Consulter** les transcriptions et analyses cognitives

### 🖥️ Mode Streamlit (Legacy)

1. **Naviguer** vers "🎙️ Nouvelle Déclaration"
2. **Choisir** le mode:
   - Upload fichier audio (MP3, WAV, etc.)
   - Texte simulé (démo rapide)
3. **Sélectionner** la langue (Français/Arabe)
4. **Cliquer** sur "🚀 Analyser"
5. **Observer** le traitement en temps réel
ELEVENLABS_API_KEY=YOUR_ELEVENLABS_KEY

# Optionnel
OPENAI_API_KEY=YOUR_OPENAI_KEY
GEMINI_API_KEY=YOUR_GEMINI_KEY
```

---

## 📖 Guide d'Utilisation

### Scénario 1: Nouvelle Déclaration Audio

1. **Naviguer** vers "🎙️ Nouvelle Déclaration"
2. **Choisir** le mode:
   - Upload fichier audio (MP3, WAV, etc.)
   - Texte simulé (démo rapide)
3. **Sélectionner** la langue (Français/Arabe)
4. **Cliquer** sur "🚀 Analyser"
5. **Observer** le traitement en temps réel:
   - Transcription
   - Analyse cognitive
   - Calcul de complexité
   - Décision autonomie/escalade
   - Génération réponse audio

### Scénario 2: Consultation CRM

1. **Naviguer** vers "📋 Tableau de Bord CRM"
2. **Filtrer** les sinistres par état/escalade
3. **Cliquer** sur un sinistre pour voir les détails complets

### Scénario 3: Statistiques

1. **Naviguer** vers "📊 Statistiques"
2. **Visualiser** les métriques globales et distributions

---

## 🧩 Exemples de Déclarations

### Exemple Simple (Score < 40)
```
"Bonjour, j'ai eu un petit accrochage hier sur un parking. 
L'autre conducteur a rayé mon aile avant en manœuvrant. 
Nous avons fait un constat amiable, il reconnaît sa faute. 
J'ai les photos et le constat signé."
```

**Résultat:** Traitement autonome, délai 24-48h

### Exemple Complexe (Score > 60)
```
"Euh, bonjour... je ne sais pas trop par où commencer. 
Il y a eu un accident, peut-être il y a trois jours, ou quatre. 
Il y avait plusieurs voitures impliquées, je pense trois ou quatre. 
Je nChanger la Voix ElevenLabs

Dans `modules/tts_module.py`:

```python
class TTSEngine:
    def __init__(self, voice="george"):  # Modifier ici
        # Options: george, alice, eric, jessica, will, roger, sarah
```

### Personnaliser le Modèle ElevenLabs

```python
# Dans modules/tts_module.py
model = "eleven_flash_v2_5"  # Options:
# - eleven_flash_v2_5 (recommandé, rapide, -50% prix)
# - eleven_multilingual_v2 (qualité max, +lent, +cher)
# - eleven_turbo_v2_5 (ultra rapide mais anglais only)
```

### Mode LLM (OpenAI GPT-4)

Pour activer l'extraction cognitive via LLM:

```python
# Dans cognitive_engine.py
cognitive_engine = CognitiveClaimEngine(
    use_llm=True,  # Active le mode LLM
    llm_provider="openai"
)
```

Nécessite: `OPENAI_API_KEY` dans variables d'environnement

### Désactiver la Traduction Darija

Dans `modules/stt_module.py`:

```python
# Mettre use_groq_translation=False pour désactiver
stt = STTModule(use_groq_translation=Fals

---

## 🛠️ Configuration Avancée

### Mode LLM (OpenAI GPT-4)

### Performances Vocales

- ⚡ **Latence STT:** ~1-2 secondes (LemonFox API)
- 🔊 **Latence TTS:** 75ms (ElevenLabs Flash V2.5)
- 🎯 **Qualité Audio:** Premium natural voice (11 langues ElevenLabs)
- 🌍 **Précision Darija:** ~90% (LemonFox spécialisé dialectes marocains)
- 🔁 **Traduction Groq:** <500ms (Darija→Français)

### Performances Système

- ⚡ **Temps de traitement complet:** 5-10 secondes (sans LLM)
- 🎯 **Précision classification type:** ~85% (règles expertes)
- 📈 **Taux d'escalade optimal:** 15-25% (selon seuils CCI)
- 🔌 **WebSocket:** Temps réel bidirectionnel (<100ms round-trip)

### Coûts Estimés (par conversation)

- **STT LemonFox:** ~$0.006/minute
- **TTS ElevenLabs Flash V2.5:** ~$0.015/1000 chars (-50% vs V2)
- **Traduction Groq:** ~$0.001/requête
- **Total conversation moyenne:** ~$0.05-0.10
cognitive_engine = CognitiveClaimEngine(
    use_llm=True,  # Active le mode LLM
    llm_provider="openai"
)
```

Nécessite: `OPENAI_API_KEY` dans variables d'environnement

### Mode TTS Avancé (Coqui)

Pour voix plus naturelle:

```bash
pip install TTS
```

```python
# Dans tts_module.py
tts_engine = TTSEngine(use_advanced=True)
```

---

## 📊 Métriques de Performance (Démo)

- ⚡ Temps de traitement: **5-10 secondes** (sans LLM)
- 🎯 Précision classification type: **~85%** (règles expertes)
- 📈 Taux d'escalade optimal: **15-25%** (selon seuils)
- 🔊 Qualité TTS: **Professionnelle** (gTTS standard)

---

## 🔐 Sécurité & Conformité

### Données Sensibles
- **Aucune donnée** envoyée à des tiers en mode règles
- Mode LLM: données envoyées à OpenAI (chiffrement TLS)
- **Recommandation production:** Utiliser Azure OpenAI (RGPD compliant)

### RGPD
- Anonymisation possible via paramétrage
- Droit à l'oubli: `crm.delete_claim(claim_id)`
- Export données: Format JSON standard

---

## 🚧 Limitations MVP

### Actuelles
- ❌ Pas d'authentification utilisateur
- ❌ Pas de validation contractuelle réelle
- ❌ Coûts non calculés (estimations indicatives)
- ❌ Pas d'intégration système de paiement

### Roadmap Production
- ✅ Authentification SSO
- ✅ Intégration API référentiel contrats
- ✅ Moteur de règles tarifaires
- ✅ Connexion gestionnaires externes
- ✅ OCR pour traitement documents
- ✅ Signature électronique

---

#### Backend
- **FastAPI** - API WebSocket + REST
- **Pydantic** - Validation données
- **LemonFox API** - STT spécialisé Darija/Français
- **ElevenLabs SDK** - TTS Premium (voices naturelles)
- **Groq** - Traduction LLM rapide (Darija→Français)
- **SQLite** - Persistance légère

#### Frontend
- **React** - UI components
- **Next.js** - Framework React production
- **TailwindCSS** - Styling moderne
- **WebSocket Client** - Communication temps réel
- **HTML5 Audio** - Streaming MP3 ElevenLabs

### Concepts Métier
- **Digital Twin** - Réplique numérique du sinistre
- **Cognitive Analysis** - Compréhension structurée
- **CCI** (Claim Complexity Index) - Métrique propriétaire
- **Escalation Engine** - Décision autonomie vs humain
- **Conversation Manager** - Flux multi-tours contextualisé
- **Audio Streaming** - Réponses vocales progressives

### Technologies Vocales
- **LemonFox:** STT cloud optimisé dialectes MENA (15+ dialectes)
- **ElevenLabs:** TTS premium 32 langues, 7 voix disponibles
- **Groq:** LLM ultra-rapide pour traduction contextuelle
- **Model Flash V2.5:** 75ms latency, 11x plus rapide que V2
# Adapter le calculateur de complexité
class ComplexityCalculator:
    def _calculate_guarantees_score(self, structure):
        base_complexity = {
            # ... existants
            "cyber_risque": 65  # Nouveau
        }
```

---

## 📞 Support & Contact

**Équipe Projet:**  
- Architecture:  AI Engineer: Badr eddine Tadlaoui
- Domaine: Expert Assurance : Moubin 
- UX: Interface Métier : Othman sadiki 

**Documentation Technique:**  
- Code commenté en français
- Docstrings conformes PEP 257
- Type hints Python 3.10+

---

## 📄 Licence

**Prototype MVP** - Usage interne hackathon  
© 2026 AssurTech Innovation Lab

---

## 🎓 Références Techniques

### Frameworks & Libraries
- **Streamlit** - Interface web
- **Pydantic** - Validation données
- **OpenAI Whisper** - Transcription audio
- **gTTS** - Synthèse vocale
- **SQLite** - Persistance légère

### Concepts Métier
- **Digital Twin** - Réplique numérique du sinistre
- **Cognitive Analysis** - Compréhension structurée
- **CCI** (Claim Complexity Index) - Métrique propriétaire
- **Escalation Engine** - Décision autonomie vs humain

---

**🚀 Ready for Demo!**
