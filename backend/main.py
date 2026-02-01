"""
Backend FastAPI pour MVP Gestion Cognitive des Sinistres
Exposes les modules Python en API REST + WebSocket temps réel
"""

from dotenv import load_dotenv
load_dotenv()  # Charger .env au démarrage

from fastapi import FastAPI, UploadFile, File, WebSocket, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse, FileResponse
from fastapi.staticfiles import StaticFiles
from pydantic import BaseModel
from pathlib import Path
import sys
import os
from datetime import datetime
import json
import uuid

# Ajouter les modules Python existants au path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Imports des modules existants
from modules.stt_module import STTEngine
from modules.tts_module import TTSEngine
from modules.cognitive_engine import CognitiveClaimEngine
from modules.conversation_manager import ConversationManager, ConversationPhase
from modules.complexity_calculator import ComplexityCalculator
from modules.decision_engine import DecisionEngine
from modules.summary_generator import SummaryGenerator
from modules.crm_system import get_crm
from models.claim_models import ClaimDigitalTwin, ClaimState

# Configuration FastAPI
app = FastAPI(
    title="Insurance Claims API",
    description="API moderne pour gestion cognitive des sinistres",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Modèles Pydantic
class ClaimRequest(BaseModel):
    text: str
    language: str = "fr"

class ClaimResponse(BaseModel):
    claim_id: str
    status: str
    complexity_score: float
    claim_type: str
    is_escalated: bool
    summary: dict

class ConversationMessage(BaseModel):
    speaker: str
    text: str
    timestamp: str

# Stockage des sessions (en mémoire pour MVP)
active_sessions = {}

# Helper pour TTS
def generate_tts_audio(text: str, tts_engine: TTSEngine) -> str:
    """Génère l'audio TTS et retourne le chemin"""
    try:
        audio_path = tts_engine.synthesize(text, tone="professional")
        return audio_path
    except Exception as e:
        print(f"❌ Erreur TTS: {e}")
        return None

def build_audio_url(audio_path: str) -> str:
    """Construit l'URL audio servie par /audio/{filename}."""
    if not audio_path:
        return None
    filename = Path(audio_path).name
    return f"/audio/{filename}"

# ===== ENDPOINTS SANTÉ =====

@app.get("/health")
def health_check():
    """Vérifier que l'API est en ligne"""
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "version": "1.0.0"
    }

@app.get("/audio/{filename}")
def serve_audio(filename: str):
    """Servir les fichiers audio générés"""
    audio_path = Path(f"c:/Users/HP/Inssurance Advanced/data/audio_responses/{filename}")
    if audio_path.exists():
        return FileResponse(audio_path, media_type="audio/mpeg")
    raise HTTPException(status_code=404, detail="Audio not found")

# ===== ENDPOINTS DÉCLARATION SINISTRE =====

@app.post("/api/transcribe")
async def transcribe_audio(file: UploadFile = File(...)):
    """
    Transcrit un fichier audio en texte
    
    - Upload audio → STT → Retourne transcription
    """
    try:
        # Sauvegarder temporairement le fichier
        temp_dir = Path("data/temp_audio")
        temp_dir.mkdir(parents=True, exist_ok=True)
        
        temp_file = temp_dir / f"upload_{datetime.now().strftime('%Y%m%d_%H%M%S')}.wav"
        
        with open(temp_file, "wb") as f:
            content = await file.read()
            f.write(content)
        
        # Transcription avec STT Engine (AUTO-DÉTECTION pour arabe/français)
        stt_engine = STTEngine()
        transcript_metadata = stt_engine.transcribe_audio(str(temp_file), language=None)
        
        # Nettoyer le fichier temporaire
        try:
            temp_file.unlink()
        except:
            pass
        
        return {
            "success": True,
            "transcript": transcript_metadata.normalized_transcript,
            "original": transcript_metadata.original_transcript,
            "language": transcript_metadata.language,
            "confidence": transcript_metadata.confidence_score
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Transcription error: {str(e)}")

@app.post("/api/claims", response_model=ClaimResponse)
async def create_claim(request: ClaimRequest):
    """
    Crée une nouvelle déclaration de sinistre
    
    - Transcription → Analyse cognitive → Décision escalade
    - Retourne un résumé structuré
    """
    try:
        # Créer les métadonnées de transcription simulées
        from models.claim_models import TranscriptMetadata
        
        transcript = TranscriptMetadata(
            original_transcript=request.text,
            normalized_transcript=request.text.strip(),
            language=request.language,
            confidence_score=0.95,
            emotional_markers=["stress"] if "inquiet" in request.text.lower() else [],
            hesitations=0,
            duration_seconds=60.0
        )
        
        # 1. Analyse cognitive
        cognitive_engine = CognitiveClaimEngine(use_llm=False)
        cognitive_structure = cognitive_engine.analyze_claim(transcript)
        
        # 2. Calcul complexité
        complexity_calc = ComplexityCalculator()
        complexity = complexity_calc.calculate(cognitive_structure)
        
        # 3. Digital Twin
        claim_id = f"CLM-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        digital_twin = ClaimDigitalTwin(
            claim_id=claim_id,
            transcript_metadata=transcript,
            cognitive_structure=cognitive_structure,
            complexity=complexity,
            current_state=ClaimState.ANALYZING
        )
        
        # 4. Décision
        decision_engine = DecisionEngine()
        should_escalate, reason, action = decision_engine.make_decision(digital_twin)
        
        if should_escalate:
            digital_twin.escalate(reason)
        else:
            digital_twin.change_state(ClaimState.AUTONOMOUS, reason)
        
        # 5. Résumés
        summary_gen = SummaryGenerator()
        client_summary = summary_gen.generate_client_summary(digital_twin)
        
        # Sauvegarder en CRM
        crm = get_crm()
        crm.create_claim(digital_twin)
        
        return ClaimResponse(
            claim_id=claim_id,
            status=digital_twin.current_state.value,
            complexity_score=complexity.total_score,
            claim_type=cognitive_structure.claim_type.value,
            is_escalated=digital_twin.is_escalated,
            summary=client_summary.model_dump()
        )
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

# ===== ENDPOINTS CONVERSATION (WebSocket) =====

@app.websocket("/ws/conversation/{session_id}")
async def websocket_conversation(websocket: WebSocket, session_id: str):
    """
    WebSocket pour conversation temps réel
    Flux: Client STT → Backend Analyse → TTS → Client
    """
    print(f"🔌 WebSocket: Connexion tentée pour session {session_id}")
    
    try:
        await websocket.accept()
        print(f"✅ WebSocket: Connexion acceptée pour {session_id}")
    except Exception as e:
        print(f"❌ WebSocket: Erreur accept - {e}")
        return
    
    try:
        # Initialiser une session de conversation
        print(f"📝 WebSocket: Création du claim...")
        claim_id = f"CLM-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
        digital_twin = ClaimDigitalTwin(
            claim_id=claim_id,
            current_state=ClaimState.RECEIVED,
            timestamp=datetime.now()
        )
        
        print(f"🧠 WebSocket: Initialisation du ConversationManager...")
        conversation_manager = ConversationManager(digital_twin)
        active_sessions[session_id] = {
            "claim_id": claim_id,
            "manager": conversation_manager,
            "history": [],
            "saved": False
        }
        
        # Accueil initial
        print(f"🔊 WebSocket: Initialisation du TTSEngine...")
        tts_engine = TTSEngine(language="fr")
        print(f"✅ TTS engine type: {tts_engine.engine}")
        
        greeting = conversation_manager.get_greeting_prompt()
        
        # Générer l'audio TTS
        audio_path = generate_tts_audio(greeting, tts_engine)
        
        print(f"📤 WebSocket: Envoi du greeting...")
        response_data = {
            "type": "greeting",
            "message": greeting,
            "claim_id": claim_id
        }
        
        if audio_path:
            # Convertir le chemin en URL relative servie par /audio/{filename}
            filename = Path(audio_path).name
            audio_url = f"/audio/{filename}"
            response_data["audio_url"] = audio_url
            print(f"🔊 Audio TTS inclus: {audio_url}")
        
        await websocket.send_json(response_data)
        print(f"✅ WebSocket: Greeting envoyé!")
        
        conversation_manager.current_phase = ConversationPhase.LISTEN
        
        # Boucle de conversation
        while True:
            try:
                data = await websocket.receive_json()
            except Exception as e:
                print(f"WebSocket closed: {e}")
                break
            
            if data["type"] == "user_text":
                user_text = data["text"]
                
                # STT simulé (texte déjà transcrit par frontend)
                from models.claim_models import TranscriptMetadata
                metadata = TranscriptMetadata(
                    original_transcript=user_text,
                    normalized_transcript=user_text,
                    language="fr",
                    confidence_score=0.95,
                    emotional_markers=[],
                    hesitations=0,
                    duration_seconds=30.0
                )
                
                manager = active_sessions[session_id]["manager"]
                
                # Traitement selon la phase actuelle
                if manager.current_phase == ConversationPhase.LISTEN:
                    # Analyse cognitive
                    cognitive_engine = CognitiveClaimEngine(use_llm=False)
                    cognitive_analysis = cognitive_engine.analyze_claim(metadata)
                    
                    ack_text, summary_text, next_q = manager.process_accident_description(
                        user_text,
                        {
                            "claim_type": cognitive_analysis.claim_type.value,
                            "location": cognitive_analysis.location or "lieu non précisé",
                            "damages": cognitive_analysis.damages_description,
                            "emotional_stress": cognitive_analysis.emotional_stress_level
                        }
                    )
                    
                    response_text = f"{ack_text}\n\n{summary_text}\n\n{next_q}"
                    audio_path = generate_tts_audio(response_text, tts_engine)
                    audio_url = build_audio_url(audio_path)
                    
                    await websocket.send_json({
                        "type": "response",
                        "acknowledge": ack_text,
                        "summary": summary_text,
                        "next_question": next_q,
                        "phase": manager.current_phase.value,
                        "audio_url": audio_url
                    })
                
                elif manager.current_phase == ConversationPhase.ASK_CALLER_ID:
                    next_q = manager.process_caller_identification(user_text)
                    
                    response_text = f"Merci. {next_q}"
                    audio_path = generate_tts_audio(response_text, tts_engine)
                    audio_url = build_audio_url(audio_path)
                    
                    await websocket.send_json({
                        "type": "response",
                        "next_question": next_q,
                        "phase": manager.current_phase.value,
                        "message": response_text,
                        "audio_url": audio_url
                    })
                
                elif manager.current_phase == ConversationPhase.ASK_VEHICLE:
                    next_q = manager.process_vehicle_info(user_text)
                    
                    response_text = f"Parfait. {next_q}"
                    audio_path = generate_tts_audio(response_text, tts_engine)
                    audio_url = build_audio_url(audio_path)
                    
                    await websocket.send_json({
                        "type": "response",
                        "next_question": next_q,
                        "phase": manager.current_phase.value,
                        "message": response_text,
                        "audio_url": audio_url
                    })
                
                elif manager.current_phase == ConversationPhase.ASK_NAME:
                    next_q = manager.process_name_confirmation(user_text)
                    
                    response_text = f"Très bien, {user_text}. {next_q}"
                    audio_path = generate_tts_audio(response_text, tts_engine)
                    audio_url = build_audio_url(audio_path)
                    
                    await websocket.send_json({
                        "type": "response",
                        "next_question": next_q,
                        "phase": manager.current_phase.value,
                        "message": response_text,
                        "audio_url": audio_url
                    })
                
                elif manager.current_phase == ConversationPhase.ASK_CIN:
                    closing_q = manager.process_cin(user_text)
                    
                    response_text = f"Merci. Toutes les informations requises ont été collectées. {closing_q}"
                    audio_path = generate_tts_audio(response_text, tts_engine)
                    audio_url = build_audio_url(audio_path)
                    
                    await websocket.send_json({
                        "type": "response",
                        "next_question": closing_q,
                        "phase": manager.current_phase.value,
                        "message": response_text,
                        "completed": True,
                        "audio_url": audio_url
                    })

                    # 🔍 Analyse + Classification + Ajout CRM (après collecte complète)
                    try:
                        session = active_sessions.get(session_id, {})
                        if not session.get("saved"):
                            collected = manager.get_collected_data()
                            accident_text = collected.get("accident_description") or ""

                            from models.claim_models import TranscriptMetadata

                            transcript = TranscriptMetadata(
                                original_transcript=accident_text,
                                normalized_transcript=accident_text.strip(),
                                language="fr",
                                confidence_score=0.95,
                                emotional_markers=[],
                                hesitations=0,
                                duration_seconds=60.0
                            )

                            cognitive_engine = CognitiveClaimEngine(use_llm=False)
                            cognitive_structure = cognitive_engine.analyze_claim(transcript)

                            complexity_calc = ComplexityCalculator()
                            complexity = complexity_calc.calculate(cognitive_structure)

                            digital_twin.transcript_metadata = transcript
                            digital_twin.cognitive_structure = cognitive_structure
                            digital_twin.complexity = complexity

                            # Décision automatique
                            decision_engine = DecisionEngine()
                            should_escalate, reason, action = decision_engine.make_decision(digital_twin)
                            if should_escalate:
                                digital_twin.escalate(reason)
                            else:
                                digital_twin.change_state(ClaimState.AUTONOMOUS, reason)

                            # Sauvegarde CRM
                            crm = get_crm()
                            crm.create_claim(digital_twin)
                            session["saved"] = True
                    except Exception as e:
                        print(f"❌ Erreur sauvegarde sinistre conversation: {e}")
                
                else:
                    # Réponse finale
                    await websocket.send_json({
                        "type": "response",
                        "message": "Merci pour ces informations. Votre dossier est maintenant complet et sera traité rapidement.",
                        "completed": True
                    })
                
                # Enregistrer dans historique
                active_sessions[session_id]["history"].append({
                    "speaker": "client",
                    "text": user_text,
                    "timestamp": datetime.now().isoformat()
                })
            
            elif data["type"] == "close":
                break
    
    except Exception as e:
        print(f"WebSocket error: {e}")
        try:
            await websocket.send_json({"type": "error", "message": str(e)})
        except:
            pass  # La connexion est déjà fermée
    
    finally:
        if session_id in active_sessions:
            del active_sessions[session_id]

# ===== ENDPOINTS CRM & STATISTIQUES =====

@app.get("/api/claims")
def list_claims(limit: int = 50, escalated_only: bool = False):
    """Récupérer la liste des sinistres"""
    try:
        crm = get_crm()
        claims = crm.list_claims(
            escalated_only=escalated_only,
            limit=limit
        )
        
        return {
            "total": len(claims),
            "claims": [
                {
                    "claim_id": c.claim_id,
                    "status": c.current_state.value,
                    "complexity": c.complexity.total_score,
                    "is_escalated": c.is_escalated,
                    "created_at": c.created_at.isoformat()
                }
                for c in claims
            ]
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/claims/{claim_id}")
def get_claim(claim_id: str):
    """Récupérer les détails d'un sinistre"""
    try:
        crm = get_crm()
        claim = crm.get_claim(claim_id)
        
        if not claim:
            raise HTTPException(status_code=404, detail="Sinistre non trouvé")
        
        return {
            "claim_id": claim.claim_id,
            "status": claim.current_state.value,
            "complexity": claim.complexity.total_score,
            "is_escalated": claim.is_escalated,
            "claim_type": claim.cognitive_structure.claim_type.value,
            "created_at": claim.created_at.isoformat()
        }
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/statistics")
def get_statistics():
    """Obtenir les statistiques globales"""
    try:
        crm = get_crm()
        stats = crm.get_statistics()
        
        return {
            "total_claims": stats.get("total_claims", 0),
            "escalated_count": stats.get("escalated_count", 0),
            "avg_complexity": stats.get("avg_complexity", 0),
            "by_state": stats.get("by_state", {})
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/test-tts")
def test_tts_engine():
    """Test du moteur TTS (debug)"""
    try:
        tts = TTSEngine(language="fr")
        return {
            "engine": tts.engine,
            "elevenlabs_key_loaded": bool(tts.elevenlabs_key),
            "status": "OK"
        }
    except Exception as e:
        return {
            "engine": "error",
            "error": str(e),
            "status": "FAILED"
        }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
