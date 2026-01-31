"""
Test de l'intégration Gemini pour analyse cognitive et traduction
"""

import os
from dotenv import load_dotenv
load_dotenv()

def test_gemini_cognitive():
    """Test Gemini pour l'analyse cognitive"""
    print("="*80)
    print("🧪 TEST: Analyse Cognitive avec Gemini")
    print("="*80)
    
    from modules.cognitive_engine import CognitiveClaimEngine
    from models.claim_models import TranscriptMetadata
    
    # Test avec Gemini
    print("\n🔷 Initialisation du moteur cognitif (Gemini)...")
    engine = CognitiveClaimEngine(use_llm=True, llm_provider="gemini")
    
    # Transcription test
    transcript = TranscriptMetadata(
        original_transcript="Bonjour, hier j'ai eu un accident de voiture sur l'autoroute. Un véhicule m'a percuté par l'arrière.",
        normalized_transcript="Bonjour, hier j'ai eu un accident de voiture sur l'autoroute. Un véhicule m'a percuté par l'arrière.",
        language="fr",
        confidence_score=0.95,
        emotional_markers=["inquiet"],
        hesitations=0,
        duration_seconds=5.0
    )
    
    print("\n📝 Transcription:")
    print(f"   {transcript.normalized_transcript}")
    
    print("\n🤖 Analyse avec Gemini...")
    result = engine.analyze_claim(transcript)
    
    print(f"\n📊 Résultat:")
    print(f"   Type: {result.claim_type}")
    print(f"   Faits: {len(result.facts)} identifiés")
    print(f"   Suppositions: {len(result.assumptions)} identifiées")
    
    if result.facts:
        print(f"\n✅ Faits extraits:")
        for fact in result.facts[:3]:
            print(f"   • {fact}")
    
    print("\n" + "="*80)

def test_gemini_translation():
    """Test Gemini pour la traduction Darija"""
    print("\n🧪 TEST: Traduction Darija avec Gemini")
    print("="*80)
    
    from modules.stt_module import STTEngine
    
    engine = STTEngine()
    
    darija_text = "السلام عليكم، الكار ديالي جا واحد ضرب فيا من لور بزاف"
    
    print(f"\n📝 Texte Darija:")
    print(f"   {darija_text}")
    
    print("\n🌐 Traduction avec Gemini...")
    result = engine._process_result(
        text=darija_text,
        lang="ar",
        conf=0.95,
        duration=3.0
    )
    
    print(f"\n✅ Original: {result.original_transcript}")
    print(f"🇫🇷 Traduit: {result.normalized_transcript}")
    
    print("\n" + "="*80)

if __name__ == "__main__":
    print("\n🚀 TESTS D'INTÉGRATION GEMINI")
    print("="*80)
    
    # Vérifier la clé API
    gemini_key = os.getenv("GEMINI_API_KEY")
    if gemini_key:
        print(f"✅ GEMINI_API_KEY configurée: {gemini_key[:20]}...")
    else:
        print("❌ GEMINI_API_KEY non trouvée!")
        exit(1)
    
    try:
        test_gemini_cognitive()
        test_gemini_translation()
        
        print("\n" + "="*80)
        print("✅ TOUS LES TESTS GEMINI RÉUSSIS!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
