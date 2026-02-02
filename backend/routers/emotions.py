"""
Router pour l'analyse émotionnelle
Endpoints pour analyser les émotions des clients
"""

import os
import sys
from pathlib import Path
from typing import Optional, List
from datetime import datetime
import json
import sqlite3

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from fastapi import APIRouter, UploadFile, File, Form, HTTPException
from pydantic import BaseModel

from modules.emotion_analyzer import EmotionAnalyzer
from modules.audio_recorder import AudioRecorder

router = APIRouter(prefix="/api/v1/emotions", tags=["Emotions"])

# Initialiser les modules
emotion_analyzer = EmotionAnalyzer()
audio_recorder = AudioRecorder()


class EmotionResponse(BaseModel):
    """Réponse d'analyse émotionnelle"""
    status: str
    dominant_emotion: dict
    fused_scores: dict
    audio_features: dict
    interpretation: str
    audio_path: Optional[str] = None


class EmotionStats(BaseModel):
    """Statistiques émotionnelles"""
    total_recordings: int
    client_audios: int
    advisor_audios: int
    storage_mb: float
    emotions_summary: dict


@router.post("/analyze", response_model=EmotionResponse)
async def analyze_emotion(
    audio: UploadFile = File(...),
    transcription: str = Form(...),
    client_id: Optional[str] = Form(None),
    sinistre_id: Optional[str] = Form(None)
):
    """
    Analyse émotionnelle complète d'un audio client
    
    Args:
        audio: Fichier audio (wav, mp3)
        transcription: Texte transcrit de l'audio
        client_id: ID du client (optionnel)
        sinistre_id: ID du sinistre (optionnel)
        
    Returns:
        Résultats de l'analyse émotionnelle
    """
    try:
        # 1. Sauvegarder temporairement l'audio
        temp_dir = Path("data/temp_audio")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        temp_filename = f"temp_{timestamp}_{audio.filename}"
        temp_path = temp_dir / temp_filename
        
        with open(temp_path, "wb") as f:
            content = await audio.read()
            f.write(content)
        
        # 2. Analyser les émotions
        result = emotion_analyzer.analyze_complete(
            str(temp_path),
            transcription,
            save_results=True
        )
        
        # 3. Enregistrer dans le système (si IDs fournis)
        saved_path = None
        if client_id or sinistre_id:
            saved_path = audio_recorder.save_client_audio(
                str(temp_path),
                client_id=client_id,
                sinistre_id=sinistre_id,
                metadata={
                    "transcription": transcription,
                    "emotion_analysis": result['dominant_emotion'],
                    "fused_scores": result['fused_emotion_scores']
                }
            )
        
        # 4. Interpréter les résultats
        interpretation = emotion_analyzer.get_emotion_interpretation(
            result['dominant_emotion']['label'],
            result['dominant_emotion']['confidence']
        )
        
        return EmotionResponse(
            status="success",
            dominant_emotion=result['dominant_emotion'],
            fused_scores=result['fused_emotion_scores'],
            audio_features=result['audio_features'],
            interpretation=interpretation,
            audio_path=saved_path
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur analyse: {str(e)}")


@router.get("/stats", response_model=EmotionStats)
async def get_emotion_stats():
    """
    Statistiques globales des enregistrements et émotions
    """
    try:
        # Stats d'enregistrement
        recording_stats = audio_recorder.get_recording_stats()
        
        # Analyser toutes les émotions enregistrées
        emotions_count = {
            "anger": 0,
            "stress": 0,
            "sadness": 0,
            "fear": 0,
            "frustration": 0,
            "neutral": 0
        }
        
        # Parcourir les fichiers .emotion.json
        emotion_files = Path("data/recordings/metadata").glob("*.emotion.json") if Path("data/recordings/metadata").exists() else []
        
        for emotion_file in emotion_files:
            try:
                with open(emotion_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    emotion_label = data.get('dominant_emotion', {}).get('label', 'neutral')
                    if emotion_label in emotions_count:
                        emotions_count[emotion_label] += 1
            except:
                pass
        
        return EmotionStats(
            total_recordings=recording_stats['total_audio_count'],
            client_audios=recording_stats['client_audio_count'],
            advisor_audios=recording_stats['advisor_audio_count'],
            storage_mb=recording_stats['total_size_mb'],
            emotions_summary=emotions_count
        )
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur stats: {str(e)}")


@router.get("/history/{sinistre_id}")
async def get_emotion_history(sinistre_id: str):
    """
    Historique émotionnel d'un sinistre spécifique
    
    Args:
        sinistre_id: Numéro du sinistre
        
    Returns:
        Liste chronologique des émotions détectées
    """
    try:
        audios = audio_recorder.get_client_audios(sinistre_id=sinistre_id)
        
        history = []
        for audio_path, meta in audios:
            # Chercher le fichier .emotion.json associé
            emotion_json = Path(audio_path).with_suffix('.emotion.json')
            
            if emotion_json.exists():
                with open(emotion_json, 'r', encoding='utf-8') as f:
                    emotion_data = json.load(f)
                    
                    history.append({
                        "timestamp": meta.get('timestamp'),
                        "dominant_emotion": emotion_data.get('dominant_emotion'),
                        "fused_scores": emotion_data.get('fused_emotion_scores'),
                        "transcription": emotion_data.get('transcription', ''),
                        "audio_path": audio_path
                    })
        
        return {
            "sinistre_id": sinistre_id,
            "emotion_count": len(history),
            "history": history
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur historique: {str(e)}")


@router.get("/recent")
async def get_recent_emotions(limit: int = 10):
    """
    Récupère les N dernières analyses émotionnelles
    
    Args:
        limit: Nombre max de résultats (défaut: 10)
        
    Returns:
        Liste des analyses récentes
    """
    try:
        recent = []
        
        # Parcourir tous les fichiers .emotion.json
        temp_audio_dir = Path("data/temp_audio")
        if temp_audio_dir.exists():
            emotion_files = sorted(
                temp_audio_dir.glob("*.emotion.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            for emotion_file in emotion_files[:limit]:
                with open(emotion_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    recent.append({
                        "timestamp": data.get('timestamp'),
                        "dominant_emotion": data.get('dominant_emotion'),
                        "transcription": data.get('transcription', '')[:100] + '...',
                        "audio_path": data.get('audio_path')
                    })
        
        return {
            "count": len(recent),
            "recent_analyses": recent
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur récents: {str(e)}")


@router.get("/alerts")
async def get_emotion_alerts():
    """
    Récupère les alertes émotionnelles (clients en détresse)
    
    Returns:
        Liste des clients nécessitant une attention immédiate
    """
    try:
        alerts = []
        
        # Seuils d'alerte
        ALERT_THRESHOLDS = {
            "anger": 70,
            "stress": 75,
            "sadness": 60,
            "fear": 65
        }
        
        # Parcourir les analyses récentes
        temp_audio_dir = Path("data/temp_audio")
        if temp_audio_dir.exists():
            emotion_files = sorted(
                temp_audio_dir.glob("*.emotion.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            # Check dernières 50 analyses
            for emotion_file in emotion_files[:50]:
                with open(emotion_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    emotion = data.get('dominant_emotion', {})
                    label = emotion.get('label')
                    confidence = emotion.get('confidence', 0)
                    
                    # Vérifier si c'est une alerte
                    if label in ALERT_THRESHOLDS and confidence >= ALERT_THRESHOLDS[label]:
                        alerts.append({
                            "timestamp": data.get('timestamp'),
                            "emotion": label,
                            "confidence": confidence,
                            "transcription": data.get('transcription', '')[:150],
                            "severity": "high" if confidence >= 85 else "medium",
                            "audio_path": data.get('audio_path')
                        })
        
        return {
            "alert_count": len(alerts),
            "alerts": alerts[:20]  # Max 20 alertes
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur alertes: {str(e)}")


@router.get("/dashboard-summary")
async def get_dashboard_summary():
    """
    Récupère un résumé des émotions pour affichage sur le dashboard principal
    
    Returns:
        Statistiques résumées pour le dashboard
    """
    try:
        temp_audio_dir = Path("data/temp_audio")
        
        # Statistiques globales
        emotion_counts = {
            'anger': 0,
            'stress': 0,
            'sadness': 0,
            'fear': 0,
            'frustration': 0,
            'neutral': 0
        }
        
        alert_count = 0
        recent_analyses = []
        
        if temp_audio_dir.exists():
            emotion_files = sorted(
                temp_audio_dir.glob("*.emotion.json"),
                key=lambda p: p.stat().st_mtime,
                reverse=True
            )
            
            for emotion_file in emotion_files[:30]:  # Dernières 30 analyses
                with open(emotion_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    emotion = data.get('dominant_emotion', {})
                    label = emotion.get('label')
                    confidence = emotion.get('confidence', 0)
                    
                    # Compter les émotions
                    if label in emotion_counts:
                        emotion_counts[label] += 1
                    
                    # Compter les alertes
                    if label in ['anger', 'stress'] and confidence >= 70:
                        alert_count += 1
                    
                    # Ajouter aux analyses récentes (top 5)
                    if len(recent_analyses) < 5:
                        recent_analyses.append({
                            "timestamp": data.get('timestamp'),
                            "emotion": label,
                            "confidence": confidence,
                            "sinistre_id": emotion_file.stem.split('_')[0] if '_' in emotion_file.stem else None
                        })
        
        # Calculer les pourcentages
        total = sum(emotion_counts.values())
        percentages = {k: round((v / total * 100) if total > 0 else 0, 1) 
                      for k, v in emotion_counts.items()}
        
        # Émotion dominante
        dominant = max(emotion_counts.items(), key=lambda x: x[1])
        
        return {
            "total_analyses": total,
            "alert_count": alert_count,
            "emotion_counts": emotion_counts,
            "emotion_percentages": percentages,
            "dominant_emotion": {
                "label": dominant[0],
                "count": dominant[1],
                "percentage": percentages[dominant[0]]
            },
            "recent_analyses": recent_analyses,
            "timestamp": datetime.now().isoformat()
        }
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Erreur résumé dashboard: {str(e)}")

