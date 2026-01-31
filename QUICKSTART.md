# 🚀 Guide de Démarrage Rapide

## Installation en 3 Minutes

### 1️⃣ Installer les dépendances

```powershell
# Ouvrir PowerShell dans le dossier du projet
cd "c:\Users\HP\Inssurance Advanced"

# Créer environnement virtuel (recommandé)
python -m venv venv
.\venv\Scripts\activate

# Installer les packages
pip install -r requirements.txt
```

### 2️⃣ Tester le système (CLI)

```powershell
# Exécuter la démonstration CLI
python demo.py
```

Cela va:
- ✅ Traiter 2 sinistres de test (simple + complexe)
- ✅ Afficher l'analyse cognitive complète
- ✅ Créer la base de données CRM
- ✅ Valider que tout fonctionne

### 3️⃣ Lancer l'interface web

```powershell
# Démarrer Streamlit
streamlit run app.py
```

L'interface s'ouvre automatiquement sur `http://localhost:8501`

---

## 🎯 Premiers Pas dans l'Interface

### Scénario 1: Tester avec du texte simulé

1. Aller dans **🎙️ Nouvelle Déclaration**
2. Choisir mode **📝 Texte simulé (démo)**
3. Sélectionner un exemple pré-rempli
4. Cliquer sur **🚀 Analyser**
5. Observer le traitement en temps réel

### Scénario 2: Upload audio

1. Préparer un fichier audio (MP3, WAV)
2. Aller dans **📁 Upload fichier audio**
3. Sélectionner le fichier
4. Cliquer sur **🚀 Analyser**

### Scénario 3: Consulter le CRM

1. Aller dans **📋 Tableau de Bord CRM**
2. Voir tous les sinistres traités
3. Filtrer par état / escalade
4. Cliquer sur un sinistre pour détails

---

## 🔧 Configuration Optionnelle

### Activer le LLM (OpenAI GPT-4)

```powershell
# Créer fichier .env
copy .env.example .env

# Éditer .env et ajouter votre clé
# OPENAI_API_KEY=sk-...
```

Puis dans `app.py`, modifier:
```python
cognitive_engine = CognitiveClaimEngine(use_llm=True)  # Active GPT-4
```

### Installer Whisper pour vraie transcription

```powershell
# Installer FFmpeg (requis par Whisper)
# Télécharger depuis: https://ffmpeg.org/download.html

# Installer Whisper
pip install openai-whisper

# Plus besoin de rien, c'est automatique!
```

---

## ⚡ Résolution Problèmes Courants

### Erreur: Module not found

```powershell
# Vérifier que venv est activé
.\venv\Scripts\activate

# Réinstaller
pip install -r requirements.txt
```

### Erreur: Port déjà utilisé

```powershell
# Utiliser un autre port
streamlit run app.py --server.port 8502
```

### Base de données verrouillée

```powershell
# Supprimer et recréer
del data\claims_crm.db
python demo.py
```

---

## 📚 Prochaines Étapes

1. ✅ Tester les 3 exemples de déclarations
2. ✅ Observer les différents niveaux de complexité
3. ✅ Comparer les résumés Client vs Conseiller
4. ✅ Analyser les décisions d'escalade
5. ✅ Explorer les statistiques CRM

---

## 🎓 Ressources

- **README.md** - Documentation complète
- **demo.py** - Code source des démonstrations
- **app.py** - Code interface Streamlit
- **modules/** - Tous les moteurs cognitifs

---

## 🆘 Support

Si problème:
1. Vérifier Python version: `python --version` (doit être 3.10+)
2. Vérifier packages: `pip list`
3. Relancer: `python demo.py` pour tester CLI d'abord

**Tout fonctionne?** 🎉  
→ Prêt pour la démo hackathon!
