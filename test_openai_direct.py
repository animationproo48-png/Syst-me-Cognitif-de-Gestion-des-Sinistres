"""
Test simplifié de traduction avec OpenAI
"""

from dotenv import load_dotenv
load_dotenv()

import os

def test_openai_direct():
    print("="*80)
    print("🧪 TEST: Traduction OpenAI Directe")
    print("="*80)
    
    openai_key = os.getenv("OPENAI_API_KEY")
    print(f"\n📍 Clé OpenAI: {openai_key[:30]}... ({'✅ OK' if openai_key else '❌ MANQUANTE'})")
    
    if not openai_key:
        print("❌ Clé OpenAI manquante!")
        return
    
    try:
        from openai import OpenAI
        client = OpenAI(api_key=openai_key)
        
        text_darija = "الكار ديالي تكسرات بزاف، غادي نخلص التأمين"
        
        print(f"\n📝 Texte Darija:")
        print(f"   {text_darija}")
        
        print("\n🤖 Appel API OpenAI...")
        response = client.chat.completions.create(
            model="gpt-4o-mini",
            messages=[{
                "role": "system",
                "content": "Tu es un expert traducteur Darija marocain vers français. Contexte: déclaration sinistre assurance."
            }, {
                "role": "user",
                "content": f"Traduis ce texte en français:\n{text_darija}"
            }],
            temperature=0.3,
            max_tokens=500
        )
        
        translation = response.choices[0].message.content.strip()
        
        print(f"\n🇫🇷 Traduction OpenAI:")
        print(f"   {translation}")
        
        print("\n" + "="*80)
        print("✅ SUCCÈS: OpenAI fonctionne parfaitement!")
        print("="*80)
        
    except Exception as e:
        print(f"\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    test_openai_direct()
