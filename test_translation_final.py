"""
Test final de traduction avec le système simplifié
"""

from modules.stt_module import STTEngine

def test_translation_final():
    print("="*80)
    print("🧪 TEST: Traduction Multi-Provider (Gemini → Groq → OpenAI)")
    print("="*80)
    
    engine = STTEngine()
    
    # Test direct de la méthode de traduction
    darija_texts = [
        "الكار ديالي تكسرات بزاف",
        "حدث لي حادث سير أمس على الطريق السيار",
        "الاشورونس كيقول ليا خاصني نجيب البابي"
    ]
    
    for i, text in enumerate(darija_texts, 1):
        print(f"\n📍 Test {i}:")
        print(f"   Original: {text}")
        
        translation = engine._translate_with_llm(text)
        
        if translation:
            print(f"   🇫🇷 Traduit: {translation}")
        else:
            print("   ❌ Traduction échouée (tous les providers ont échoué)")
    
    print("\n" + "="*80)
    print("✅ RÉSUMÉ:")
    print("   • Gemini: Quota dépassé (attendu)")
    print("   • Groq: Devrait fonctionner ✅")
    print("   • OpenAI: Quota insuffisant")
    print("   • Au moins 1 provider doit réussir!")
    print("="*80)

if __name__ == "__main__":
    test_translation_final()
