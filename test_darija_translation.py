"""
Test de la transcription Darija avec traduction automatique via Groq
"""

from modules.stt_module import STTEngine

def test_darija_translation():
    """Test la traduction automatique du Darija vers le français"""
    print("="*80)
    print("🧪 TEST: Traduction Darija → Français via Groq LLM")
    print("="*80)
    
    engine = STTEngine()
    
    # Simulation d'une transcription Darija
    darija_text = "الكار ديالي جا واحد ضرب فيا من لور. كانت كاتجي بزاف وماوقفاتش."
    
    print(f"\n📝 Texte Darija original:")
    print(f"   {darija_text}")
    
    # Test de la traduction
    result = engine._process_result(
        text=darija_text,
        lang="ar",
        conf=0.95,
        duration=5.0
    )
    
    print(f"\n🌐 Transcription originale:")
    print(f"   {result.original_transcript}")
    
    print(f"\n🇫🇷 Traduction française (normalized_transcript):")
    print(f"   {result.normalized_transcript}")
    
    print(f"\n📊 Métadonnées:")
    print(f"   Langue: {result.language}")
    print(f"   Confiance: {result.confidence_score}")
    print(f"   Durée: {result.duration_seconds}s")
    
    print("\n" + "="*80)
    
    if result.normalized_transcript != darija_text:
        print("✅ SUCCÈS: Traduction automatique activée!")
        print(f"   Original: {darija_text[:50]}...")
        print(f"   Traduit: {result.normalized_transcript[:50]}...")
    else:
        print("⚠️ ATTENTION: Traduction non activée (vérifier GROQ_API_KEY)")
    
    print("="*80)

if __name__ == "__main__":
    test_darija_translation()
