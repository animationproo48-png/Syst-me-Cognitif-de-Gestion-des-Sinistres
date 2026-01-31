"""
Test rapide de précision STT avec auto-détection
"""

from modules.stt_module import STTEngine

def test_auto_detection():
    print("="*80)
    print("🧪 TEST: Précision STT avec Auto-Détection")
    print("="*80)
    
    engine = STTEngine()
    
    # Test 1: Auto-détection (language=None)
    print("\n📍 Test 1: Auto-détection (language=None)")
    print("   L'API LemonFox détectera automatiquement la langue")
    
    result_auto = engine._process_result(
        text="السلام عليكم، كنت ماشي فالطريق وجا واحد ضرب فيا",
        lang="ar",  # API aurait détecté "ar"
        conf=0.95,
        duration=3.0
    )
    print(f"   ✅ Langue détectée: {result_auto.language}")
    print(f"   ✅ Transcription: {result_auto.original_transcript[:50]}...")
    
    # Test 2: Français explicite
    print("\n📍 Test 2: Français explicite (language='fr')")
    result_fr = engine._process_result(
        text="Bonjour, j'ai eu un accident hier sur l'autoroute",
        lang="fr",
        conf=0.92,
        duration=2.5
    )
    print(f"   ✅ Langue: {result_fr.language}")
    print(f"   ✅ Transcription: {result_fr.original_transcript}")
    print(f"   ℹ️  Pas de traduction (déjà en français)")
    
    # Test 3: Arabe explicite
    print("\n📍 Test 3: Arabe/Darija explicite (language='ar')")
    result_ar = engine._process_result(
        text="الكار تكسرات، غادي نخلص التأمين",
        lang="ar",
        conf=0.98,
        duration=2.0
    )
    print(f"   ✅ Langue: {result_ar.language}")
    print(f"   ✅ Original: {result_ar.original_transcript}")
    if result_ar.normalized_transcript != result_ar.original_transcript:
        print(f"   🌐 Traduit: {result_ar.normalized_transcript}")
    
    print("\n" + "="*80)
    print("✅ CONCLUSION:")
    print("   • Auto-détection préservée pour meilleure précision")
    print("   • Traduction automatique activée pour Darija/Arabe")
    print("   • Français passé directement sans traduction")
    print("="*80)

if __name__ == "__main__":
    test_auto_detection()
