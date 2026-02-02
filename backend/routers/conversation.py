# backend/routers/conversation.py

from fastapi import APIRouter, Depends, WebSocket, WebSocketDisconnect, HTTPException
from sqlalchemy.orm import Session
from uuid import UUID
import json
import logging
import sys
from pathlib import Path
from datetime import datetime
from decimal import Decimal

# Import from parent directory
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from backend.database import get_db, SessionLocal
from backend.models import (
    ClientDB, SinistreDB, HistoriqueConversationDB, RemboursementDB,
    ActionRecommandeeDB, ConseillerDB, EscaladeDB, ContratDB
)
from backend.schemas.schemas import ConversationPhaseResponse, MessageRequest
from modules.conversation_manager_crm import ConversationManager
from modules.tts_module import TTSEngine

router = APIRouter(tags=["Conversation"])
logger = logging.getLogger(__name__)

active_conversations = {}
tts_engine = TTSEngine(language="fr", voice="george")


def extract_and_normalize_matricule(text: str) -> list:
    """
    Extrait et normalise le matricule d'une phrase.
    Retourne une liste de formats possibles.
    
    Exemples:
    - "AB 45, 21, 22" -> ["AB-4521-22", "AB452122"]
    - "mon matricule est FC 7834 19" -> ["FC-7834-19", "FC783419"]
    - "AB452122" -> ["AB-4521-22", "AB452122"]
    """
    import re
    
    # Nettoyer le texte
    text = text.upper().strip()
    
    # PATTERN 1: Lettres suivies IMMÉDIATEMENT de chiffres (ex: AB452122)
    # Chercher 2 lettres IMMÉDIATEMENT suivies de 6 chiffres ou plus
    compact_match = re.search(r'([A-Z]{2})(\d{6,})', text)
    
    if compact_match:
        letters = compact_match.group(1)
        all_digits = compact_match.group(2)[:6]  # Prendre les 6 premiers chiffres
        middle = all_digits[:4]
        end = all_digits[4:6]
        
        formats = []
        formats.append(f"{letters}-{middle}-{end}")  # AB-4521-22
        formats.append(f"{letters}{middle}{end}")    # AB452122
        formats.append(f"{letters} {middle} {end}")  # AB 4521 22
        return formats
    
    # PATTERN 2: Lettres séparées des chiffres (ex: AB 45 21 22)
    # Autoriser uniquement séparateurs non alphanumériques entre lettres et chiffres
    spaced_match = re.search(r'([A-Z]{2})[^0-9A-Z]{0,6}(\d+(?:[^0-9]+\d+)*)', text)

    if not spaced_match:
        return []

    letters = spaced_match.group(1)
    digits_block = spaced_match.group(2)

    # Extraire tous les chiffres après les lettres
    digits = re.findall(r'\d+', digits_block)
    
    if not digits:
        return []
    
    # Concaténer tous les chiffres
    all_digits = ''.join(digits)
    
    # Vérifier qu'on a bien au moins 4 chiffres
    if len(all_digits) < 4:
        return []
    
    # Prendre les 4 premiers chiffres et les 2 derniers
    if len(all_digits) >= 6:
        middle = all_digits[:4]
        end = all_digits[4:6]
    else:
        middle = all_digits[:4]
        end = all_digits[4:].zfill(2) if len(all_digits) > 4 else "00"
    
    formats = []
    formats.append(f"{letters}-{middle}-{end}")  # AB-4521-22
    formats.append(f"{letters}{middle}{end}")    # AB452122
    formats.append(f"{letters} {middle} {end}")  # AB 4521 22
    
    return formats


def generate_audio_url(text: str) -> str:
    """Generate audio file and return URL"""
    try:
        audio_path = tts_engine.synthesize(text, tone="professional")
        if audio_path:
            filename = Path(audio_path).name
            return f"http://localhost:8000/audio/{filename}"
    except Exception as e:
        logger.error(f"TTS Error: {e}")
    return None


# ============================================================
# PHASE 1: AUTHENTIFICATION
# ============================================================
@router.post("/api/v1/conversation/authenticate")
async def authenticate(payload: MessageRequest, db: Session = Depends(get_db)):
    """Vérifier matricule - PHASE 1: AUTHENTIFICATION"""
    matricule = (payload.text or "").strip()
    if not matricule:
        raise HTTPException(status_code=400, detail="Matricule requis")

    client = db.query(ClientDB).filter(ClientDB.matricule == matricule).first()
    
    if not client:
        return {
            "valide": False,
            "message": f"Matricule {matricule} non trouvé",
            "client": None
        }
    
    active_sinistres = db.query(SinistreDB).filter(
        SinistreDB.client_id == client.id,
        SinistreDB.status_dossier != "fermé"
    ).all()
    
    return {
        "valide": True,
        "message": f"Client trouvé: {client.nom} {client.prenom}",
        "client": {
            "id": str(client.id),
            "matricule": client.matricule,
            "nom": client.nom,
            "prenom": client.prenom,
            "email": client.email,
            "telephone": client.telephone
        },
        "dossiers_actifs": len(active_sinistres),
        "sinistres": [
            {
                "numero": s.numero_sinistre,
                "type": s.type_sinistre,
                "status": s.status_dossier,
                "id": str(s.id)
            }
            for s in active_sinistres
        ]
    }


# ============================================================
# WEBSOCKET - CONVERSATION COMPLÈTE
# ============================================================
@router.websocket("/ws/conversation/{session_id}")
async def websocket_conversation_endpoint(websocket: WebSocket, session_id: str):
    """WebSocket conversation - 7 PHASES"""
    await websocket.accept()
    logger.info(f"🔗 Client connecté: {session_id}")
    db = SessionLocal()

    try:
        # Initialiser manager
        conv_manager = ConversationManager(session_id)
        active_conversations[session_id] = conv_manager

        # État conversation
        state = {
            "phase": "AUTHENTIFICATION",
            "client_id": None,
            "client_data": None,
            "sinistre_id": None,
            "contexte": {
                "questions": [],
                "question_index": 0,
                "details_reponses": []
            }
        }

        # PHASE 1: AUTHENTIFICATION - Demander matricule
        greeting = conv_manager.get_greeting()
        greeting_text = greeting.get("message")
        await websocket.send_json({
            "phase": "AUTHENTIFICATION",
            "message": greeting_text,
            "audio_url": generate_audio_url(greeting_text),
            "action": "demander_matricule"
        })

        while True:
            # Recevoir input utilisateur
            data = await websocket.receive_text()
            try:
                user_input = json.loads(data)
                user_text = user_input.get("text", "").strip()
            except json.JSONDecodeError:
                user_text = data.strip()

            logger.info(f"📥 Phase {state['phase']}: {user_text[:50]}")

            # === PHASE 1: AUTHENTIFICATION ===
            if state["phase"] == "AUTHENTIFICATION":
                # Extraire et normaliser le matricule
                possible_formats = extract_and_normalize_matricule(user_text)
                logger.info(f"🔍 Formats testés: {possible_formats}")
                
                client = None
                matched_format = None
                
                # Essayer chaque format
                for format_test in possible_formats:
                    client = db.query(ClientDB).filter(ClientDB.matricule == format_test).first()
                    if client:
                        matched_format = format_test
                        logger.info(f"✅ Matricule trouvé: {matched_format}")
                        break

                if not client:
                    error_msg = "Je n'ai pas trouvé ce matricule. Pouvez-vous vérifier et réessayer?"
                    await websocket.send_json({
                        "phase": "AUTHENTIFICATION",
                        "message": error_msg,
                        "audio_url": generate_audio_url(error_msg),
                        "action": "redemander_matricule"
                    })
                    continue

                state["client_id"] = client.id
                state["client_data"] = {
                    "id": str(client.id),
                    "matricule": client.matricule,
                    "nom": client.nom,
                    "prenom": client.prenom
                }

                # Demander confirmation d'identité
                state["phase"] = "CONFIRMATION"
                confirm_msg = f"Merci! Vous êtes bien {client.nom} {client.prenom}?"
                await websocket.send_json({
                    "phase": "CONFIRMATION",
                    "message": confirm_msg,
                    "audio_url": generate_audio_url(confirm_msg),
                    "action": "confirmer_identite"
                })
                continue

            # === PHASE CONFIRMATION IDENTITÉ ===
            elif state["phase"] == "CONFIRMATION":
                confirmation = user_text.lower().strip()
                positive_phrases = {
                    "oui", "yes", "ouais", "ok", "d'accord", "daccord", "correct",
                    "c'est moi", "c est moi", "c'est bien moi", "c est bien moi",
                    "c'est moi oui", "c est moi oui", "c'est bien moi oui", "c est bien moi oui",
                    "oui c'est moi", "oui c est moi", "oui c'est bien moi", "oui c est bien moi",
                    "oui je confirme", "je confirme", "je confirme oui", "confirmé",
                    "oui c'est bien moi", "oui c'est bien", "bien sûr", "bien sur",
                    "absolument", "exact", "exactement", "c'est exact", "c est exact",
                    "oui c'est exact", "oui c est exact", "oui exact", "c'est ça", "c est ça",
                    "oui c'est ça", "oui c est ça", "oui bien", "oui c'est bien",
                    "yes it's me", "yes its me", "it's me", "its me", "that's me", "that is me",
                    "yes that's me", "yes thats me", "yes that is me", "i confirm", "i do", "correct"
                }
                if confirmation in positive_phrases or "it" in confirmation and "me" in confirmation:
                    # Si dossiers actifs, proposer suivi
                    active_sinistres = db.query(SinistreDB).filter(
                        SinistreDB.client_id == state["client_id"],
                        SinistreDB.status_dossier != "fermé"
                    ).all()

                    if active_sinistres:
                        state["phase"] = "SUIVI"
                        suivi_msg = conv_manager.suivi_dossier(active_sinistres, db)
                        await websocket.send_json({
                            "phase": "SUIVI",
                            "message": suivi_msg,
                            "audio_url": generate_audio_url(suivi_msg),
                            "action": "suivi_dossier",
                            "sinistres": [
                                {
                                    "id": str(s.id),
                                    "numero": s.numero_sinistre,
                                    "type": s.type_sinistre,
                                    "status": s.status_dossier
                                }
                                for s in active_sinistres
                            ]
                        })
                        break

                    state["phase"] = "DESCRIPTION"
                    desc_prompt = conv_manager.ask_description()
                    await websocket.send_json({
                        "phase": "DESCRIPTION",
                        "message": desc_prompt,
                        "audio_url": generate_audio_url(desc_prompt),
                        "action": "demander_description"
                    })
                else:
                    state["phase"] = "AUTHENTIFICATION"
                    retry_msg = "D'accord, recommençons. Quel est votre numéro de matricule?"
                    await websocket.send_json({
                        "phase": "AUTHENTIFICATION",
                        "message": retry_msg,
                        "audio_url": generate_audio_url(retry_msg),
                        "action": "redemander_matricule"
                    })
                continue

            # === PHASE 2: DESCRIPTION ===
            elif state["phase"] == "DESCRIPTION":
                state["contexte"]["description"] = user_text
                result = conv_manager.analyser_description(user_text)

                state["contexte"].update(result)
                state["contexte"]["questions"] = result.get("next_questions", [])
                state["contexte"]["question_index"] = 0
                state["phase"] = "SINISTRE_DETAILS"

                await websocket.send_json({
                    "phase": "SINISTRE_DETAILS",
                    "message": result.get("message"),
                    "audio_url": None,
                    "type_sinistre": result.get("type_sinistre"),
                    "cci_score": result.get("cci_score", 0)
                })

            # === PHASE 3: SINISTRE_DETAILS ===
            elif state["phase"] == "SINISTRE_DETAILS":
                state["contexte"]["details_reponses"].append(user_text)
                cci_increment = conv_manager.calculer_cci_incremental(user_text)
                state["contexte"]["cci_score"] = state["contexte"].get("cci_score", 0) + cci_increment

                state["contexte"]["question_index"] += 1
                questions = state["contexte"].get("questions", [])
                idx = state["contexte"].get("question_index", 0)

                if idx < len(questions):
                    await websocket.send_json({
                        "phase": "SINISTRE_DETAILS",
                        "message": questions[idx],
                        "audio_url": None,
                        "cci_score": state["contexte"].get("cci_score", 0)
                    })
                    continue

                state["phase"] = "DOCUMENTS"

                await websocket.send_json({
                    "phase": "DOCUMENTS",
                    "message": conv_manager.demander_documents(),
                    "audio_url": None,
                    "cci_score": state["contexte"].get("cci_score", 0)
                })

            # === PHASE 4: DOCUMENTS ===
            elif state["phase"] == "DOCUMENTS":
                state["contexte"]["documents_status"] = user_text
                state["contexte"]["documents_complets"] = True

                # === PHASE 5: DECISION ===
                final_cci = state["contexte"].get("cci_score", 0)
                type_traitement = "escalade" if final_cci > 60 else "autonome"

                # Créer sinistre
                numero_sinistre = f"SINS-{datetime.utcnow().strftime('%Y%m%d%H%M%S')}"
                sinistre = SinistreDB(
                    client_id=state["client_id"],
                    numero_sinistre=numero_sinistre,
                    type_sinistre=state["contexte"].get("type_sinistre", "collision"),
                    date_sinistre=datetime.utcnow().date(),
                    description=state["contexte"].get("description", ""),
                    cci_score=final_cci,
                    status_dossier="escalade" if type_traitement == "escalade" else "nouveau",
                    type_traitement=type_traitement,
                    documents_complets=True
                )
                db.add(sinistre)
                db.commit()
                db.refresh(sinistre)

                state["sinistre_id"] = str(sinistre.id)

                if final_cci > 60:
                    # ESCALADE
                    conseiller = db.query(ConseillerDB).filter(ConseillerDB.statut == "disponible").first()
                    escalade = EscaladeDB(
                        sinistre_id=sinistre.id,
                        conseiller_id=conseiller.id if conseiller else None,
                        raison_escalade="CCI > 60",
                        cci_score_trigger=final_cci,
                        status="en_attente",
                        date_escalade=datetime.utcnow()
                    )
                    db.add(escalade)
                    db.commit()

                    await websocket.send_json({
                        "phase": "TRANSFERT",
                        "message": conv_manager.preparer_transfert(numero_sinistre),
                        "audio_url": None,
                        "action": "transferer_conseiller",
                        "cci_score": final_cci,
                        "raison": "CCI > 60",
                        "sinistre_id": str(sinistre.id)
                    })
                else:
                    # AUTONOME
                    await websocket.send_json({
                        "phase": "SUIVI",
                        "message": conv_manager.suivi_message_autonome(numero_sinistre),
                        "audio_url": None,
                        "action": "fin_autonome",
                        "cci_score": final_cci,
                        "type_traitement": "autonome",
                        "sinistre_id": str(sinistre.id)
                    })

                break

    except WebSocketDisconnect:
        logger.info(f"❌ Client déconnecté: {session_id}")
        active_conversations.pop(session_id, None)
    except Exception as e:
        logger.error(f"❌ Erreur WebSocket: {e}")
        try:
            await websocket.send_json({
                "phase": "ERROR",
                "message": "Une erreur s'est produite",
                "error": str(e)
            })
        except:
            pass
    finally:
        db.close()
