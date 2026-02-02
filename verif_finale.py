"""
🎯 Vérification Finale de l'Intégration Émotionnelle
Vérifie que tous les composants sont prêts pour la démo
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import json
from datetime import datetime

def print_section(title):
    """Affiche une section avec style"""
    print("\n" + "=" * 70)
    print(f"  {title}")
    print("=" * 70)

def check_mark(condition, message):
    """Affiche un check ou une croix"""
    symbol = "✅" if condition else "❌"
    print(f"{symbol} {message}")
    return condition

def main():
    """Vérification complète du système"""
    
    print_section("🎭 VÉRIFICATION SYSTÈME ANALYSE ÉMOTIONNELLE")
    
    checks = []
    
    # 1. Vérifier les modules Python
    print("\n📦 MODULES PYTHON")
    print("-" * 70)
    
    try:
        from modules.emotion_analyzer import EmotionAnalyzer
        checks.append(check_mark(True, "emotion_analyzer.py"))
    except:
        checks.append(check_mark(False, "emotion_analyzer.py"))
    
    try:
        from modules.audio_recorder import AudioRecorder
        checks.append(check_mark(True, "audio_recorder.py"))
    except:
        checks.append(check_mark(False, "audio_recorder.py"))
    
    try:
        from modules.emotion_integration import process_audio_with_emotion_analysis
        checks.append(check_mark(True, "emotion_integration.py"))
    except:
        checks.append(check_mark(False, "emotion_integration.py"))
    
    # 2. Vérifier le backend
    print("\n🔧 BACKEND API")
    print("-" * 70)
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / "backend"))
        from routers import emotions
        checks.append(check_mark(True, "backend/routers/emotions.py importable"))
        print(f"   Préfixe router: {emotions.router.prefix}")
        print(f"   Tags: {emotions.router.tags}")
    except Exception as e:
        checks.append(check_mark(False, f"backend/routers/emotions.py: {e}"))
    
    # Vérifier que le backend tourne
    try:
        import requests
        response = requests.get("http://localhost:8000/health", timeout=2)
        if response.status_code == 200:
            checks.append(check_mark(True, "Backend tourne (http://localhost:8000)"))
        else:
            checks.append(check_mark(False, f"Backend répond mais erreur {response.status_code}"))
    except:
        checks.append(check_mark(False, "Backend ne répond pas (http://localhost:8000)"))
        print("   💡 Démarrer avec: cd backend && python -m uvicorn main:app --reload")
    
    # 3. Vérifier les fichiers frontend
    print("\n🎨 FRONTEND NEXT.JS")
    print("-" * 70)
    
    frontend_files = [
        ("frontend-advisor/pages/index.js", "Dashboard principal"),
        ("frontend-advisor/pages/emotions.js", "Page émotions"),
        ("frontend-advisor/components/Navigation.js", "Navigation"),
    ]
    
    for filepath, description in frontend_files:
        path = Path(filepath)
        exists = path.exists()
        checks.append(check_mark(exists, f"{description} ({filepath})"))
        
        if exists and "emotions.js" in filepath:
            content = path.read_text(encoding='utf-8')
            has_fetches = "fetch" in content and "emotions" in content
            checks.append(check_mark(has_fetches, f"  └─ Fetches API émotions"))
    
    # Vérifier que le frontend tourne
    try:
        import requests
        response = requests.get("http://localhost:3001", timeout=2)
        checks.append(check_mark(True, "Frontend tourne (http://localhost:3001)"))
    except:
        checks.append(check_mark(False, "Frontend ne répond pas (http://localhost:3001)"))
        print("   💡 Démarrer avec: cd frontend-advisor && npm run dev")
    
    # 4. Vérifier l'intégration Streamlit
    print("\n🎙️ STREAMLIT APP.PY")
    print("-" * 70)
    
    app_path = Path("app.py")
    if app_path.exists():
        checks.append(check_mark(True, "app.py existe"))
        
        content = app_path.read_text(encoding='utf-8')
        has_import = "emotion_integration" in content
        has_call = "process_audio_with_emotion_analysis" in content
        has_tab = "Analyse Émotionnelle" in content or "render_emotion_tab" in content
        
        checks.append(check_mark(has_import, "  └─ Import emotion_integration"))
        checks.append(check_mark(has_call, "  └─ Appel process_audio_with_emotion_analysis"))
        checks.append(check_mark(has_tab, "  └─ Tab 'Analyse Émotionnelle'"))
    else:
        checks.append(check_mark(False, "app.py introuvable"))
    
    # 5. Vérifier les répertoires de données
    print("\n📁 RÉPERTOIRES DE DONNÉES")
    print("-" * 70)
    
    data_dirs = [
        "data/recordings",
        "data/recordings/client_inputs",
        "data/recordings/advisor_responses",
        "data/recordings/metadata",
        "data/temp_audio"
    ]
    
    for directory in data_dirs:
        path = Path(directory)
        exists = path.exists()
        checks.append(check_mark(exists, f"{directory}"))
        
        if exists and directory == "data/temp_audio":
            emotion_files = list(path.glob("*.emotion.json"))
            checks.append(check_mark(len(emotion_files) > 0, 
                                   f"  └─ {len(emotion_files)} fichier(s) .emotion.json"))
    
    # 6. Vérifier les dépendances Python
    print("\n📚 DÉPENDANCES PYTHON")
    print("-" * 70)
    
    dependencies = [
        ("librosa", "Analyse audio avancée"),
        ("soundfile", "I/O fichiers audio"),
        ("numpy", "Calculs numériques"),
        ("numba", "Accélération librosa"),
    ]
    
    for module, description in dependencies:
        try:
            __import__(module)
            checks.append(check_mark(True, f"{module} - {description}"))
        except:
            checks.append(check_mark(False, f"{module} - {description}"))
            print(f"   💡 Installer avec: pip install {module}")
    
    # Vérifier version numpy
    try:
        import numpy as np
        version = np.__version__
        major = int(version.split('.')[0])
        is_compatible = major < 2
        checks.append(check_mark(is_compatible, 
                                f"  └─ NumPy {version} {'(compatible)' if is_compatible else '(⚠️ incompatible, downgrader)'}"))
        if not is_compatible:
            print('   💡 Downgrader avec: pip install "numpy<2.0"')
    except:
        pass
    
    # 7. Vérifier les fichiers de test
    print("\n🧪 FICHIERS DE TEST")
    print("-" * 70)
    
    test_files = [
        ("test_emotion_system.py", "Tests unitaires"),
        ("test_emotion_integration.py", "Tests intégration"),
        ("demo_emotion_complete.py", "Démonstration complète"),
    ]
    
    for filepath, description in test_files:
        path = Path(filepath)
        checks.append(check_mark(path.exists(), f"{description} ({filepath})"))
    
    # 8. Vérifier la documentation
    print("\n📄 DOCUMENTATION")
    print("-" * 70)
    
    doc_files = [
        ("EMOTION_INTEGRATION.md", "Guide intégration système"),
        ("LIVRAISON_EMOTION.md", "Document de livraison"),
    ]
    
    for filepath, description in doc_files:
        path = Path(filepath)
        checks.append(check_mark(path.exists(), f"{description} ({filepath})"))
    
    # 9. Résumé final
    print_section("📊 RÉSUMÉ")
    
    total = len(checks)
    passed = sum(checks)
    percentage = (passed / total) * 100
    
    print(f"\nVérifications réussies: {passed}/{total} ({percentage:.1f}%)")
    
    if passed == total:
        print("\n" + "🎉" * 25)
        print("\n✅ SYSTÈME 100% OPÉRATIONNEL")
        print("\nTous les composants sont prêts pour la démonstration!")
        print("\n" + "🎉" * 25)
    elif passed >= total * 0.8:
        print("\n⚠️ SYSTÈME PARTIELLEMENT OPÉRATIONNEL")
        print(f"\n{total - passed} problème(s) mineur(s) détecté(s).")
        print("Le système peut fonctionner mais vérifiez les avertissements ci-dessus.")
    else:
        print("\n❌ SYSTÈME NON OPÉRATIONNEL")
        print(f"\n{total - passed} problème(s) majeur(s) détecté(s).")
        print("Corrigez les erreurs avant d'utiliser le système.")
    
    # 10. Prochaines étapes
    print_section("🚀 PROCHAINES ÉTAPES")
    
    if passed < total:
        print("\n1. Corriger les problèmes marqués ❌ ci-dessus")
        print("2. Réexécuter cette vérification: python verif_finale.py")
    else:
        print("\n1. Démarrer les services (si pas déjà fait):")
        print("   Terminal 1: cd backend && python -m uvicorn main:app --reload")
        print("   Terminal 2: cd frontend-advisor && npm run dev")
        print("   Terminal 3: streamlit run app.py")
        print("\n2. Générer des données de démonstration:")
        print("   python demo_emotion_complete.py")
        print("\n3. Tester le système:")
        print("   - Streamlit: http://localhost:8501")
        print("   - Dashboard: http://localhost:3001")
        print("   - API: http://localhost:8000/docs")
        print("\n4. Vérifier l'affichage:")
        print("   - Upload audio dans Streamlit")
        print("   - Voir badge émotionnel + tab détaillé")
        print("   - Ouvrir dashboard web")
        print("   - Voir section émotions en haut")
        print("   - Cliquer 'Voir détails' → page complète")
    
    print("\n" + "=" * 70)
    print(f"⏰ Vérification terminée: {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("=" * 70 + "\n")


if __name__ == "__main__":
    try:
        main()
    except Exception as e:
        print(f"\n❌ ERREUR CRITIQUE: {e}")
        import traceback
        traceback.print_exc()
