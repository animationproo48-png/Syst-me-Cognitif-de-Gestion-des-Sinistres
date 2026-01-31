# 🎙️ DÉMARRAGE ULTRA-RAPIDE

## ⚡ En 30 Secondes

```powershell
# Dans PowerShell (dossier du projet)

# Installation (1ère fois seulement)
python -m venv venv
.\venv\Scripts\activate
pip install -r requirements.txt

# Vérification API Whisper (optionnel)
python test_whisper_api.py

# Lancement
streamlit run app.py
```

**Ça ouvre automatiquement sur http://localhost:8501**

---

## 🎯 Test Rapide

1. Cliquer **"🎙️ Nouvelle Déclaration"**
2. Choisir **"🎤 Enregistrement audio"** (API Whisper activée) ou **"📝 Texte simulé"**
3. Parler/Écrire votre sinistre
4. Cliquer **"🚀 Traiter la déclaration"**
5. Observer le traitement complet avec transcription temps réel

---

## 📚 Documentation Complète

- **LIVRAISON.md** ← Commencer ici (tout détaillé)
- **README.md** ← Documentation technique complète
- **QUICKSTART.md** ← Guide pas-à-pas
- **PRESENTATION_HACKATHON.md** ← Pour le jury

---

## ✅ Tests Validation

```powershell
# Vérifier que tout fonctionne
python test_system.py

# Tester l'intégration API Whisper
python test_whisper_api.py

# Résultat attendu: Tous tests PASS ✅
```

---

## 🎬 Démo CLI Alternative

```powershell
# Sans interface graphique
python demo.py

# Traite 2 sinistres en CLI
```

---

**🚀 C'est tout! Le système est prêt.**

En cas de problème: voir LIVRAISON.md section "Support"
