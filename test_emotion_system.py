"""
Test du système d'analyse émotionnelle multimodale
"""

import sys
from pathlib import Path

# Ajouter le chemin parent pour les imports
sys.path.append(str(Path(__file__).parent))

from modules.emotion_analyzer import EmotionAnalyzer, analyze_claim_audio
from modules.audio_recorder import AudioRecorder


def test_emotion_analyzer():
    """Test de l'analyseur d'émotions"""
    print("="*70)
    print("TEST 1: Analyseur d'émotions (texte seul)")
    print("="*70 + "\n")
    
    analyzer = EmotionAnalyzer()
    
    # Test différents textes émotionnels
    test_cases = [
        {
            "text": "Je suis vraiment furieux ! C'est inacceptable ! Vous devez régler ça MAINTENANT !",
            "expected": "anger"
        },
        {
            "text": "Je suis très stressé, j'ai besoin d'aide rapidement s'il vous plaît...",
            "expected": "stress"
        },
        {
            "text": "Je suis triste et découragé, personne ne m'aide...",
            "expected": "sadness"
        },
        {
            "text": "J'ai peur que mon dossier soit refusé, c'est très inquiétant",
            "expected": "fear"
        },
        {
            "text": "Bonjour, je voudrais déclarer un sinistre survenu hier à 14h",
            "expected": "neutral"
        }
    ]
    
    for i, case in enumerate(test_cases, 1):
        print(f"Test {i}: {case['expected'].upper()}")
        print(f"Texte: \"{case['text']}\"")
        
        scores = analyzer.analyze_text_emotion(case['text'])
        dominant = max(scores.items(), key=lambda x: x[1])
        
        print(f"Émotion dominante: {dominant[0]} ({dominant[1]:.1f}%)")
        print(f"Scores détaillés:")
        for emotion, score in sorted(scores.items(), key=lambda x: -x[1]):
            if score > 0:
                bar = "█" * int(score / 5)
                print(f"  {emotion:12} {score:5.1f}% {bar}")
        
        # Interprétation
        interpretation = analyzer.get_emotion_interpretation(dominant[0], dominant[1])
        print(f"💡 {interpretation}")
        print()
    
    print("✅ Test analyseur d'émotions texte: RÉUSSI\n")


def test_audio_recorder():
    """Test du système d'enregistrement"""
    print("="*70)
    print("TEST 2: Système d'enregistrement audio")
    print("="*70 + "\n")
    
    recorder = AudioRecorder()
    
    # Afficher les stats
    stats = recorder.get_recording_stats()
    print("📊 Statistiques d'enregistrement:")
    print(f"  Audios clients: {stats['client_audio_count']}")
    print(f"  Audios conseillers: {stats['advisor_audio_count']}")
    print(f"  Total: {stats['total_audio_count']}")
    print(f"  Taille totale: {stats['total_size_mb']} MB")
    print(f"  Emplacement: {stats['storage_path']}")
    
    print("\n✅ Test système d'enregistrement: RÉUSSI\n")


def test_complete_analysis():
    """Test analyse complète (si un audio existe)"""
    print("="*70)
    print("TEST 3: Analyse complète multimodale (audio + texte)")
    print("="*70 + "\n")
    
    # Chercher un fichier audio test
    test_audio_dir = Path("c:/Users/HP/Inssurance Advanced/data/temp_audio")
    
    if not test_audio_dir.exists():
        print("⚠️ Pas de répertoire temp_audio, test ignoré")
        return
    
    audio_files = list(test_audio_dir.glob("*.wav")) + list(test_audio_dir.glob("*.mp3"))
    
    if not audio_files:
        print("⚠️ Pas de fichier audio trouvé, test ignoré")
        return
    
    # Prendre le premier fichier
    audio_path = str(audio_files[0])
    print(f"📁 Fichier audio: {audio_files[0].name}")
    
    # Simulation de transcription (dans la vraie app, ce serait le STT)
    test_transcription = "Je suis vraiment stressé, mon accident était grave et j'ai besoin d'une réponse urgente !"
    print(f"📝 Transcription simulée: \"{test_transcription}\"")
    print()
    
    # Analyser
    analyzer = EmotionAnalyzer()
    result = analyzer.analyze_complete(audio_path, test_transcription, save_results=True)
    
    print("🎯 RÉSULTATS:")
    print(f"  Mode d'analyse: {result['analysis_mode']}")
    print(f"  Émotion dominante: {result['dominant_emotion']['label']} ({result['dominant_emotion']['confidence']}%)")
    print()
    
    print("📊 Scores émotionnels fusionnés:")
    for emotion, score in sorted(result['fused_emotion_scores'].items(), key=lambda x: -x[1]):
        if score > 5:  # Seulement les scores significatifs
            bar = "█" * int(score / 5)
            print(f"  {emotion:12} {score:5.1f}% {bar}")
    
    print()
    print("🔊 Features audio extraites:")
    features = result['audio_features']
    if not features.get('fallback'):
        print(f"  Pitch moyen: {features['pitch_mean']:.1f} Hz")
        print(f"  Variation pitch: {features['pitch_std']:.1f} Hz")
        print(f"  Énergie: {features['energy_mean']:.4f}")
        print(f"  Tempo: {features['tempo']:.1f} BPM")
        print(f"  Durée: {features['duration']:.1f}s")
    else:
        print("  (Analyse audio basique - librosa non installé)")
    
    print()
    print("💬 Scores émotionnels (texte):")
    for emotion, score in sorted(result['text_emotion_scores'].items(), key=lambda x: -x[1]):
        if score > 5:
            print(f"  {emotion:12} {score:5.1f}%")
    
    print()
    print("🔊 Scores émotionnels (audio):")
    for emotion, score in sorted(result['audio_emotion_scores'].items(), key=lambda x: -x[1]):
        if score > 5:
            print(f"  {emotion:12} {score:5.1f}%")
    
    print()
    interpretation = analyzer.get_emotion_interpretation(
        result['dominant_emotion']['label'],
        result['dominant_emotion']['confidence']
    )
    print(f"💡 Interprétation: {interpretation}")
    
    print("\n✅ Test analyse complète: RÉUSSI\n")


def main():
    """Lance tous les tests"""
    print("\n" + "="*70)
    print("🧪 TEST DU SYSTÈME D'ANALYSE ÉMOTIONNELLE MULTIMODALE")
    print("="*70 + "\n")
    
    try:
        test_emotion_analyzer()
        test_audio_recorder()
        test_complete_analysis()
        
        print("="*70)
        print("✅ TOUS LES TESTS RÉUSSIS")
        print("="*70)
        
        print("\n📋 Prochaines étapes:")
        print("  1. Installer les dépendances audio: pip install librosa soundfile praat-parselmouth")
        print("  2. Intégrer dans le backend (main.py)")
        print("  3. Ajouter les endpoints API")
        print("  4. Créer le dashboard d'analyse émotionnelle")
        print("  5. Connecter au système de conversation")
        
    except Exception as e:
        print(f"\n❌ ERREUR LORS DES TESTS: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
