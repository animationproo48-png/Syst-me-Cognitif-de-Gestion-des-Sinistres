"""
Script de validation rapide du système.
Teste tous les modules sans lancer l'interface.
"""

import sys
from pathlib import Path

# Setup path
sys.path.insert(0, str(Path(__file__).parent))

def test_imports():
    """Test 1: Vérifier que tous les modules s'importent"""
    print("\n🔍 Test 1: Imports des modules...")
    
    try:
        from models.claim_models import (
            ClaimDigitalTwin, ClaimType, ClaimState, 
            TranscriptMetadata, ComplexityBreakdown
        )
        print("   ✅ Models OK")
        
        from modules.stt_module import STTEngine
        print("   ✅ STT Module OK")
        
        from modules.tts_module import TTSEngine
        print("   ✅ TTS Module OK")
        
        from modules.cognitive_engine import CognitiveClaimEngine
        print("   ✅ Cognitive Engine OK")
        
        from modules.complexity_calculator import ComplexityCalculator
        print("   ✅ Complexity Calculator OK")
        
        from modules.decision_engine import DecisionEngine
        print("   ✅ Decision Engine OK")
        
        from modules.summary_generator import SummaryGenerator
        print("   ✅ Summary Generator OK")
        
        from modules.crm_system import ClaimCRM
        print("   ✅ CRM System OK")
        
        return True
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False


def test_stt_module():
    """Test 2: Module STT"""
    print("\n🔍 Test 2: Module STT...")
    
    try:
        from modules.stt_module import STTEngine
        
        engine = STTEngine()
        
        # Test simulation (sans fichier audio)
        metadata = engine._simulate_transcription("test.wav", "fr")
        
        assert metadata.language == "fr"
        assert len(metadata.original_transcript) > 0
        assert metadata.confidence_score > 0
        
        print("   ✅ STT fonctionne (mode simulation)")
        return True
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        return False


def test_cognitive_engine():
    """Test 3: Moteur cognitif"""
    print("\n🔍 Test 3: Moteur Cognitif...")
    
    try:
        from modules.cognitive_engine import CognitiveClaimEngine
        from models.claim_models import TranscriptMetadata
        
        transcript = "J'ai eu un accident de voiture hier sur l'autoroute A1."
        
        metadata = TranscriptMetadata(
            original_transcript=transcript,
            normalized_transcript=transcript,
            language="fr",
            confidence_score=0.9,
            emotional_markers=[],
            hesitations=0
        )
        
        engine = CognitiveClaimEngine(use_llm=False)
        structure = engine.analyze_claim(metadata)
        
        assert structure.claim_type is not None
        assert structure.claim_type_confidence > 0
        
        print(f"   ✅ Type détecté: {structure.claim_type.value}")
        print(f"   ✅ Confiance: {structure.claim_type_confidence*100:.0f}%")
        return True
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def test_complexity_calculator():
    """Test 4: Calculateur de complexité"""
    print("\n🔍 Test 4: Calculateur de Complexité...")
    
    try:
        from modules.complexity_calculator import ComplexityCalculator
        from modules.cognitive_engine import CognitiveClaimEngine
        from models.claim_models import TranscriptMetadata
        
        transcript = "Accident avec plusieurs voitures, je ne sais pas exactement quand."
        
        metadata = TranscriptMetadata(
            original_transcript=transcript,
            normalized_transcript=transcript,
            language="fr",
            confidence_score=0.8,
            emotional_markers=["confusion"],
            hesitations=2
        )
        
        cognitive_engine = CognitiveClaimEngine(use_llm=False)
        structure = cognitive_engine.analyze_claim(metadata)
        
        calc = ComplexityCalculator()
        complexity = calc.calculate(structure)
        
        assert 0 <= complexity.total_score <= 100
        assert complexity.level is not None
        
        print(f"   ✅ Score: {complexity.total_score:.1f}/100")
        print(f"   ✅ Niveau: {complexity.level.value}")
        return True
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def test_decision_engine():
    """Test 5: Moteur de décision"""
    print("\n🔍 Test 5: Moteur de Décision...")
    
    try:
        from modules.decision_engine import DecisionEngine
        from modules.complexity_calculator import ComplexityCalculator
        from modules.cognitive_engine import CognitiveClaimEngine
        from models.claim_models import TranscriptMetadata, ClaimDigitalTwin, ClaimState
        import uuid
        from datetime import datetime
        
        # Créer un cas simple
        metadata = TranscriptMetadata(
            original_transcript="Accident simple avec constat.",
            normalized_transcript="Accident simple avec constat.",
            language="fr",
            confidence_score=0.95,
            emotional_markers=[],
            hesitations=0
        )
        
        cognitive_engine = CognitiveClaimEngine(use_llm=False)
        structure = cognitive_engine.analyze_claim(metadata)
        
        calc = ComplexityCalculator()
        complexity = calc.calculate(structure)
        
        claim_id = f"TEST-{uuid.uuid4().hex[:6]}"
        digital_twin = ClaimDigitalTwin(
            claim_id=claim_id,
            transcript_metadata=metadata,
            cognitive_structure=structure,
            complexity=complexity,
            current_state=ClaimState.ANALYZING
        )
        
        decision_engine = DecisionEngine()
        should_escalate, reason, action = decision_engine.make_decision(digital_twin)
        
        print(f"   ✅ Décision: {'Escalade' if should_escalate else 'Autonome'}")
        print(f"   ✅ Raison: {reason[:50]}...")
        return True
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def test_crm_system():
    """Test 6: Système CRM"""
    print("\n🔍 Test 6: Système CRM...")
    
    try:
        from modules.crm_system import ClaimCRM
        from models.claim_models import ClaimDigitalTwin, ClaimState
        import uuid
        from datetime import datetime
        
        # Créer un CRM temporaire
        crm = ClaimCRM(db_path=":memory:")
        
        # Créer un sinistre test
        claim_id = f"TEST-{uuid.uuid4().hex[:6]}"
        digital_twin = ClaimDigitalTwin(
            claim_id=claim_id,
            current_state=ClaimState.RECEIVED
        )
        
        # Test création
        success = crm.create_claim(digital_twin)
        assert success, "Échec création sinistre"
        
        # Test récupération
        retrieved = crm.get_claim(claim_id)
        assert retrieved is not None, "Échec récupération sinistre"
        assert retrieved.claim_id == claim_id
        
        # Test statistiques
        stats = crm.get_statistics()
        assert stats["total_claims"] >= 1
        
        print(f"   ✅ CRM opérationnel")
        print(f"   ✅ Sinistre créé: {claim_id}")
        print(f"   ✅ Statistiques: {stats['total_claims']} sinistres")
        
        crm.close()
        return True
    except Exception as e:
        print(f"   ❌ Erreur: {e}")
        import traceback
        print(traceback.format_exc())
        return False


def main():
    """Execute tous les tests"""
    print("="*80)
    print("🧪 VALIDATION SYSTÈME - Tests Automatiques")
    print("="*80)
    
    tests = [
        ("Imports", test_imports),
        ("STT Module", test_stt_module),
        ("Cognitive Engine", test_cognitive_engine),
        ("Complexity Calculator", test_complexity_calculator),
        ("Decision Engine", test_decision_engine),
        ("CRM System", test_crm_system)
    ]
    
    results = []
    
    for test_name, test_func in tests:
        try:
            result = test_func()
            results.append((test_name, result))
        except Exception as e:
            print(f"\n❌ Test '{test_name}' a crashé: {e}")
            results.append((test_name, False))
    
    # Résumé
    print("\n" + "="*80)
    print("📊 RÉSUMÉ DES TESTS")
    print("="*80)
    
    passed = sum(1 for _, result in results if result)
    total = len(results)
    
    for test_name, result in results:
        status = "✅ PASS" if result else "❌ FAIL"
        print(f"{status} - {test_name}")
    
    print("\n" + "="*80)
    print(f"Résultat: {passed}/{total} tests réussis ({passed/total*100:.0f}%)")
    print("="*80)
    
    if passed == total:
        print("\n🎉 Tous les tests sont passés! Système prêt pour la démo.")
        print("👉 Lancez: streamlit run app.py")
        return 0
    else:
        print(f"\n⚠️ {total - passed} test(s) échoué(s). Vérifiez les erreurs ci-dessus.")
        return 1


if __name__ == "__main__":
    exit(main())
