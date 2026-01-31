# 🔧 Configuration du Système

## 📋 Variables d'Environnement

Le système utilise un fichier `.env` pour stocker les configurations sensibles.

### Fichier `.env` (Déjà Configuré)

```bash
# STT - Speech to Text
WHISPER_API_KEY=7fk3Ppa7utGvvHJ7MGUYwV3K24FpxxJh

# Cognitive Engine (Optionnel - pour mode LLM avancé)
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...

# CRM Database
CRM_DB_PATH=c:/Users/HP/Inssurance Advanced/data/claims_crm.db

# Audio Processing
AUDIO_TEMP_DIR=c:/Users/HP/Inssurance Advanced/data/temp_audio
AUDIO_RESPONSE_DIR=c:/Users/HP/Inssurance Advanced/data/audio_responses

# Seuils de Décision
AUTONOMOUS_THRESHOLD=40
```

### Modification de la Clé API

Si vous devez changer la clé API Whisper :

1. Ouvrir le fichier `.env`
2. Modifier la ligne :
   ```bash
   WHISPER_API_KEY=votre_nouvelle_cle
   ```
3. Sauvegarder
4. Redémarrer l'application

---

## 🎛️ Configuration des Modules

### 1. STT Engine (Speech-to-Text)

```python
from modules.stt_module import STTEngine

# Configuration par défaut (API Whisper)
engine = STTEngine()

# Configuration personnalisée
engine = STTEngine(
    model_name="base",  # tiny, base, small, medium, large
    use_api=True        # True = API, False = Local
)
```

**Options** :
- `model_name` : Modèle Whisper (pour mode local uniquement)
  - `tiny` : Le plus rapide, moins précis (39M paramètres)
  - `base` : Bon compromis (74M paramètres)
  - `small` : Meilleure qualité (244M paramètres)
  - `medium` : Très bon (769M paramètres)
  - `large` : Meilleur qualité (1550M paramètres)
- `use_api` : Mode de transcription
  - `True` : Utilise l'API Whisper (recommandé)
  - `False` : Utilise un modèle local (nécessite téléchargement)

### 2. Cognitive Engine

```python
from modules.cognitive_engine import CognitiveClaimEngine

# Configuration par défaut (règles)
engine = CognitiveClaimEngine()

# Configuration avec LLM
engine = CognitiveClaimEngine(
    use_llm=True,           # Utiliser GPT/Claude
    llm_provider="openai"   # "openai" ou "anthropic"
)
```

**Options** :
- `use_llm` : Utiliser un LLM pour l'analyse
  - `False` : Règles heuristiques (rapide, gratuit)
  - `True` : LLM avancé (plus précis, coûteux)
- `llm_provider` : Fournisseur LLM
  - `"openai"` : GPT-4 (nécessite OPENAI_API_KEY)
  - `"anthropic"` : Claude (nécessite ANTHROPIC_API_KEY)

### 3. Complexity Calculator

```python
from modules.complexity_calculator import ComplexityCalculator

calculator = ComplexityCalculator()
```

**Seuils de complexité** (modifiables dans le code) :
```python
# complexity_calculator.py
SIMPLE = 0-30       # Traitement autonome
MODERATE = 31-60    # Revue rapide
COMPLEX = 61-80     # Expertise requise
CRITICAL = 81-100   # Escalade immédiate
```

### 4. Decision Engine

```python
from modules.decision_engine import DecisionEngine

engine = DecisionEngine(
    autonomous_threshold=40  # CCI < 40 = autonome
)
```

**Options** :
- `autonomous_threshold` : Seuil CCI pour traitement autonome
  - Par défaut : 40
  - Valeurs recommandées : 30-50

### 5. CRM System

```python
from modules.crm_system import ClaimCRM

crm = ClaimCRM(
    db_path="data/claims_crm.db"  # Chemin base de données
)
```

**Options** :
- `db_path` : Chemin vers la base SQLite
  - Par défaut : Depuis .env ou `data/claims_crm.db`

---

## 📊 Configuration de l'Interface Streamlit

### Fichier `app.py`

Personnalisation de l'interface :

```python
# Configuration de la page
st.set_page_config(
    page_title="Cognitive Claim System",
    page_icon="🎙️",
    layout="wide",           # "wide" ou "centered"
    initial_sidebar_state="expanded"  # "expanded" ou "collapsed"
)
```

### Thème Streamlit

Créer `.streamlit/config.toml` :

```toml
[theme]
primaryColor = "#FF4B4B"
backgroundColor = "#FFFFFF"
secondaryBackgroundColor = "#F0F2F6"
textColor = "#262730"
font = "sans serif"

[server]
port = 8501
address = "localhost"
```

---

## 🔐 Sécurité

### Protection des Clés API

1. **NE JAMAIS** commiter `.env` sur Git
2. Le fichier `.gitignore` exclut déjà `.env`
3. Utiliser `.env.example` pour la documentation

### Fichier `.env.example`

```bash
# Copie de template (sans vraies clés)
WHISPER_API_KEY=your_whisper_api_key_here
OPENAI_API_KEY=your_openai_api_key_here
ANTHROPIC_API_KEY=your_anthropic_api_key_here

CRM_DB_PATH=data/claims_crm.db
AUDIO_TEMP_DIR=data/temp_audio
AUDIO_RESPONSE_DIR=data/audio_responses
AUTONOMOUS_THRESHOLD=40
```

---

## 📁 Structure des Dossiers

```
Inssurance Advanced/
├── .env                    # ✅ Configuration (ignoré par Git)
├── .env.example            # Template pour partage
├── app.py                  # Application Streamlit
├── modules/
│   ├── stt_module.py       # 🎙️ Transcription
│   ├── cognitive_engine.py # 🧠 Analyse
│   ├── complexity_calculator.py
│   └── ...
├── data/
│   ├── claims_crm.db       # Base de données SQLite
│   ├── temp_audio/         # Fichiers audio temporaires
│   └── audio_responses/    # Réponses TTS générées
└── models/
    └── claim_models.py     # Modèles Pydantic
```

---

## 🧪 Configuration de Test

### Mode Développement

```bash
# Variables pour dev/test
export ENVIRONMENT=development
export DEBUG=true
export LOG_LEVEL=DEBUG
```

### Mode Production

```bash
# Variables pour production
export ENVIRONMENT=production
export DEBUG=false
export LOG_LEVEL=INFO
```

---

## 🌍 Configuration Multilingue

### Langues Supportées

Le système supporte nativement :
- **Français** (`fr`)
- **Arabe** (`ar`)
- **Anglais** (`en`)

### Ajouter une Langue

1. Modifier `cognitive_engine.py` :
```python
LANGUAGE_PATTERNS = {
    "fr": [...],
    "ar": [...],
    "es": [...]  # Ajouter espagnol
}
```

2. Ajouter des transcriptions simulées dans `stt_module.py`
3. Tester avec `python test_system.py`

---

## ⚙️ Configuration Avancée

### Désactiver le Mode API

Pour forcer le mode local/simulation :

```python
# Dans app.py, ligne ~50
engine = STTEngine(use_api=False)
```

### Changer le Modèle Local

```python
# Télécharger un modèle plus précis
engine = STTEngine(
    model_name="medium",  # ou "large"
    use_api=False
)
```

**Note** : Les modèles plus gros sont plus lents mais plus précis.

### Activer le Mode LLM

Pour une analyse cognitive plus avancée :

1. Obtenir une clé OpenAI ou Anthropic
2. Ajouter dans `.env` :
   ```bash
   OPENAI_API_KEY=sk-...
   ```
3. Modifier `app.py` :
   ```python
   cognitive = CognitiveClaimEngine(use_llm=True)
   ```

---

## 📞 Support Configuration

Pour toute question de configuration :
1. Consulter [README.md](README.md)
2. Exécuter les tests : `python test_system.py`
3. Vérifier les logs : Streamlit affiche les erreurs dans le terminal

---

## ✅ Checklist de Configuration

- [x] `.env` créé avec WHISPER_API_KEY
- [x] Dépendances installées (`pip install -r requirements.txt`)
- [x] Tests réussis (`python test_whisper_api.py`)
- [ ] Dossier `data/` créé (créé automatiquement)
- [ ] Permissions sur `data/` configurées
- [ ] Streamlit lancé (`streamlit run app.py`)

---

Dernière mise à jour : Configuration complète et validée ✅
