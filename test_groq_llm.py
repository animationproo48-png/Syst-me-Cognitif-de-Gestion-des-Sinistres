"""
Test de l'intégration Groq LLM pour l'analyse cognitive
"""

import os
from dotenv import load_dotenv
from groq import Groq

print("=" * 70)
print("🧪 TEST GROQ LLM - ANALYSE COGNITIVE")
print("=" * 70)

# Charger la clé API
load_dotenv()
api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    print("❌ GROQ_API_KEY non trouvée dans .env")
    exit(1)

print(f"✅ Clé API trouvée: {api_key[:20]}...")

# Initialiser le client Groq
try:
    client = Groq(api_key=api_key)
    print("✅ Client Groq initialisé")
except Exception as e:
    print(f"❌ Erreur d'initialisation: {e}")
    exit(1)

# Test 1: Analyse simple d'un sinistre
print("\n" + "-" * 70)
print("TEST 1: Analyse d'un sinistre automobile")
print("-" * 70)

texte_sinistre = """
Bonjour, je vous appelle pour déclarer un accident de voiture.
C'était hier vers 18h30 sur l'autoroute A1 près de Lille.
Un autre véhicule m'a percuté à l'arrière alors que j'étais à l'arrêt.
Mon pare-choc est complètement enfoncé et le coffre ne ferme plus.
L'autre conducteur a reconnu sa responsabilité et on a rempli un constat amiable.
J'ai pris des photos des dégâts.
"""

prompt = f"""Analyse ce sinistre d'assurance et extrait les informations structurées au format JSON.

Texte: {texte_sinistre}

Retourne un JSON avec:
- type_sinistre (automobile, habitation, santé, etc.)
- date_incident (format ISO ou null)
- lieu (description du lieu)
- dommages (liste des dommages mentionnés)
- tiers_impliques (nombre de tiers)
- documents_mentionnes (liste)
- faits_verifies (liste des faits avérés)
- suppositions (liste des suppositions)

Réponds UNIQUEMENT avec le JSON, sans texte avant ou après."""

try:
    print("🌐 Envoi de la requête à Groq...")
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",  # Modèle rapide et performant
        messages=[
            {
                "role": "system",
                "content": "Tu es un expert en analyse de sinistres d'assurance. Extrais les informations de manière structurée."
            },
            {
                "role": "user",
                "content": prompt
            }
        ],
        temperature=0.1,
        max_tokens=1000
    )
    
    resultat = response.choices[0].message.content
    
    print("✅ Réponse reçue de Groq!")
    print("\n📊 RÉSULTAT D'ANALYSE:")
    print(resultat)
    
    # Vérifier que c'est du JSON valide
    import json
    try:
        data = json.loads(resultat)
        print("\n✅ JSON valide!")
        print(f"   Type: {data.get('type_sinistre')}")
        print(f"   Lieu: {data.get('lieu')}")
        print(f"   Dommages: {len(data.get('dommages', []))} éléments")
        print(f"   Faits: {len(data.get('faits_verifies', []))} éléments")
    except json.JSONDecodeError:
        print("⚠️ La réponse n'est pas du JSON valide")
        
except Exception as e:
    print(f"❌ Erreur lors de l'appel Groq: {e}")
    exit(1)

# Test 2: Analyse avec darija
print("\n" + "-" * 70)
print("TEST 2: Analyse d'un texte en darija marocain")
print("-" * 70)

texte_darija = """
سير كنت ماشي ف الطوموبيل ديالي و واحد الكار جا ضرب فيا من لور
كاين الكسيدة كبيرة و الباروكاس ولا ما كيتسدش
الآخر قال ليا سماحليا غير نديروا لكونستا
"""

prompt_darija = f"""Analyse ce texte en darija marocain (dialecte marocain) sur un sinistre automobile.

Texte: {texte_darija}

Extrais les informations principales en français au format JSON:
- type_sinistre
- resume_francais (résumé en français)
- dommages_decrits
- tiers_reconnait_responsabilite (oui/non)

Réponds en JSON."""

try:
    print("🌐 Envoi de la requête darija à Groq...")
    
    response = client.chat.completions.create(
        model="llama-3.3-70b-versatile",
        messages=[
            {
                "role": "system",
                "content": "Tu es expert en darija marocain et en analyse d'assurance. Tu comprends le dialecte marocain."
            },
            {
                "role": "user",
                "content": prompt_darija
            }
        ],
        temperature=0.1,
        max_tokens=500
    )
    
    resultat = response.choices[0].message.content
    print("✅ Réponse reçue!")
    print("\n📊 ANALYSE DARIJA:")
    print(resultat)
    
except Exception as e:
    print(f"❌ Erreur: {e}")

print("\n" + "=" * 70)
print("✅ Tests Groq terminés!")
print("=" * 70)
print("\n💡 Utilisation dans le système:")
print("   from modules.cognitive_engine import CognitiveClaimEngine")
print("   engine = CognitiveClaimEngine(use_llm=True, llm_provider='groq')")
print("   result = engine.analyze_claim(transcript)")
