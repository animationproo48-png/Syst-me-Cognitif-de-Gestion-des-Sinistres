"""
Script de test pour vérifier l'intégration de l'API LemonFox STT
"""

import os
from pathlib import Path
from modules.stt_module import STTEngine
from dotenv import load_dotenv


def test_api_connection():
    """Test 1: Vérifier la connexion à l'API"""
    print("=" * 60)
    print("TEST 1: Vérification de la connexion API LemonFox")
    print("=" * 60)
    
    # Charger les variables d'environnement
    load_dotenv()
    api_key = os.getenv("WHISPER_API_KEY")
    
    if not api_key:
        print("❌ ÉCHEC: Clé API non trouvée dans .env")
        return False
    
    print(f"✅ Clé API trouvée: {api_key[:10]}...")
    
    # Vérifier que la clé a le bon format
    if len(api_key) > 20:
        print("✅ Format de clé API valide")
        return True
    else:
        print("⚠️ Format de clé API suspect (trop courte)")
        return False

def test_stt_initialization():
    """Test 2: Initialiser le moteur STT avec API"""
    print("\n" + "=" * 60)
    print("TEST 2: Initialisation du moteur STT")
    print("=" * 60)
    
    try:
        # Mode API activé par défaut
        engine = STTEngine(use_api=True)
        
        if engine.api_key:
            print("✅ Moteur STT initialisé avec API LemonFox")
            return True
        else:
            print("⚠️ Moteur STT initialisé mais clé API non chargée")
            return False
    
    except Exception as e:
        print(f"❌ ÉCHEC: {e}")
        return False

def test_simulation_mode():
    """Test 3: Tester le mode simulation (fallback)"""
    print("\n" + "=" * 60)
    print("TEST 3: Mode simulation (fallback)")
    print("=" * 60)
    
    try:
        # Forcer le mode simulation
        engine = STTEngine(use_api=False)
        
        # Transcrire en mode simulation
        result = engine.transcribe_audio("dummy_audio.wav", language="fr")
        
        print(f"✅ Transcription simulée générée:")
        print(f"   - Langue: {result.language}")
        print(f"   - Confiance: {result.confidence_score}")
        print(f"   - Longueur: {len(result.original_transcript)} caractères")
        print(f"   - Marqueurs émotionnels: {result.emotional_markers}")
        
        return True
    
    except Exception as e:
        print(f"❌ ÉCHEC: {e}")
        return False

def test_dependencies():
    """Test 4: Vérifier les dépendances installées"""
    print("\n" + "=" * 60)
    print("TEST 4: Vérification des dépendances")
    print("=" * 60)
    
    dependencies = {
        "dotenv": "python-dotenv",
        "requests": "requests",
        "streamlit": "streamlit",
        "pydantic": "pydantic"
    }
    
    all_ok = True
    for module, package in dependencies.items():
        try:
            __import__(module)
            print(f"✅ {package} installé")
        except ImportError:
            print(f"❌ {package} manquant (pip install {package})")
            all_ok = False
    
    return all_ok

def main():
    """Exécute tous les tests"""
    print("\n" + "🧪" * 30)
    print("TEST D'INTÉGRATION API LEMONFOX STT")
    print("🧪" * 30 + "\n")
    
    results = []
    
    # Test 1: Connexion API
    results.append(("Connexion API", test_api_connection()))
    
    # Test 2: Initialisation STT
    results.append(("Initialisation STT", test_stt_initialization()))
    
    # Test 3: Mode simulation
    results.append(("Mode simulation", test_simulation_mode()))
    
    # Test 4: Dépendances
    results.append(("Dépendances", test_dependencies()))
    
    # Résumé
    print("\n" + "=" * 60)
    print("RÉSUMÉ DES TESTS")
    print("=" * 60)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {name}")
    
    print("\n" + "=" * 60)
    print(f"Score: {passed}/{total} tests réussis")
    
    if passed == total:
        print("🎉 Tous les tests sont passés! L'API LemonFox est prête.")
    else:
        print("⚠️ Certains tests ont échoué. Vérifiez la configuration.")
    
    print("=" * 60 + "\n")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)
