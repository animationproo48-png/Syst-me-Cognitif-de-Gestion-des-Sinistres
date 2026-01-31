# 🎙️ Guide d'Utilisation API Whisper

## ✅ Statut de l'Intégration

**L'API Whisper est maintenant intégrée et fonctionnelle !**

- **Clé API** : Configurée dans `.env`
- **Dépendances** : Toutes installées
- **Tests** : 4/4 réussis ✅

---

## 🚀 Modes de Fonctionnement

Le système STT fonctionne en 3 modes avec fallback automatique :

### 1. **Mode API** (Priorité 1) 🌐
- Utilise l'API Whisper d'OpenAI
- Meilleure qualité de transcription
- Supporte tous les formats audio
- Détection automatique de la langue
- **Actif par défaut quand la clé API est configurée**

### 2. **Mode Local** (Priorité 2) 🖥️
- Utilise un modèle Whisper téléchargé localement
- Nécessite `pip install openai-whisper`
- Fonctionne hors ligne
- Utilisé si l'API échoue

### 3. **Mode Simulation** (Fallback) 🎭
- Transcriptions pré-enregistrées pour démo
- Aucune dépendance requise
- Utilisé uniquement si les 2 autres modes échouent

---

## 📝 Utilisation dans l'Application

### Avec Streamlit (Interface Web)

```bash
streamlit run app.py
```

1. Aller sur **"📞 Nouvelle Déclaration"**
2. Choisir un mode d'entrée :

#### **🎤 Enregistrement Audio** (Recommandé)
- Cliquer sur le bouton microphone
- Parler en français ou arabe
- L'API Whisper transcrit automatiquement

#### **📁 Upload Audio**
- Uploader un fichier `.wav`, `.mp3`, `.m4a`, `.ogg`
- L'API traite le fichier
- Transcription affichée en quelques secondes

#### **💬 Simulation Textuelle**
- Mode texte pour tests rapides
- Pas de transcription audio

---

## 🧪 Test avec Python

### Test Simple

```python
from modules.stt_module import STTEngine

# Initialiser avec API
engine = STTEngine(use_api=True)

# Transcrire un fichier
result = engine.transcribe_audio("mon_audio.wav", language="fr")

print(f"Transcription : {result.normalized_transcript}")
print(f"Langue détectée : {result.language}")
print(f"Confiance : {result.confidence_score}")
```

### Test Complet

```bash
python test_whisper_api.py
```

---

## 🎯 Formats Audio Supportés

L'API Whisper accepte :
- **WAV** (`.wav`)
- **MP3** (`.mp3`)
- **M4A** (`.m4a`)
- **OGG** (`.ogg`)
- **FLAC** (`.flac`)
- **WEBM** (`.webm`)

**Limite de taille** : 25 MB par fichier

---

## 🌍 Langues Supportées

L'API détecte automatiquement la langue, mais vous pouvez forcer :

```python
# Français
result = engine.transcribe_audio("audio.wav", language="fr")

# Arabe
result = engine.transcribe_audio("audio.wav", language="ar")

# Anglais
result = engine.transcribe_audio("audio.wav", language="en")
```

Plus de 50 langues supportées au total !

---

## 🔧 Configuration Avancée

### Changer la Priorité des Modes

```python
# Forcer le mode API uniquement
engine = STTEngine(use_api=True)

# Forcer le mode local uniquement
engine = STTEngine(use_api=False)
```

### Variables d'Environnement

Fichier `.env` :
```bash
# STT avec Whisper
WHISPER_API_KEY=7fk3Ppa7utGvvHJ7MGUYwV3K24FpxxJh

# Optionnel : Pour cognitive engine avancé
# OPENAI_API_KEY=sk-...
# ANTHROPIC_API_KEY=sk-ant-...
```

---

## ⚡ Performance

### Mode API
- **Latence** : 2-5 secondes (selon taille fichier)
- **Qualité** : Excellente (modèle Whisper-1)
- **Coût** : $0.006 par minute audio

### Mode Local
- **Latence** : Variable (selon modèle et hardware)
- **Qualité** : Bonne à excellente
- **Coût** : Gratuit (après téléchargement du modèle)

### Mode Simulation
- **Latence** : Instantané
- **Qualité** : Prédéfini
- **Coût** : Gratuit

---

## 🐛 Dépannage

### Problème : "Clé API non trouvée"
```bash
# Vérifier que .env existe
cat .env

# Vérifier que python-dotenv est installé
pip install python-dotenv
```

### Problème : "API Whisper error"
- Vérifier la validité de la clé API
- Vérifier la connexion internet
- Le système basculera automatiquement en mode local ou simulation

### Problème : "Invalid audio file"
- Vérifier le format du fichier (WAV, MP3, etc.)
- Vérifier que le fichier n'est pas corrompu
- Taille maximale : 25 MB

---

## 📊 Exemple Complet

```python
from modules.stt_module import STTEngine
from modules.cognitive_engine import CognitiveClaimEngine
from modules.complexity_calculator import ComplexityCalculator

# 1. Transcrire l'audio
stt = STTEngine(use_api=True)
transcript = stt.transcribe_audio("client_appel.wav", language="fr")

print(f"📝 Transcription : {transcript.normalized_transcript}")
print(f"🎭 Émotions : {transcript.emotional_markers}")

# 2. Analyser le sinistre
cognitive = CognitiveClaimEngine()
claim = cognitive.analyze_claim(transcript)

print(f"🔍 Type : {claim.claim_type}")
print(f"📅 Date : {claim.incident_date}")

# 3. Calculer la complexité
calculator = ComplexityCalculator()
complexity = calculator.calculate(claim)

print(f"📊 Score CCI : {complexity.total_cci}/100")
print(f"⚖️ Niveau : {complexity.complexity_level}")
```

---

## 🎉 Prochaines Étapes

1. **Tester** : `python test_whisper_api.py`
2. **Lancer l'app** : `streamlit run app.py`
3. **Enregistrer un sinistre** : Utiliser le microphone ou uploader un fichier
4. **Observer** : La transcription en temps réel avec l'API Whisper

---

## 📞 Support

Pour toute question :
- Consulter [README.md](README.md)
- Consulter [LIVRAISON.md](LIVRAISON.md)
- Exécuter les tests : `python test_system.py`
