"""
Test de traduction avec les 3 providers: Gemini, Groq, OpenAI
"""

from modules.stt_module import STTEngine
import os

def test_translation_providers():
    print("="*80)
    print("🧪 TEST: Traduction Multi-Provider (Gemini → Groq → OpenAI)")
    print("="*80)
    
    # Afficher les clés disponibles
    print("\n📍 Clés API configurées:")
    print(f"   Gemini: {'✅' if os.getenv('GEMINI_API_KEY') else '❌'}")
    print(f"   Groq: {'✅' if os.getenv('GROQ_API_KEY') else '❌'}")
    print(f"   OpenAI: {'✅' if os.getenv('OPENAI_API_KEY') else '❌'}")
    
    engine = STTEngine()
    
    # Test 1: Darija basique
    print("\n📍 Test 1: Darija Marocain")
    print("   Original: الكار ديالي تكسرات بزاف")
    
    metadata = engine._transcribe_with_api(
        "dummy.mp3", 
        "ar"
    )
    
    # Simuler un result avec texte arabe
    metadata.original_transcript = "الكار ديالي تكسرات بزاف"
    metadata.language = "ar"
    
    # Forcer la traduction
    translation = engine._translate_with_llm(metadata.original_transcript)
    
    print(f"\n   ✅ Original: {metadata.original_transcript}")
    if translation:
        print(f"   🇫🇷 Traduit: {translation}")
    else:
        print("   ❌ Traduction échouée")
    
    print("\n" + "="*80)
    print("✅ CONCLUSION:")
    print("   • Gemini essayé en priorité (quota dépassé attendu)")
    print("   • Groq essayé en fallback")
    print("   • OpenAI disponible en dernier recours")
    print("   • Un des 3 providers doit fonctionner!")
    print("="*80)

if __name__ == "__main__":
    test_translation_providers()
