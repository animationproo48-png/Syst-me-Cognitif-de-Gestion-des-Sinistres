"""
Application Microphone Haute Qualité - Mode Dialogue LAMA
Enregistrement direct en WAV sans compression (comme les fichiers uploadés)
"""

import streamlit as st
import os
import wave
import pyaudio
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
    page_title="Service Gestion Sinistre - Microphone",
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
    st.session_state.recording = False


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
            st.audio(audio_file, format='audio/wav')


def log_conversation(speaker: str, text: str, audio_path: str = None):
    """Enregistre un tour de conversation"""
    st.session_state.conversation_history.append({
        "timestamp": datetime.now(),
        "speaker": speaker,
        "text": text,
        "audio": audio_path
    })


def record_audio_wav(duration: int = 10, sample_rate: int = 16000):
    """
    Enregistre l'audio directement en WAV haute qualité (16kHz, 16-bit, mono).
    Sans compression WebM comme st.audio_input().
    
    Args:
        duration: Durée maximale en secondes
        sample_rate: Fréquence d'échantillonnage (16000 Hz optimal pour STT)
    
    Returns:
        Chemin du fichier WAV enregistré
    """
    try:
        # Configuration PyAudio
        CHUNK = 1024
        FORMAT = 8  # 16-bit (pyaudio.paInt16)
        CHANNELS = 1  # Mono
        
        audio = pyaudio.PyAudio()
        
        stream = audio.open(
            format=FORMAT,
            channels=CHANNELS,
            rate=sample_rate,
            input=True,
            frames_per_buffer=CHUNK
        )
        
        # Fichier de sortie
        output_path = Path("data/temp") / f"mic_record_{datetime.now().strftime('%H%M%S')}.wav"
        output_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Enregistrement
        st.info(f"🎤 Enregistrement en cours ({duration}s)...")
        frames = []
        
        for _ in range(0, int(sample_rate / CHUNK * duration)):
            try:
                data = stream.read(CHUNK, exception_on_overflow=False)
                frames.append(data)
            except:
                break
        
        stream.stop_stream()
        stream.close()
        audio.terminate()
        
        # Sauvegarde WAV
        with wave.open(str(output_path), 'wb') as wf:
            wf.setnchannels(CHANNELS)
            wf.setsampwidth(audio.get_sample_size(FORMAT))
            wf.setframerate(sample_rate)
            wf.writeframes(b''.join(frames))
        
        st.success(f"✅ Enregistrement sauvegardé: {output_path.stat().st_size} bytes")
        return str(output_path)
        
    except Exception as e:
        st.error(f"❌ Erreur microphone: {e}")
        st.info("💡 Conseil: Utilisez app_upload.py pour uploader des fichiers pré-enregistrés")
        return None


# ===== INTERFACE PRINCIPALE =====

st.title("🎙️ Service Gestion Sinistre - Microphone Haute Qualité")
st.markdown("""
Système conversationnel LAMA interactif - Enregistrement direct
- **Enregistrez** directement via microphone (WAV haute qualité)
- **Transcription** automatique en français
- **Analyse** cognitive du sinistre
- **Dialogue** LAMA avec réponses vocales

**💡 Conseil**: Pour meilleure qualité, préférez [app_upload.py](http://localhost:8501?app=app_upload.py) (upload de fichiers)
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
            
            status.update(label="✅ Accueil terminé - En attente de votre enregistrement", state="complete")

with col2:
    if st.button("❌ Fermer conversation", key="end_conversation", use_container_width=True):
        st.session_state.conversation_active = False
        st.session_state.session_initialized = False
        st.info("Conversation fermée. Cliquez sur 'Lancer' pour recommencer.")


# ===== SECTION 2: ENREGISTREMENT MICROPHONE =====
if st.session_state.session_initialized and st.session_state.conversation_active:
    st.divider()
    st.subheader("🎤 Enregistrement Microphone")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        duration = st.slider("Durée maximale (secondes)", 5, 60, 15)
    
    with col2:
        if st.button("🔴 Démarrer enregistrement", key="record_btn", use_container_width=True):
            st.session_state.recording = True
    
    with col3:
        if st.button("⏹️ Arrêter enregistrement", key="stop_btn", use_container_width=True):
            st.session_state.recording = False
    
    if st.session_state.recording:
        audio_file = record_audio_wav(duration=duration)
        st.session_state.recording = False
        
        if audio_file:
            # Étape 2: STT
            with st.status("🔄 Traitement...", expanded=True) as status:
                st.write("📝 Transcription en cours...")
                
                stt_engine = STTEngine()
                metadata = stt_engine.transcribe_audio(audio_file)
                
                st.write(f"✅ Langue détectée: **{metadata.language}**")
                st.write(f"📝 Transcription originale: **{metadata.original_transcript[:100]}...**")
                st.write(f"📝 Transcription traduite: **{metadata.normalized_transcript[:100]}...**")
                
                user_text = metadata.normalized_transcript
                log_conversation("Client", user_text, audio_file)
                
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
                    st.audio(open(ack_audio, 'rb'), format='audio/mp3')
                    log_conversation("System", ack_text, str(ack_audio))
                    
                    # MAKE STATEMENT
                    st.write(f"\n2️⃣ **Résumé**: {summary_text}")
                    summary_audio = Path("data/audio_responses") / f"summary_{datetime.now().strftime('%H%M%S')}.mp3"
                    tts_engine.synthesize(summary_text, str(summary_audio), tone="professional")
                    st.audio(open(summary_audio, 'rb'), format='audio/mp3')
                    log_conversation("System", summary_text, str(summary_audio))
                    
                    # ASK QUESTIONS
                    st.write(f"\n3️⃣ **Question**: {next_q}")
                    question_audio = Path("data/audio_responses") / f"q_{datetime.now().strftime('%H%M%S')}.mp3"
                    tts_engine.synthesize(next_q, str(question_audio), tone="professional")
                    st.audio(open(question_audio, 'rb'), format='audio/mp3')
                    log_conversation("System", next_q, str(question_audio))
                
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


# ===== SECTION 3: HISTORIQUE =====
if st.session_state.conversation_history:
    st.divider()
    st.subheader("📋 Historique de conversation")
    
    for item in st.session_state.conversation_history:
        with st.expander(f"{item['timestamp'].strftime('%H:%M:%S')} - {item['speaker']}"):
            st.write(f"**{item['speaker']}**: {item['text']}")
            if item['audio']:
                try:
                    st.audio(item['audio'])
                except:
                    st.write(f"Audio: {item['audio']}")

load_dotenv()
