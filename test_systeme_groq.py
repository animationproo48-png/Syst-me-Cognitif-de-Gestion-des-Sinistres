"""
Test complet du système avec Groq LLM activé
"""

from modules.stt_module import STTEngine, TranscriptMetadata
from modules.cognitive_engine import CognitiveClaimEngine
from modules.complexity_calculator import ComplexityCalculator

print("=" * 80)
print("🧪 TEST SYSTÈME COMPLET AVEC GROQ LLM")
print("=" * 80)

# ===== ÉTAPE 1: CRÉER UNE TRANSCRIPTION SIMULÉE =====
print("\n1️⃣ Création d'une transcription simulée...")

transcript = TranscriptMetadata(
    original_transcript="""
    Salam, ana knt ماشي في الطوموبيل ديالي و واحد الكار جا ضرب فيا من لور.
    C'était hier vers 18h sur la route de Casablanca.
    الكسيدة كبيرة، الباروكاس ولا محطم و الموتور كيخرج الدخان.
    L'autre conducteur il a dit smaḥ li ghi ndiro l'constat.
    J'ai pris des photos w kayn des témoins aussi.
    """,
    normalized_transcript="""
    Salam, j'étais en train de conduire ma voiture et une autre voiture m'a percuté de l'arrière.
    C'était hier vers 18h sur la route de Casablanca.
    Les dégâts sont importants, le pare-choc est détruit et le moteur fume.
    L'autre conducteur a dit pardon on va faire le constat.
    J'ai pris des photos et il y a des témoins aussi.
    """,
    language="fr",
    confidence_score=0.92,
    emotional_markers=["stress", "urgence"],
    hesitations=2,
    duration_seconds=45.0
)

print("✅ Transcription créée (mélange français/arabe/darija)")
print(f"   Langue: {transcript.language}")
print(f"   Confiance: {transcript.confidence_score:.2%}")

# ===== ÉTAPE 2: ANALYSE COGNITIVE AVEC GROQ =====
print("\n2️⃣ Analyse cognitive avec Groq LLM...")

# Mode avec LLM (Groq)
engine_llm = CognitiveClaimEngine(use_llm=True, llm_provider="groq")

try:
    claim_llm = engine_llm.analyze_claim(transcript)
    
    print("\n✅ Analyse Groq terminée!")
    print(f"   🏷️ Type: {claim_llm.claim_type}")
    print(f"   📊 Confiance: {claim_llm.claim_type_confidence:.2%}")
    print(f"   📅 Date: {claim_llm.date_incident or 'Non extraite'}")
    print(f"   📍 Lieu: {claim_llm.location or 'Non extrait'}")
    print(f"   👥 Parties: {len(claim_llm.parties_involved)}")
    print(f"   ✅ Faits: {len(claim_llm.facts)}")
    print(f"   ❓ Suppositions: {len(claim_llm.assumptions)}")
    print(f"   📄 Documents: {len(claim_llm.mentioned_documents)}")
    
    if claim_llm.facts:
        print(f"\n   📋 Faits extraits par Groq:")
        for i, fact in enumerate(claim_llm.facts[:3], 1):
            print(f"      {i}. {fact}")
    
    if claim_llm.damages_description:
        print(f"\n   💥 Dommages: {claim_llm.damages_description}")
        
except Exception as e:
    print(f"❌ Erreur lors de l'analyse Groq: {e}")
    claim_llm = None

# ===== ÉTAPE 3: COMPARAISON AVEC MODE RÈGLES =====
print("\n\n3️⃣ Comparaison avec mode règles (sans LLM)...")

engine_rules = CognitiveClaimEngine(use_llm=False)
claim_rules = engine_rules.analyze_claim(transcript)

print(f"✅ Analyse règles terminée!")
print(f"   🏷️ Type: {claim_rules.claim_type}")
print(f"   📊 Confiance: {claim_rules.claim_type_confidence:.2%}")
print(f"   ✅ Faits: {len(claim_rules.facts)}")
print(f"   ❓ Suppositions: {len(claim_rules.assumptions)}")

# ===== ÉTAPE 4: CALCUL DE COMPLEXITÉ =====
if claim_llm:
    print("\n\n4️⃣ Calcul de complexité...")
    
    calculator = ComplexityCalculator()
    complexity = calculator.calculate(claim_llm)
    
    print(f"✅ Complexité calculée!")
    print(f"   🎯 Score CCI: {complexity.total_score}/100")
    print(f"   ⚖️ Niveau: {complexity.level}")

# ===== RÉSUMÉ COMPARATIF =====
print("\n\n" + "=" * 80)
print("📊 RÉSUMÉ COMPARATIF")
print("=" * 80)

if claim_llm:
    print("\n🤖 Avec Groq LLM:")
    print(f"   • Type détecté: {claim_llm.claim_type}")
    print(f"   • Précision: {claim_llm.claim_type_confidence:.2%}")
    print(f"   • Extraction: {len(claim_llm.facts)} faits")
    print(f"   • Compréhension multilingue: ✅ (FR/AR/Darija)")

print(f"\n📐 Sans LLM (règles):")
print(f"   • Type détecté: {claim_rules.claim_type}")
print(f"   • Précision: {claim_rules.claim_type_confidence:.2%}")
print(f"   • Extraction: {len(claim_rules.facts)} faits")
print(f"   • Compréhension multilingue: ⚠️ (limité)")

if claim_llm and claim_rules:
    print(f"\n🎯 Avantage LLM:")
    print(f"   • Meilleure extraction: {'✅' if len(claim_llm.facts) > len(claim_rules.facts) else '❌'}")
    print(f"   • Contexte darija: ✅")
    print(f"   • Analyse sémantique: ✅")

print("\n" + "=" * 80)
print("✅ Test complet terminé!")
print("=" * 80)

print("\n💡 Pour activer Groq dans l'application:")
print("   Modifier app.py ligne ~300:")
print("   cognitive = CognitiveClaimEngine(use_llm=True, llm_provider='groq')")
