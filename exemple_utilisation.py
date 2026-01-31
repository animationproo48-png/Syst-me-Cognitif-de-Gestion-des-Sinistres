"""
Exemple d'utilisation complète du STT avec API LemonFox
Ce script montre comment utiliser le module STT avec un fichier audio réel
"""

from modules.stt_module import STTEngine
from modules.cognitive_engine import CognitiveClaimEngine
from modules.complexity_calculator import ComplexityCalculator
from pathlib import Path

print("=" * 70)
print("🎙️ EXEMPLE D'UTILISATION - API LEMONFOX STT")
print("=" * 70)

# ===== ÉTAPE 1: INITIALISATION =====
print("\n1️⃣ Initialisation du moteur STT...")
engine = STTEngine(use_api=True)
print("   ✅ Moteur initialisé avec API LemonFox")

# ===== ÉTAPE 2: TRANSCRIPTION =====
print("\n2️⃣ Transcription d'un fichier audio...")

# Exemple 1: Si vous avez un fichier audio local
audio_file = "data/temp_audio/mon_sinistre.wav"

if Path(audio_file).exists():
    print(f"   📂 Fichier trouvé: {audio_file}")
    
    # Transcrire en français
    result = engine.transcribe_audio(audio_file, language="fr")
    
    print(f"\n   ✅ Transcription réussie!")
    print(f"   📝 Texte original: {result.original_transcript[:100]}...")
    print(f"   ✨ Texte normalisé: {result.normalized_transcript[:100]}...")
    print(f"   🌍 Langue: {result.language}")
    print(f"   📊 Confiance: {result.confidence_score:.2%}")
    print(f"   🎭 Émotions: {result.emotional_markers}")
    print(f"   ⏱️ Durée: {result.duration_seconds}s")
    
    # ===== ÉTAPE 3: ANALYSE COGNITIVE =====
    print("\n3️⃣ Analyse cognitive du sinistre...")
    cognitive = CognitiveClaimEngine()
    claim = cognitive.analyze_claim(result)
    
    print(f"   ✅ Analyse terminée!")
    print(f"   🏷️ Type: {claim.claim_type}")
    print(f"   📅 Date: {claim.incident_date or 'Non spécifiée'}")
    print(f"   📍 Lieu: {claim.location or 'Non spécifié'}")
    print(f"   ✅ Faits: {len(claim.facts)}")
    print(f"   ❓ Suppositions: {len(claim.assumptions)}")
    
    # ===== ÉTAPE 4: CALCUL DE COMPLEXITÉ =====
    print("\n4️⃣ Calcul de la complexité...")
    calculator = ComplexityCalculator()
    complexity = calculator.calculate(claim)
    
    print(f"   ✅ Complexité calculée!")
    print(f"   🎯 Score CCI: {complexity.total_cci}/100")
    print(f"   ⚖️ Niveau: {complexity.complexity_level}")
    print(f"   💡 Recommandation: {claim.recommended_action}")
    
    print("\n" + "=" * 70)
    print("✅ Pipeline complet exécuté avec succès!")
    print("=" * 70)

else:
    print(f"   ⚠️ Fichier {audio_file} non trouvé")
    print("\n   💡 Pour tester avec votre fichier:")
    print("      1. Créez le dossier: data/temp_audio/")
    print("      2. Placez un fichier audio dedans")
    print("      3. Modifiez la variable 'audio_file' ci-dessus")
    print("      4. Relancez ce script")
    
    # Exemple avec mode simulation
    print("\n   🎭 Utilisation du mode simulation à la place...")
    result = engine.transcribe_audio("dummy.wav", language="fr")
    
    print(f"\n   ✅ Transcription simulée générée!")
    print(f"   📝 Texte: {result.normalized_transcript[:150]}...")
    print(f"   🌍 Langue: {result.language}")
    print(f"   📊 Confiance: {result.confidence_score:.2%}")

print("\n" + "=" * 70)
print("📚 DOCUMENTATION:")
print("   - Guide API: GUIDE_API_WHISPER.md")
print("   - Configuration: CONFIGURATION.md")
print("   - Intégration: API_LEMONFOX_INTEGRÉE.md")
print("=" * 70)
