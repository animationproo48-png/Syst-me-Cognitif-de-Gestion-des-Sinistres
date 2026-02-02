"""
Script de démonstration complète du système émotionnel
Génère des conversations simulées avec analyses émotionnelles
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent))

import numpy as np
import soundfile as sf
from datetime import datetime, timedelta
import random

from modules.emotion_integration import (
    process_audio_with_emotion_analysis,
    get_emotion_label_fr,
    get_emotion_color
)

# Scénarios de conversation réalistes
SCENARIOS = [
    {
        "client_id": "CLI001",
        "sinistre_id": "SIN001",
        "emotion": "anger",
        "transcription": "C'est INADMISSIBLE ! Ça fait 3 semaines que j'attends et PERSONNE ne me rappelle ! Mon dossier est URGENT !",
        "pitch_base": 250,  # Hz - voix tendue/aiguë
        "energy": 0.08,     # Amplitude forte
        "tempo": 150        # BPM rapide
    },
    {
        "client_id": "CLI002",
        "sinistre_id": "SIN002",
        "emotion": "stress",
        "transcription": "Je suis vraiment stressé, c'est très urgent, j'ai besoin d'une réponse rapidement s'il vous plaît.",
        "pitch_base": 210,
        "energy": 0.06,
        "tempo": 140
    },
    {
        "client_id": "CLI003",
        "sinistre_id": "SIN003",
        "emotion": "sadness",
        "transcription": "Je suis tellement triste... Personne ne peut m'aider avec mon dossier. Je me sens abandonné.",
        "pitch_base": 150,  # Voix basse
        "energy": 0.03,     # Faible
        "tempo": 90         # Lent
    },
    {
        "client_id": "CLI004",
        "sinistre_id": "SIN004",
        "emotion": "fear",
        "transcription": "J'ai vraiment peur que mon dossier soit refusé... Je ne sais pas quoi faire si ça arrive.",
        "pitch_base": 200,
        "energy": 0.04,
        "tempo": 110
    },
    {
        "client_id": "CLI005",
        "sinistre_id": "SIN005",
        "emotion": "frustration",
        "transcription": "C'est la troisième fois que j'appelle ! Toujours la même réponse ! Vous vous moquez de moi ?",
        "pitch_base": 230,
        "energy": 0.07,
        "tempo": 135
    },
    {
        "client_id": "CLI006",
        "sinistre_id": "SIN006",
        "emotion": "neutral",
        "transcription": "Bonjour, je souhaite déclarer un sinistre automobile survenu hier à 14h30 sur la rocade.",
        "pitch_base": 180,
        "energy": 0.04,
        "tempo": 100
    },
    {
        "client_id": "CLI001",
        "sinistre_id": "SIN001",
        "emotion": "anger",
        "transcription": "Encore une fois ! Toujours les mêmes excuses ! Je veux parler au responsable MAINTENANT !",
        "pitch_base": 270,
        "energy": 0.09,
        "tempo": 160
    },
    {
        "client_id": "CLI007",
        "sinistre_id": "SIN007",
        "emotion": "stress",
        "transcription": "S'il vous plaît, c'est pressé, j'ai un rendez-vous dans une heure, il me faut cette attestation maintenant.",
        "pitch_base": 220,
        "energy": 0.065,
        "tempo": 145
    }
]


def generate_synthetic_audio(pitch_base, energy, tempo, duration=3.0, sample_rate=16000):
    """
    Génère un audio synthétique avec caractéristiques émotionnelles
    
    Args:
        pitch_base: Fréquence de base (Hz)
        energy: Amplitude RMS
        tempo: Tempo (BPM, influence la modulation)
        duration: Durée (secondes)
        sample_rate: Taux d'échantillonnage
        
    Returns:
        numpy array audio
    """
    t = np.linspace(0, duration, int(sample_rate * duration))
    
    # Onde de base (sinusoïde à la fréquence pitch_base)
    audio = np.sin(2 * np.pi * pitch_base * t)
    
    # Ajouter harmoniques (plus réaliste)
    audio += 0.3 * np.sin(2 * np.pi * pitch_base * 2 * t)  # 2ème harmonique
    audio += 0.15 * np.sin(2 * np.pi * pitch_base * 3 * t)  # 3ème harmonique
    
    # Modulation tempo (vibrato émotionnel)
    modulation_freq = tempo / 60  # Hz
    modulation = 1 + 0.1 * np.sin(2 * np.pi * modulation_freq * t)
    audio = audio * modulation
    
    # Ajuster l'énergie (amplitude)
    audio = audio * energy
    
    # Ajouter bruit (respiration, fond)
    noise = np.random.normal(0, energy * 0.1, len(audio))
    audio = audio + noise
    
    # Normaliser
    audio = audio / np.max(np.abs(audio)) * 0.8
    
    return audio.astype(np.float32)


def run_demo():
    """Exécute la démonstration complète"""
    print("\n" + "=" * 70)
    print("🎭 DÉMONSTRATION SYSTÈME D'ANALYSE ÉMOTIONNELLE")
    print("=" * 70)
    
    print("\n📊 Scénarios à simuler:")
    for i, scenario in enumerate(SCENARIOS, 1):
        emotion_fr = get_emotion_label_fr(scenario['emotion'])
        color = get_emotion_color(scenario['emotion'])
        print(f"{i}. [{scenario['sinistre_id']}] {emotion_fr} - {scenario['transcription'][:50]}...")
    
    print("\n🎬 Génération des audios et analyses en cours...\n")
    
    results = []
    temp_audio_dir = Path("data/temp_audio")
    temp_audio_dir.mkdir(parents=True, exist_ok=True)
    
    for i, scenario in enumerate(SCENARIOS, 1):
        print(f"\n{'─' * 70}")
        print(f"[{i}/{len(SCENARIOS)}] {scenario['sinistre_id']} - {get_emotion_label_fr(scenario['emotion'])}")
        print(f"{'─' * 70}")
        
        # Générer audio synthétique
        print("🎙️ Génération audio synthétique...")
        audio = generate_synthetic_audio(
            pitch_base=scenario['pitch_base'],
            energy=scenario['energy'],
            tempo=scenario['tempo'],
            duration=3.0
        )
        
        # Sauvegarder l'audio
        timestamp = datetime.now() - timedelta(minutes=len(SCENARIOS) - i)  # Échelonner dans le temps
        audio_filename = f"demo_{scenario['sinistre_id']}_{timestamp.strftime('%Y%m%d_%H%M%S')}.wav"
        audio_path = temp_audio_dir / audio_filename
        
        sf.write(audio_path, audio, 16000)
        print(f"✅ Audio sauvegardé: {audio_filename}")
        
        # Analyser avec le système complet
        print("🎭 Analyse émotionnelle en cours...")
        emotion_data = process_audio_with_emotion_analysis(
            str(audio_path),
            scenario['transcription'],
            client_id=scenario['client_id'],
            sinistre_id=scenario['sinistre_id'],
            save_audio=True
        )
        
        # Afficher résultats
        detected_emotion = emotion_data['dominant_emotion']['label']
        confidence = emotion_data['dominant_emotion']['confidence']
        alert_level = emotion_data['alert_level']
        
        emotion_fr = get_emotion_label_fr(detected_emotion)
        expected_fr = get_emotion_label_fr(scenario['emotion'])
        
        # Symboles d'alerte
        alert_symbols = {
            'critical': '🚨',
            'high': '⚠️',
            'medium': '💙',
            'low': '🔵',
            'none': '🟢'
        }
        
        print(f"\n📊 RÉSULTATS:")
        print(f"  Attendue:  {expected_fr}")
        print(f"  Détectée:  {emotion_fr} ({confidence:.1f}%)")
        print(f"  Alerte:    {alert_symbols.get(alert_level, '❓')} {alert_level.upper()}")
        print(f"  Match:     {'✅ EXACT' if detected_emotion == scenario['emotion'] else '⚠️ DIFFÉRENT'}")
        
        results.append({
            'sinistre_id': scenario['sinistre_id'],
            'expected': scenario['emotion'],
            'detected': detected_emotion,
            'confidence': confidence,
            'alert_level': alert_level,
            'match': detected_emotion == scenario['emotion']
        })
    
    # Résumé final
    print("\n" + "=" * 70)
    print("📈 RÉSUMÉ DE LA DÉMONSTRATION")
    print("=" * 70)
    
    total = len(results)
    matches = sum(1 for r in results if r['match'])
    accuracy = (matches / total) * 100
    
    print(f"\nPrécision globale: {matches}/{total} ({accuracy:.1f}%)")
    
    # Statistiques par émotion
    print("\n📊 Détails par émotion:")
    for emotion in ['anger', 'stress', 'sadness', 'fear', 'frustration', 'neutral']:
        emotion_results = [r for r in results if r['expected'] == emotion]
        if emotion_results:
            emotion_matches = sum(1 for r in emotion_results if r['match'])
            emotion_total = len(emotion_results)
            emotion_accuracy = (emotion_matches / emotion_total) * 100
            emotion_fr = get_emotion_label_fr(emotion)
            
            avg_confidence = np.mean([r['confidence'] for r in emotion_results])
            
            print(f"  {emotion_fr:12} : {emotion_matches}/{emotion_total} ({emotion_accuracy:.0f}%) - Confiance moy: {avg_confidence:.1f}%")
    
    # Alertes générées
    print("\n🚨 Alertes générées:")
    critical_alerts = [r for r in results if r['alert_level'] == 'critical']
    high_alerts = [r for r in results if r['alert_level'] == 'high']
    
    print(f"  Critiques: {len(critical_alerts)}")
    for alert in critical_alerts:
        print(f"    - {alert['sinistre_id']}: {get_emotion_label_fr(alert['detected'])} ({alert['confidence']:.1f}%)")
    
    print(f"  Hautes:    {len(high_alerts)}")
    for alert in high_alerts:
        print(f"    - {alert['sinistre_id']}: {get_emotion_label_fr(alert['detected'])} ({alert['confidence']:.1f}%)")
    
    # Fichiers générés
    print("\n📁 Fichiers générés:")
    audio_files = list(temp_audio_dir.glob("demo_*.wav"))
    emotion_files = list(temp_audio_dir.glob("demo_*.emotion.json"))
    
    print(f"  Audios:    {len(audio_files)} fichiers WAV")
    print(f"  Analyses:  {len(emotion_files)} fichiers JSON")
    
    # Prochaines étapes
    print("\n" + "=" * 70)
    print("✅ DÉMONSTRATION TERMINÉE")
    print("=" * 70)
    
    print("\n🚀 Vérifier les résultats:")
    print("  1. Dashboard web: http://localhost:3001/")
    print("  2. Page émotions: http://localhost:3001/emotions")
    print("  3. API backend:   http://localhost:8000/api/v1/emotions/dashboard-summary")
    print("  4. Fichiers JSON: data/temp_audio/*.emotion.json")
    
    print("\n💡 Les données sont maintenant visibles dans:")
    print("  - Le dashboard principal (section émotions)")
    print("  - La page détaillée des émotions")
    print("  - Les analyses Streamlit (si upload)")


if __name__ == "__main__":
    try:
        run_demo()
    except KeyboardInterrupt:
        print("\n\n⚠️ Démonstration interrompue par l'utilisateur")
    except Exception as e:
        print(f"\n\n❌ ERREUR: {e}")
        import traceback
        traceback.print_exc()
