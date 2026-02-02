# backend/routers/audio.py

from fastapi import APIRouter, UploadFile, File, HTTPException
import tempfile
import os
import sys
import logging
from pathlib import Path

# Import from parent directory
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from modules.stt_module import STTEngine

router = APIRouter(prefix="/api", tags=["Audio"])
logger = logging.getLogger(__name__)

stt_engine = STTEngine(use_api=True)


@router.post("/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """Transcrire un fichier audio via LemonFox/Groq ou fallback local."""
    if not file:
        raise HTTPException(status_code=400, detail="Fichier audio requis")

    suffix = os.path.splitext(file.filename or "audio.wav")[-1]
    with tempfile.NamedTemporaryFile(delete=False, suffix=suffix) as tmp:
        tmp.write(await file.read())
        temp_path = tmp.name

    try:
        logger.info(f"📝 Transcription du fichier: {temp_path}")
        metadata = stt_engine.transcribe_audio(temp_path)
        
        if not metadata:
            logger.error("❌ Métadonnées nulles")
            return {"success": False, "error": "Transcription impossible"}

        transcript = metadata.normalized_transcript or metadata.original_transcript
        logger.info(f"✅ Transcription réussie: {transcript[:50]}...")
        
        return {
            "success": True,
            "transcript": transcript,
            "language": metadata.language,
            "confidence": float(metadata.confidence_score) if metadata.confidence_score else None
        }
    except Exception as e:
        logger.error(f"❌ Erreur transcription: {e}", exc_info=True)
        return {"success": False, "error": str(e)}
    finally:
        try:
            os.remove(temp_path)
        except Exception:
            pass
