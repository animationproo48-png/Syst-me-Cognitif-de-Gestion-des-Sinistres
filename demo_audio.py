"""
Script de démonstration du STT avec API Whisper
Teste la transcription avec un fichier audio réel
"""

import sys
from pathlib import Path
from modules.stt_module import STTEngine
from modules.cognitive_engine import CognitiveClaimEngine
from modules.complexity_calculator import ComplexityCalculator
from modules.crm_system import ClaimCRM


def demo_audio_transcription(audio_path: str):
    """
    Démo complète : Audio → Transcription → Analyse → CRM
    
    Args:
        audio_path: Chemin vers le fichier audio
    """
    print("\n" + "🎙️" * 30)
    print("DÉMO TRANSCRIPTION AUDIO - API WHISPER")
    print("🎙️" * 30 + "\n")
    
    # Vérifier que le fichier existe
    if not Path(audio_path).exists():
        print(f"❌ Fichier introuvable : {audio_path}")
        print("\n💡 Astuce : Placez un fichier audio (.wav, .mp3, etc.) dans le dossier")
        print("   et exécutez : python demo_audio.py <chemin_fichier>\n")
        return False
    
    print(f"📁 Fichier : {audio_path}")
    print(f"📦 Taille : {Path(audio_path).stat().st_size / 1024:.1f} KB\n")
    
    # ===== ÉTAPE 1: TRANSCRIPTION =====
    print("─" * 60)
    print("ÉTAPE 1: Transcription Audio → Texte")
    print("─" * 60)
    
    try:
        # Initialiser le moteur STT (API par défaut)
        engine = STTEngine(use_api=True)
        
        print("🌐 Transcription en cours (API Whisper)...")
        
        # Transcrire (détection automatique de langue)
        transcript = engine.transcribe_audio(audio_path)
        
        print(f"\n✅ Transcription réussie!")
        print(f"   🌍 Langue détectée : {transcript.language}")
        print(f"   📊 Confiance : {transcript.confidence_score:.2%}")
        print(f"   ⏱️ Durée : {transcript.duration_seconds:.1f}s")
        print(f"   🎭 Émotions : {', '.join(transcript.emotional_markers) or 'Neutre'}")
        print(f"   🗣️ Hésitations : {transcript.hesitations}")
        
        print(f"\n📝 Transcription originale :")
        print(f"   {transcript.original_transcript[:200]}...")
        
        print(f"\n✨ Transcription normalisée :")
        print(f"   {transcript.normalized_transcript[:200]}...")
        
    except Exception as e:
        print(f"\n❌ Erreur de transcription : {e}")
        print("   Le système va utiliser le mode simulation...")
        
        # Fallback sur simulation
        transcript = engine._simulate_transcription(audio_path, "fr")
        print(f"\n⚠️ Mode simulation activé")
    
    # ===== ÉTAPE 2: ANALYSE COGNITIVE =====
    print("\n" + "─" * 60)
    print("ÉTAPE 2: Analyse Cognitive du Sinistre")
    print("─" * 60)
    
    try:
        cognitive = CognitiveClaimEngine()
        
        print("🧠 Analyse en cours...")
        claim = cognitive.analyze_claim(transcript)
        
        print(f"\n✅ Analyse terminée!")
        print(f"   🏷️ Type : {claim.claim_type}")
        print(f"   📅 Date : {claim.incident_date or 'Non spécifiée'}")
        print(f"   📍 Lieu : {claim.location or 'Non spécifié'}")
        print(f"   ✅ Faits vérifiés : {len(claim.facts)}")
        print(f"   ❓ Suppositions : {len(claim.assumptions)}")
        print(f"   📄 Documents manquants : {len(claim.missing_information)}")
        
        if claim.facts:
            print(f"\n   📋 Faits clés :")
            for fact in claim.facts[:3]:
                print(f"      • {fact}")
        
    except Exception as e:
        print(f"\n❌ Erreur d'analyse : {e}")
        return False
    
    # ===== ÉTAPE 3: CALCUL DE COMPLEXITÉ =====
    print("\n" + "─" * 60)
    print("ÉTAPE 3: Calcul de la Complexité (CCI)")
    print("─" * 60)
    
    try:
        calculator = ComplexityCalculator()
        
        print("📊 Calcul en cours...")
        complexity = calculator.calculate(claim)
        
        print(f"\n✅ Complexité calculée!")
        print(f"   🎯 Score CCI : {complexity.total_cci}/100")
        print(f"   ⚖️ Niveau : {complexity.complexity_level}")
        print(f"   📈 Dimensions :")
        print(f"      • Garanties : {complexity.guarantees_score}/20")
        print(f"      • Tiers impliqués : {complexity.third_party_score}/20")
        print(f"      • Documents : {complexity.missing_docs_score}/20")
        print(f"      • Ambiguïté : {complexity.ambiguity_score}/15")
        print(f"      • Émotionnel : {complexity.emotional_score}/15")
        print(f"      • Incohérences : {complexity.inconsistency_score}/10")
        
    except Exception as e:
        print(f"\n❌ Erreur de calcul : {e}")
        return False
    
    # ===== ÉTAPE 4: ENREGISTREMENT CRM =====
    print("\n" + "─" * 60)
    print("ÉTAPE 4: Enregistrement dans la CRM")
    print("─" * 60)
    
    try:
        crm = ClaimCRM()
        
        print("💾 Enregistrement en cours...")
        claim_id = crm.create_claim(claim)
        
        print(f"\n✅ Sinistre enregistré!")
        print(f"   🆔 ID : {claim_id}")
        print(f"   📊 Statut : En attente de traitement")
        
        # Statistiques CRM
        stats = crm.get_statistics()
        print(f"\n📈 Statistiques CRM :")
        print(f"   📋 Total sinistres : {stats['total_claims']}")
        print(f"   ⏳ En attente : {stats['pending_claims']}")
        print(f"   ✅ Traités : {stats['processed_claims']}")
        
    except Exception as e:
        print(f"\n❌ Erreur CRM : {e}")
        return False
    
    # ===== RÉSUMÉ FINAL =====
    print("\n" + "=" * 60)
    print("🎉 DÉMO TERMINÉE AVEC SUCCÈS!")
    print("=" * 60)
    print(f"\n✅ Pipeline complet exécuté :")
    print(f"   1. Audio transcrit (API Whisper)")
    print(f"   2. Sinistre analysé (Cognitive Engine)")
    print(f"   3. Complexité calculée (CCI: {complexity.total_cci}/100)")
    print(f"   4. Enregistré dans CRM (ID: {claim_id})")
    
    print(f"\n💡 Recommandation : {claim.recommended_action}")
    
    print("\n" + "=" * 60 + "\n")
    
    return True


def main():
    """Point d'entrée principal"""
    
    if len(sys.argv) < 2:
        print("\n" + "🎙️" * 30)
        print("DÉMO TRANSCRIPTION AUDIO - API WHISPER")
        print("🎙️" * 30)
        print("\nUsage:")
        print("  python demo_audio.py <chemin_fichier_audio>\n")
        print("Exemple:")
        print("  python demo_audio.py mon_audio.wav")
        print("  python demo_audio.py recordings/sinistre.mp3\n")
        print("Formats supportés: .wav, .mp3, .m4a, .ogg, .flac, .webm")
        print("\n💡 Si vous n'avez pas de fichier audio, utilisez:")
        print("   streamlit run app.py")
        print("   (puis utilisez le mode 'Simulation textuelle')\n")
        return
    
    audio_path = sys.argv[1]
    success = demo_audio_transcription(audio_path)
    
    sys.exit(0 if success else 1)


if __name__ == "__main__":
    main()
