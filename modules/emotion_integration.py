"""
Module d'intégration du système émotionnel dans le flux de conversation
Enregistre automatiquement et analyse les émotions lors des conversations
"""

import sys
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))

from modules.emotion_analyzer import EmotionAnalyzer
from modules.audio_recorder import AudioRecorder
from typing import Optional, Dict
import logging

logger = logging.getLogger(__name__)

# Instances globales
emotion_analyzer = None
audio_recorder = None


def get_emotion_analyzer():
    """Récupère l'instance singleton de l'analyseur d'émotions"""
    global emotion_analyzer
    if emotion_analyzer is None:
        emotion_analyzer = EmotionAnalyzer()
        logger.info("✅ EmotionAnalyzer initialisé")
    return emotion_analyzer


def get_audio_recorder():
    """Récupère l'instance singleton de l'enregistreur audio"""
    global audio_recorder
    if audio_recorder is None:
        audio_recorder = AudioRecorder()
        logger.info("✅ AudioRecorder initialisé")
    return audio_recorder


def process_audio_with_emotion_analysis(
    audio_path: str,
    transcription: str,
    client_id: Optional[str] = None,
    sinistre_id: Optional[str] = None,
    save_audio: bool = True
) -> Dict:
    """
    Traite un audio avec analyse émotionnelle complète
    
    Args:
        audio_path: Chemin du fichier audio
        transcription: Texte transcrit
        client_id: ID du client (optionnel)
        sinistre_id: Numéro du sinistre (optionnel)
        save_audio: Enregistrer l'audio dans le système (défaut: True)
        
    Returns:
        Dict contenant:
        - emotion_result: Résultats de l'analyse émotionnelle
        - audio_saved_path: Chemin où l'audio a été sauvegardé
        - interpretation: Interprétation humaine de l'émotion
    """
    try:
        analyzer = get_emotion_analyzer()
        recorder = get_audio_recorder()
        
        # 1. Analyser les émotions
        logger.info(f"🎭 Analyse émotionnelle de: {Path(audio_path).name}")
        emotion_result = analyzer.analyze_complete(
            audio_path,
            transcription,
            save_results=True
        )
        
        # 2. Enregistrer l'audio si demandé
        audio_saved_path = None
        if save_audio and (client_id or sinistre_id):
            logger.info(f"💾 Enregistrement audio pour client={client_id}, sinistre={sinistre_id}")
            audio_saved_path = recorder.save_client_audio(
                audio_path,
                client_id=client_id,
                sinistre_id=sinistre_id,
                metadata={
                    "transcription": transcription,
                    "emotion_dominant": emotion_result['dominant_emotion'],
                    "fused_scores": emotion_result['fused_emotion_scores']
                }
            )
            logger.info(f"✅ Audio sauvegardé: {audio_saved_path}")
        
        # 3. Interpréter l'émotion
        interpretation = analyzer.get_emotion_interpretation(
            emotion_result['dominant_emotion']['label'],
            emotion_result['dominant_emotion']['confidence']
        )
        
        # 4. Logger l'émotion détectée
        emotion_label = emotion_result['dominant_emotion']['label']
        confidence = emotion_result['dominant_emotion']['confidence']
        logger.info(f"🎯 Émotion détectée: {emotion_label} ({confidence:.1f}%)")
        
        # 5. Alerte si émotion forte
        if emotion_label in ['anger', 'stress', 'fear'] and confidence > 75:
            logger.warning(f"⚠️ ALERTE ÉMOTIONNELLE: {emotion_label.upper()} ({confidence:.1f}%) - Client en détresse")
        
        return {
            "emotion_result": emotion_result,
            "audio_saved_path": audio_saved_path,
            "interpretation": interpretation,
            "dominant_emotion": emotion_result['dominant_emotion'],
            "fused_scores": emotion_result['fused_emotion_scores'],
            "alert_level": get_alert_level(emotion_label, confidence)
        }
        
    except Exception as e:
        logger.error(f"❌ Erreur analyse émotionnelle: {e}")
        return {
            "emotion_result": None,
            "audio_saved_path": None,
            "interpretation": "Analyse émotionnelle non disponible",
            "dominant_emotion": {"label": "unknown", "confidence": 0},
            "fused_scores": {},
            "alert_level": "none"
        }


def get_alert_level(emotion: str, confidence: float) -> str:
    """
    Détermine le niveau d'alerte selon l'émotion et la confiance
    
    Returns:
        'critical', 'high', 'medium', 'low', 'none'
    """
    if emotion == 'anger' and confidence >= 85:
        return 'critical'
    elif emotion in ['anger', 'stress'] and confidence >= 75:
        return 'high'
    elif emotion in ['sadness', 'fear', 'frustration'] and confidence >= 70:
        return 'medium'
    elif emotion in ['anger', 'stress', 'sadness', 'fear'] and confidence >= 50:
        return 'low'
    else:
        return 'none'


def get_emotion_color(emotion: str) -> str:
    """
    Retourne la couleur associée à une émotion
    
    Returns:
        Code couleur hexadécimal
    """
    colors = {
        'anger': '#EF4444',      # Rouge
        'stress': '#F59E0B',     # Orange
        'sadness': '#3B82F6',    # Bleu
        'fear': '#8B5CF6',       # Violet
        'frustration': '#EC4899', # Rose
        'neutral': '#6B7280',    # Gris
        'unknown': '#9CA3AF'     # Gris clair
    }
    return colors.get(emotion, '#9CA3AF')


def get_emotion_label_fr(emotion: str) -> str:
    """
    Retourne le label français d'une émotion
    
    Returns:
        Label en français
    """
    labels = {
        'anger': 'Colère',
        'stress': 'Stress',
        'sadness': 'Tristesse',
        'fear': 'Peur',
        'frustration': 'Frustration',
        'neutral': 'Neutre',
        'unknown': 'Inconnu'
    }
    return labels.get(emotion, 'Inconnu')


def format_emotion_for_response(emotion_data: Dict) -> str:
    """
    Formate les données émotionnelles pour adaptation de réponse
    
    Args:
        emotion_data: Dict retourné par process_audio_with_emotion_analysis
        
    Returns:
        Préfixe de réponse adapté à l'émotion
    """
    if not emotion_data or not emotion_data.get('dominant_emotion'):
        return ""
    
    emotion = emotion_data['dominant_emotion']['label']
    confidence = emotion_data['dominant_emotion']['confidence']
    
    # Seulement si confiance > 60%
    if confidence < 60:
        return ""
    
    prefixes = {
        'anger': "Je comprends parfaitement votre frustration et je vous assure que nous prenons votre situation très au sérieux. ",
        'stress': "Je vais traiter votre demande en priorité pour vous apporter une réponse rapide. ",
        'sadness': "Nous sommes là pour vous accompagner et vous soutenir dans cette situation difficile. ",
        'fear': "Soyez rassuré(e), nous allons examiner votre dossier avec attention et vous tenir informé(e) à chaque étape. ",
        'frustration': "Je comprends que l'attente puisse être difficile. Permettez-moi de voir comment accélérer le traitement de votre dossier. "
    }
    
    return prefixes.get(emotion, "")


if __name__ == "__main__":
    # Test du module
    print("🧪 Test du module d'intégration émotionnelle\n")
    
    # Test avec un fichier audio existant
    test_audio = Path("data/temp_audio")
    if test_audio.exists():
        audio_files = list(test_audio.glob("*.wav"))
        if audio_files:
            result = process_audio_with_emotion_analysis(
                str(audio_files[0]),
                "Je suis vraiment furieux, c'est inadmissible !",
                client_id="TEST123",
                sinistre_id="SIN001"
            )
            print(f"✅ Émotion: {result['dominant_emotion']}")
            print(f"✅ Interprétation: {result['interpretation']}")
            print(f"✅ Niveau alerte: {result['alert_level']}")
        else:
            print("⚠️ Aucun fichier audio trouvé")
    else:
        print("⚠️ Répertoire temp_audio introuvable")
