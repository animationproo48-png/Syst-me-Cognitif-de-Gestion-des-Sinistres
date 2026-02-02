"""
Script de test rapide de l'intégration émotionnelle
Vérifie que tous les composants fonctionnent ensemble
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test 1: Vérifier que tous les modules s'importent"""
    print("\n🧪 TEST 1: Imports des modules")
    print("-" * 50)
    
    try:
        from modules.emotion_analyzer import EmotionAnalyzer
        print("✅ emotion_analyzer")
    except Exception as e:
        print(f"❌ emotion_analyzer: {e}")
        return False
    
    try:
        from modules.audio_recorder import AudioRecorder
        print("✅ audio_recorder")
    except Exception as e:
        print(f"❌ audio_recorder: {e}")
        return False
    
    try:
        from modules.emotion_integration import (
            process_audio_with_emotion_analysis,
            format_emotion_for_response,
            get_emotion_label_fr
        )
        print("✅ emotion_integration")
    except Exception as e:
        print(f"❌ emotion_integration: {e}")
        return False
    
    return True


def test_emotion_labels():
    """Test 2: Vérifier les labels français"""
    print("\n🧪 TEST 2: Labels émotionnels français")
    print("-" * 50)
    
    from modules.emotion_integration import get_emotion_label_fr
    
    emotions = ['anger', 'stress', 'sadness', 'fear', 'frustration', 'neutral']
    expected = ['Colère', 'Stress', 'Tristesse', 'Peur', 'Frustration', 'Neutre']
    
    for emotion, expected_label in zip(emotions, expected):
        label = get_emotion_label_fr(emotion)
        if label == expected_label:
            print(f"✅ {emotion} → {label}")
        else:
            print(f"❌ {emotion} → {label} (attendu: {expected_label})")
            return False
    
    return True


def test_emotion_colors():
    """Test 3: Vérifier les couleurs émotionnelles"""
    print("\n🧪 TEST 3: Couleurs émotionnelles")
    print("-" * 50)
    
    from modules.emotion_integration import get_emotion_color
    
    colors = {
        'anger': '#EF4444',
        'stress': '#F59E0B',
        'sadness': '#3B82F6',
        'fear': '#8B5CF6',
        'frustration': '#EC4899',
        'neutral': '#6B7280'
    }
    
    for emotion, expected_color in colors.items():
        color = get_emotion_color(emotion)
        if color == expected_color:
            print(f"✅ {emotion} → {color}")
        else:
            print(f"❌ {emotion} → {color} (attendu: {expected_color})")
            return False
    
    return True


def test_alert_levels():
    """Test 4: Vérifier les niveaux d'alerte"""
    print("\n🧪 TEST 4: Niveaux d'alerte")
    print("-" * 50)
    
    from modules.emotion_integration import get_alert_level
    
    test_cases = [
        ('anger', 90, 'critical'),
        ('anger', 80, 'high'),
        ('stress', 80, 'high'),
        ('sadness', 75, 'medium'),
        ('fear', 75, 'medium'),
        ('neutral', 50, 'none'),
    ]
    
    for emotion, confidence, expected_level in test_cases:
        level = get_alert_level(emotion, confidence)
        if level == expected_level:
            print(f"✅ {emotion} ({confidence}%) → {level}")
        else:
            print(f"❌ {emotion} ({confidence}%) → {level} (attendu: {expected_level})")
            return False
    
    return True


def test_response_formatting():
    """Test 5: Vérifier le formatage des réponses"""
    print("\n🧪 TEST 5: Formatage des réponses empathiques")
    print("-" * 50)
    
    from modules.emotion_integration import format_emotion_for_response
    
    # Test avec colère forte
    emotion_data = {
        'dominant_emotion': {'label': 'anger', 'confidence': 85},
        'fused_scores': {},
        'alert_level': 'high'
    }
    
    prefix = format_emotion_for_response(emotion_data)
    if "frustration" in prefix.lower() or "comprends" in prefix.lower():
        print(f"✅ Colère (85%): Préfixe empathique généré")
        print(f"   → {prefix[:80]}...")
    else:
        print(f"❌ Colère (85%): Pas de préfixe")
        return False
    
    # Test avec émotion faible (pas de préfixe attendu)
    emotion_data['dominant_emotion']['confidence'] = 40
    prefix = format_emotion_for_response(emotion_data)
    if prefix == "":
        print(f"✅ Colère (40%): Pas de préfixe (normal)")
    else:
        print(f"❌ Colère (40%): Préfixe inattendu")
        return False
    
    return True


def test_data_directories():
    """Test 6: Vérifier les répertoires de données"""
    print("\n🧪 TEST 6: Répertoires de données")
    print("-" * 50)
    
    directories = [
        Path("data/recordings"),
        Path("data/recordings/client_inputs"),
        Path("data/recordings/advisor_responses"),
        Path("data/recordings/metadata"),
        Path("data/temp_audio")
    ]
    
    for directory in directories:
        if directory.exists():
            print(f"✅ {directory}")
        else:
            print(f"⚠️ {directory} (sera créé automatiquement)")
    
    return True


def test_emotion_files():
    """Test 7: Vérifier les fichiers d'analyse existants"""
    print("\n🧪 TEST 7: Fichiers d'analyse émotionnelle")
    print("-" * 50)
    
    temp_audio = Path("data/temp_audio")
    if temp_audio.exists():
        emotion_files = list(temp_audio.glob("*.emotion.json"))
        print(f"✅ Trouvé {len(emotion_files)} fichiers .emotion.json")
        
        if emotion_files:
            import json
            latest = sorted(emotion_files, key=lambda p: p.stat().st_mtime)[-1]
            print(f"   Dernier: {latest.name}")
            
            with open(latest, 'r', encoding='utf-8') as f:
                data = json.load(f)
                emotion = data.get('dominant_emotion', {}).get('label', 'unknown')
                confidence = data.get('dominant_emotion', {}).get('confidence', 0)
                print(f"   Émotion: {emotion} ({confidence:.1f}%)")
    else:
        print(f"⚠️ Répertoire {temp_audio} introuvable")
    
    return True


def test_backend_router():
    """Test 8: Vérifier que le router backend s'importe"""
    print("\n🧪 TEST 8: Router backend")
    print("-" * 50)
    
    try:
        sys.path.insert(0, str(Path(__file__).parent / "backend"))
        from routers import emotions
        print(f"✅ Router emotions importé")
        print(f"   Préfixe: {emotions.router.prefix}")
        print(f"   Tags: {emotions.router.tags}")
        return True
    except Exception as e:
        print(f"❌ Erreur import router: {e}")
        return False


def main():
    """Exécuter tous les tests"""
    print("\n" + "=" * 50)
    print("🎭 TEST D'INTÉGRATION ÉMOTIONNELLE")
    print("=" * 50)
    
    tests = [
        test_imports,
        test_emotion_labels,
        test_emotion_colors,
        test_alert_levels,
        test_response_formatting,
        test_data_directories,
        test_emotion_files,
        test_backend_router
    ]
    
    results = []
    for test in tests:
        try:
            result = test()
            results.append(result)
        except Exception as e:
            print(f"\n❌ ERREUR CRITIQUE: {e}")
            import traceback
            traceback.print_exc()
            results.append(False)
    
    print("\n" + "=" * 50)
    print("📊 RÉSULTATS")
    print("=" * 50)
    passed = sum(results)
    total = len(results)
    print(f"Tests réussis: {passed}/{total}")
    
    if passed == total:
        print("\n✅ TOUS LES TESTS RÉUSSIS!")
        print("Le système d'analyse émotionnelle est prêt à l'emploi.")
    else:
        print(f"\n⚠️ {total - passed} test(s) échoué(s)")
        print("Vérifiez les erreurs ci-dessus.")
    
    print("\n" + "=" * 50)
    print("🚀 PROCHAINES ÉTAPES")
    print("=" * 50)
    print("1. Démarrer le backend: cd backend && python -m uvicorn main:app --reload")
    print("2. Démarrer le frontend: cd frontend-advisor && npm run dev")
    print("3. Lancer Streamlit: streamlit run app.py")
    print("4. Tester avec un audio client dans l'interface Streamlit")
    print("5. Vérifier l'affichage dans le dashboard web: http://localhost:3001")


if __name__ == "__main__":
    main()
