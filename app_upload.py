"""
Application Upload Audio - Mode Dialogue LAMA
Ancien système avec upload de fichier audio (fonctionnait bien)
"""

import streamlit as st
import os
from pathlib import Path
from datetime import datetime
from dotenv import load_dotenv

# Imports métier
from modules.stt_module import STTEngine
from modules.tts_module import TTSEngine
from modules.cognitive_engine import CognitiveClaimEngine
from modules.conversation_manager import ConversationManager, ConversationPhase
from models.claim_models import ClaimDigitalTwin, ClaimState

# Configuration Streamlit
st.set_page_config(
    page_title="Service Gestion Sinistre - Upload Audio",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialisation session state
if "session_initialized" not in st.session_state:
    st.session_state.session_initialized = False
    st.session_state.conversation_active = False
    st.session_state.digital_twin = None
    st.session_state.conversation_manager = None
    st.session_state.conversation_history = []
    st.session_state.current_phase = None


def initialize_session():
    """Initialise une nouvelle session de conversation"""
    claim_id = f"CLM-{datetime.now().strftime('%Y%m%d-%H%M%S')}"
    
    # Créer le Digital Twin
    digital_twin = ClaimDigitalTwin(
        claim_id=claim_id,
        current_state=ClaimState.RECEIVED,
        timestamp=datetime.now()
    )
    
    # Initialiser le gestionnaire de conversation
    conversation_manager = ConversationManager(digital_twin)
    
    st.session_state.digital_twin = digital_twin
    st.session_state.conversation_manager = conversation_manager
    st.session_state.conversation_active = True
    st.session_state.session_initialized = True
    st.session_state.claim_id = claim_id
    st.session_state.conversation_history = []
    
    return digital_twin, conversation_manager, claim_id


def play_audio(audio_path):
    """Joue un fichier audio"""
    if audio_path and os.path.exists(audio_path):
        with open(audio_path, 'rb') as audio_file:
            st.audio(audio_file, format='audio/mp3')


def log_conversation(speaker: str, text: str, audio_path: str = None):
    """Enregistre un tour de conversation"""
    st.session_state.conversation_history.append({
        "timestamp": datetime.now(),
        "speaker": speaker,
        "text": text,
        "audio": audio_path
    })


# ===== INTERFACE PRINCIPALE =====

st.title("🎙️ Service Gestion Sinistre - Upload Audio")
st.markdown("""
Système conversationnel LAMA interactif - Mode Upload
- **Uploadez** votre fichier audio
- **Transcription** automatique en français
- **Analyse** cognitive du sinistre
- **Dialogue** LAMA avec réponses vocales
""")

# ===== SECTION 1: INITIALISATION =====
col1, col2 = st.columns(2)

with col1:
    if st.button("🎙️ Lancer une conversation", key="start_conversation", use_container_width=True):
        digital_twin, conv_manager, claim_id = initialize_session()
        
        with st.status("🎙️ Session initialisée...", expanded=True) as status:
            st.write(f"✅ Claim ID: `{claim_id}`")
            st.write(f"✅ État: {digital_twin.current_state.value}")
            
            # Étape 1: Accueil TTS
            st.write("\n📢 **Accueil vocal...**")
            tts_engine = TTSEngine(language="fr")
            greeting_text = conv_manager.get_greeting_prompt()
            
            greeting_audio = Path("data/audio_responses") / f"greeting_{claim_id}.mp3"
            greeting_audio.parent.mkdir(parents=True, exist_ok=True)
            tts_engine.synthesize(greeting_text, str(greeting_audio), tone="professional")
            
            st.write(f"🎙️ **Système**: {greeting_text}")
            play_audio(str(greeting_audio))
            
            log_conversation("System", greeting_text, str(greeting_audio))
            
            # Passer à la phase LISTEN après le greeting
            conv_manager.current_phase = ConversationPhase.LISTEN
            
            status.update(label="✅ Accueil terminé - En attente de votre fichier audio", state="complete")
        
        st.rerun()  # Forcer le refresh pour afficher la section upload

with col2:
    if st.button("❌ Fermer conversation", key="end_conversation", use_container_width=True):
        st.session_state.conversation_active = False
        st.session_state.session_initialized = False
        st.info("Conversation fermée. Cliquez sur 'Lancer' pour recommencer.")


# ===== SECTION 2: UPLOAD AUDIO =====
if st.session_state.session_initialized and st.session_state.conversation_active:
    st.divider()
    st.subheader("📁 Uploadez votre fichier audio")
    
    uploaded_audio = st.file_uploader(
        "Sélectionnez un fichier audio (MP3, WAV, OGG, M4A, WebM)",
        type=["mp3", "wav", "ogg", "m4a", "webm"],
        key="audio_upload"
    )
    
    if uploaded_audio is not None:
        # Sauvegarder le fichier uploadé
        temp_audio = Path("data/temp") / f"upload_{datetime.now().strftime('%H%M%S')}.{uploaded_audio.name.split('.')[-1]}"
        temp_audio.parent.mkdir(parents=True, exist_ok=True)
        
        with open(temp_audio, 'wb') as f:
            f.write(uploaded_audio.getbuffer())
        
        st.success(f"✅ Fichier reçu: {uploaded_audio.name} ({uploaded_audio.size} bytes)")
        
        # Étape 2: STT
        with st.status("🔄 Traitement...", expanded=True) as status:
            st.write("📝 Transcription en cours...")
            
            stt_engine = STTEngine()
            metadata = stt_engine.transcribe_audio(str(temp_audio))
            
            st.write(f"✅ Langue détectée: **{metadata.language}**")
            st.write(f"📝 Transcription originale: **{metadata.original_transcript[:100]}...**")
            st.write(f"📝 Transcription traduite: **{metadata.normalized_transcript[:100]}...**")
            
            user_text = metadata.normalized_transcript
            log_conversation("Client", user_text, str(temp_audio))
            
            # Étape 3: Analyse cognitive
            st.write("\n🧠 Analyse cognitive en cours...")
            
            conv_manager = st.session_state.conversation_manager
            
            cognitive_engine = CognitiveClaimEngine()
            cognitive_analysis = cognitive_engine.analyze_claim(metadata)
            
            st.write(f"✅ Type de sinistre: {cognitive_analysis.claim_type.value}")
            st.write(f"✅ Stress émotionnel: {cognitive_analysis.emotional_stress_level}/10")
            st.write(f"✅ Phase actuelle: {conv_manager.current_phase.value}")
            
            # Étape 4: Gestion conversation LAMA
            st.write("\n💬 Réponse du système (méthode LAMA)...")
            
            # Selon la phase actuelle
            if conv_manager.current_phase == ConversationPhase.GREETING:
                # Si encore en phase GREETING, passer à LISTEN
                conv_manager.current_phase = ConversationPhase.LISTEN
            
            if conv_manager.current_phase == ConversationPhase.LISTEN:
                ack_text, summary_text, next_q = conv_manager.process_accident_description(
                    user_text,
                    {
                        "claim_type": cognitive_analysis.claim_type.value,
                        "location": " / ".join(cognitive_analysis.location or []),
                        "damages": cognitive_analysis.damages_description,
                        "emotional_stress": cognitive_analysis.emotional_stress_level
                    }
                )
                
                # Générer les réponses TTS
                tts_engine = TTSEngine(language="fr")
                
                # ACKNOWLEDGE
                st.write(f"\n1️⃣ **Empathie**: {ack_text}")
                ack_audio = Path("data/audio_responses") / f"ack_{datetime.now().strftime('%H%M%S')}.mp3"
                tts_engine.synthesize(ack_text, str(ack_audio), tone="empathetic")
                play_audio(str(ack_audio))
                log_conversation("System", ack_text, str(ack_audio))
                
                # MAKE STATEMENT
                st.write(f"\n2️⃣ **Résumé**: {summary_text}")
                summary_audio = Path("data/audio_responses") / f"summary_{datetime.now().strftime('%H%M%S')}.mp3"
                tts_engine.synthesize(summary_text, str(summary_audio), tone="professional")
                play_audio(str(summary_audio))
                log_conversation("System", summary_text, str(summary_audio))
                
                # ASK QUESTIONS
                st.write(f"\n3️⃣ **Question**: {next_q}")
                question_audio = Path("data/audio_responses") / f"q_{datetime.now().strftime('%H%M%S')}.mp3"
                tts_engine.synthesize(next_q, str(question_audio), tone="professional")
                play_audio(str(question_audio))
                log_conversation("System", next_q, str(question_audio))
                
            # Phases de collecte d'infos
            elif conv_manager.current_phase == ConversationPhase.ASK_CALLER_ID:
                conv_manager.process_caller_identification(user_text)
                next_q = conv_manager._generate_next_question()
                
                st.write(f"✅ Identité enregistrée: {user_text}")
                st.write(f"\n❓ {next_q}")
                
                tts_engine = TTSEngine(language="fr")
                q_audio = Path("data/audio_responses") / f"q_{datetime.now().strftime('%H%M%S')}.mp3"
                tts_engine.synthesize(next_q, str(q_audio))
                play_audio(str(q_audio))
                log_conversation("System", next_q, str(q_audio))
            
            elif conv_manager.current_phase == ConversationPhase.ASK_VEHICLE:
                conv_manager.process_vehicle_info(user_text)
                next_q = conv_manager._generate_next_question()
                
                st.write(f"✅ Véhicule enregistré: {user_text}")
                st.write(f"\n❓ {next_q}")
                
                tts_engine = TTSEngine(language="fr")
                q_audio = Path("data/audio_responses") / f"q_{datetime.now().strftime('%H%M%S')}.mp3"
                tts_engine.synthesize(next_q, str(q_audio))
                play_audio(str(q_audio))
                log_conversation("System", next_q, str(q_audio))
            
            elif conv_manager.current_phase == ConversationPhase.ASK_NAME:
                conv_manager.process_name_confirmation(user_text)
                next_q = conv_manager._generate_next_question()
                
                st.write(f"✅ Nom enregistré: {user_text}")
                st.write(f"\n❓ {next_q}")
                
                tts_engine = TTSEngine(language="fr")
                q_audio = Path("data/audio_responses") / f"q_{datetime.now().strftime('%H%M%S')}.mp3"
                tts_engine.synthesize(next_q, str(q_audio))
                play_audio(str(q_audio))
                log_conversation("System", next_q, str(q_audio))
            
            elif conv_manager.current_phase == ConversationPhase.ASK_CIN:
                conv_manager.process_cin(user_text)
                closing_q = conv_manager._generate_closing_question()
                
                st.write(f"✅ CIN enregistré: {user_text}")
                st.write(f"\n✅ **Toutes les informations requises ont été collectées!**")
                st.write(f"\n❓ {closing_q}")
                
                tts_engine = TTSEngine(language="fr")
                closing_audio = Path("data/audio_responses") / f"closing_{datetime.now().strftime('%H%M%S')}.mp3"
                tts_engine.synthesize(closing_q, str(closing_audio), tone="professional")
                play_audio(str(closing_audio))
                log_conversation("System", closing_q, str(closing_audio))
            
            status.update(label="✅ Tour terminé", state="complete")
            
            # Afficher le statut actuel
            st.divider()
            st.subheader("📊 Statut de collecte")
            phase_status = conv_manager.get_phase_status()
            
            cols = st.columns(4)
            cols[0].metric("Identifié", "✅" if phase_status["caller_id_collected"] else "⏳")
            cols[1].metric("Véhicule", "✅" if phase_status["vehicle_collected"] else "⏳")
            cols[2].metric("Nom", "✅" if phase_status["name_collected"] else "⏳")
            cols[3].metric("CIN", "✅" if phase_status["cin_collected"] else "⏳")
            
            if phase_status["all_required_info"]:
                st.success("🎉 Tous les champs requis collectés!")
        
        # SECTION 3: ENREGISTREMENT DE LA RÉPONSE EN TEMPS RÉEL
        st.divider()
        st.subheader("🎤 Enregistrez votre réponse (Temps Réel)")
        
        response_audio = st.audio_input(
            "Parlez pour répondre à la dernière question du système:",
            key="response_audio_input"
        )
        
        if response_audio is not None:
            # Sauvegarder la réponse
            temp_response = Path("data/temp") / f"response_{datetime.now().strftime('%H%M%S')}.wav"
            temp_response.parent.mkdir(parents=True, exist_ok=True)
            
            with open(temp_response, 'wb') as f:
                f.write(response_audio.getbuffer())
            
            st.success(f"✅ Réponse reçue ({len(response_audio.getbuffer())} bytes)")
            
            # Traiter la réponse
            with st.status("🔄 Traitement de votre réponse...", expanded=True) as response_status:
                st.write("📝 Transcription en cours...")
                
                stt_engine = STTEngine()
                response_metadata = stt_engine.transcribe_audio(str(temp_response))
                
                response_text = response_metadata.normalized_transcript
                st.write(f"✅ Vous avez dit: **{response_text}**")
                log_conversation("Client", response_text, str(temp_response))
                
                # Analyse et réponse selon la phase
                st.write("\n🧠 Traitement de votre réponse...")
                
                conv_manager = st.session_state.conversation_manager
                
                # Passer à la phase suivante
                if conv_manager.current_phase == ConversationPhase.ASK_CALLER_ID:
                    conv_manager.process_caller_identification(response_text)
                    next_q = conv_manager._generate_next_question()
                    
                    st.write(f"✅ Identité enregistrée")
                    
                elif conv_manager.current_phase == ConversationPhase.ASK_VEHICLE:
                    conv_manager.process_vehicle_info(response_text)
                    next_q = conv_manager._generate_next_question()
                    
                    st.write(f"✅ Véhicule enregistré")
                    
                elif conv_manager.current_phase == ConversationPhase.ASK_NAME:
                    conv_manager.process_name_confirmation(response_text)
                    next_q = conv_manager._generate_next_question()
                    
                    st.write(f"✅ Nom enregistré")
                    
                elif conv_manager.current_phase == ConversationPhase.ASK_CIN:
                    conv_manager.process_cin(response_text)
                    next_q = conv_manager._generate_closing_question()
                    
                    st.write(f"✅ CIN enregistré")
                
                # Générer la réponse du système
                if next_q:
                    st.write(f"\n💬 **Prochaine question**: {next_q}")
                    
                    tts_engine = TTSEngine(language="fr")
                    next_audio = Path("data/audio_responses") / f"next_{datetime.now().strftime('%H%M%S')}.mp3"
                    tts_engine.synthesize(next_q, str(next_audio), tone="professional")
                    play_audio(str(next_audio))
                    log_conversation("System", next_q, str(next_audio))
                
                response_status.update(label="✅ Réponse traitée", state="complete")
                
                # Mettre à jour le statut
                st.divider()
                st.subheader("📊 Statut mis à jour")
                phase_status = conv_manager.get_phase_status()
                
                cols = st.columns(4)
                cols[0].metric("Identifié", "✅" if phase_status["caller_id_collected"] else "⏳")
                cols[1].metric("Véhicule", "✅" if phase_status["vehicle_collected"] else "⏳")
                cols[2].metric("Nom", "✅" if phase_status["name_collected"] else "⏳")
                cols[3].metric("CIN", "✅" if phase_status["cin_collected"] else "⏳")
                
                if phase_status["all_required_info"]:
                    st.success("🎉 Conversation terminée avec succès!")


# ===== SECTION 3: HISTORIQUE =====
if st.session_state.conversation_history:
    st.divider()
    st.subheader("📋 Historique de conversation")
    
    for item in st.session_state.conversation_history:
        with st.expander(f"{item['timestamp'].strftime('%H:%M:%S')} - {item['speaker']}"):
            st.write(f"**{item['speaker']}**: {item['text']}")
            if item['audio']:
                st.audio(item['audio'])

load_dotenv()
