"""
Script de test rapide pour générer des données émotionnelles de démo
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

from modules.emotion_analyzer import EmotionAnalyzer
from modules.audio_recorder import AudioRecorder
import json
from datetime import datetime

print("🧪 Génération de données émotionnelles de démonstration...")

analyzer = EmotionAnalyzer()
recorder = AudioRecorder()

# Exemples de déclarations clients avec émotions variées
test_cases = [
    {
        "text": "Je suis FURIEUX ! Cela fait 3 semaines que j'attends et RIEN ! C'est INADMISSIBLE !",
        "sinistre": "SIN001"
    },
    {
        "text": "Je suis très stressé, j'ai besoin d'une réponse rapidement s'il vous plaît, c'est urgent.",
        "sinistre": "SIN002"
    },
    {
        "text": "Je suis triste, personne ne m'aide, c'est vraiment difficile pour moi...",
        "sinistre": "SIN003"
    },
    {
        "text": "J'ai peur que mon dossier soit refusé, je suis très inquiet pour mon avenir.",
        "sinistre": "SIN004"
    },
    {
        "text": "Bonjour, je voudrais déclarer un sinistre automobile survenu hier à 14h30.",
        "sinistre": "SIN005"
    },
    {
        "text": "C'est la troisième fois que j'appelle ! Vous vous moquez de moi ?! Incroyable !",
        "sinistre": "SIN006"
    },
    {
        "text": "Je comprends les délais mais là c'est vraiment trop long, je suis pressé.",
        "sinistre": "SIN007"
    },
]

# Créer des analyses pour chaque cas
for i, case in enumerate(test_cases, 1):
    print(f"\n[{i}/{len(test_cases)}] Analyse: {case['sinistre']}")
    
    # Analyser le texte (pas d'audio réel pour la démo)
    text_scores = analyzer.analyze_text_emotion(case['text'])
    
    # Simuler des scores audio (pour la démo)
    audio_scores = {
        "anger": text_scores.get("anger", 0) * 0.8,
        "stress": text_scores.get("stress", 0) * 0.9,
        "sadness": text_scores.get("sadness", 0) * 0.7,
        "fear": text_scores.get("fear", 0) * 0.8,
        "frustration": text_scores.get("frustration", 0) * 0.85,
        "neutral": text_scores.get("neutral", 0) * 1.1
    }
    
    # Fusionner
    fused_scores = analyzer.fuse_emotion_scores(text_scores, audio_scores)
    
    # Émotion dominante
    dominant = max(fused_scores.items(), key=lambda x: x[1])
    
    # Créer un fichier .emotion.json dans temp_audio pour simulation
    temp_dir = Path("data/temp_audio")
    temp_dir.mkdir(parents=True, exist_ok=True)
    
    emotion_file = temp_dir / f"demo_{case['sinistre']}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.emotion.json"
    
    emotion_data = {
        "timestamp": datetime.now().isoformat(),
        "audio_path": str(emotion_file.with_suffix('.wav')),
        "transcription": case['text'],
        "text_emotion_scores": text_scores,
        "audio_emotion_scores": audio_scores,
        "fused_emotion_scores": fused_scores,
        "dominant_emotion": {
            "label": dominant[0],
            "confidence": round(dominant[1], 2)
        },
        "analysis_mode": "demo"
    }
    
    with open(emotion_file, 'w', encoding='utf-8') as f:
        json.dump(emotion_data, f, indent=2, ensure_ascii=False)
    
    print(f"  ✅ Émotion: {dominant[0]} ({dominant[1]:.1f}%)")
    print(f"  📁 Sauvegardé: {emotion_file.name}")

print(f"\n✅ {len(test_cases)} analyses de démo créées !")
print(f"📊 Vous pouvez maintenant consulter le dashboard: http://localhost:3001/emotions")
print(f"📁 Fichiers dans: data/temp_audio/")
