"""
Interface Streamlit pour le Système de Gestion Cognitive des Sinistres.
Interface professionnelle entièrement en français.
"""

import streamlit as st
import uuid
from datetime import datetime
from pathlib import Path
import sys

# Configuration du path
sys.path.append(str(Path(__file__).parent))

# Imports des modules
from modules.stt_module import STTEngine
from modules.tts_module import TTSEngine, create_client_response
from modules.cognitive_engine import CognitiveClaimEngine
from modules.complexity_calculator import ComplexityCalculator
from modules.decision_engine import DecisionEngine
from modules.summary_generator import SummaryGenerator
from modules.crm_system import get_crm
from modules.conversation_manager import ConversationManager, ConversationPhase
from models.claim_models import ClaimDigitalTwin, ClaimState


# Configuration de la page
st.set_page_config(
    page_title="Gestion Cognitive des Sinistres",
    page_icon="🎙️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# CSS personnalisé
st.markdown("""
<style>
    .main-header {
        font-size: 2.5rem;
        color: #1f77b4;
        font-weight: bold;
        text-align: center;
        padding: 1rem;
        background: linear-gradient(90deg, #e3f2fd 0%, #bbdefb 100%);
        border-radius: 10px;
        margin-bottom: 2rem;
    }
    
    .claim-card {
        background-color: #f8f9fa;
        padding: 1.5rem;
        border-radius: 10px;
        border-left: 5px solid #1f77b4;
        margin: 1rem 0;
    }
    
    .metric-card {
        background-color: #ffffff;
        padding: 1rem;
        border-radius: 8px;
        box-shadow: 0 2px 4px rgba(0,0,0,0.1);
        text-align: center;
    }
    
    .complexity-simple {
        color: #4caf50;
        font-weight: bold;
    }
    
    .complexity-moderate {
        color: #ff9800;
        font-weight: bold;
    }
    
    .complexity-complex {
        color: #f44336;
        font-weight: bold;
    }
    
    .complexity-critical {
        color: #9c27b0;
        font-weight: bold;
        animation: blink 1.5s infinite;
    }
    
    @keyframes blink {
        0%, 100% { opacity: 1; }
        50% { opacity: 0.5; }
    }
    
    .stButton>button {
        width: 100%;
        border-radius: 20px;
        font-weight: bold;
    }
</style>
""", unsafe_allow_html=True)


def initialize_session_state():
    """Initialise les variables de session Streamlit"""
    if "crm" not in st.session_state:
        st.session_state.crm = get_crm()
    
    if "current_claim" not in st.session_state:
        st.session_state.current_claim = None
    
    if "processing_complete" not in st.session_state:
        st.session_state.processing_complete = False
    
    if "audio_response_path" not in st.session_state:
        st.session_state.audio_response_path = None


def render_header():
    """Affiche l'en-tête de l'application"""
    st.markdown('<div class="main-header">🎙️ Système Cognitif de Gestion des Sinistres</div>', 
                unsafe_allow_html=True)
    
    st.markdown("""
    <p style='text-align: center; color: #666; font-size: 1.1rem;'>
    <b>Intelligence Artificielle + Voix</b> pour une gestion autonome et expliquable des déclarations de sinistres
    </p>
    """, unsafe_allow_html=True)
    
    st.divider()


def render_sidebar():
    """Affiche la barre latérale avec navigation et statistiques"""
    with st.sidebar:
        st.image("https://via.placeholder.com/200x80/1f77b4/ffffff?text=AssurTech+AI", 
                 use_column_width=True)
        
        st.markdown("### 🎯 Navigation")
        
        page = st.radio(
            "Choisir une section",
            ["🎙️ Nouvelle Déclaration", "� Conversation en temps réel", "�📋 Tableau de Bord CRM", "📊 Statistiques"],
            label_visibility="collapsed"
        )
        
        st.divider()
        
        # Statistiques en temps réel
        st.markdown("### 📈 Statistiques Temps Réel")
        stats = st.session_state.crm.get_statistics()
        
        col1, col2 = st.columns(2)
        with col1:
            st.metric("Total Sinistres", stats.get("total_claims", 0))
        with col2:
            st.metric("Escaladés", stats.get("escalated_count", 0))
        
        if stats.get("avg_complexity"):
            st.metric("Complexité Moy.", f"{stats['avg_complexity']:.1f}/100")
        
        st.divider()
        
        st.markdown("### ℹ️ À propos")
        st.markdown("""
        **Version:** 1.0.0  
        **Moteur:** GPT-4 + Whisper  
        **Mode:** Hackathon MVP
        """)
    
    return page


def page_new_declaration():
    """Page principale: Nouvelle déclaration de sinistre"""
    st.markdown("## 🎙️ Nouvelle Déclaration de Sinistre")
    
    st.info("""
    **Instructions:**
    1. Enregistrez votre déclaration vocale (français ou arabe)
    2. Ou uploadez un fichier audio existant
    3. Le système va analyser, structurer et décider du traitement
    """)
    
    # Mode de saisie
    input_mode = st.radio(
        "Mode de saisie",
        ["📁 Upload fichier audio", "🎤 Enregistrement direct", "📝 Texte simulé (démo)"],
        horizontal=True
    )
    
    transcript_text = None
    language = st.selectbox("Langue", ["Français", "Arabe", "Auto-détection"])
    lang_code = {"Français": "fr", "Arabe": "ar", "Auto-détection": None}[language]
    
    if input_mode == "📁 Upload fichier audio":
        audio_file = st.file_uploader(
            "Choisir un fichier audio",
            type=["mp3", "wav", "m4a", "ogg"],
            help="Formats supportés: MP3, WAV, M4A, OGG"
        )
        
        if audio_file:
            st.audio(audio_file)
            
            if st.button("🚀 Analyser la déclaration", type="primary"):
                with st.spinner("🎧 Transcription en cours..."):
                    # Sauvegarder temporairement
                    temp_path = Path("c:/Users/HP/Inssurance Advanced/data/temp_audio")
                    temp_path.mkdir(parents=True, exist_ok=True)
                    audio_path = temp_path / audio_file.name
                    
                    with open(audio_path, "wb") as f:
                        f.write(audio_file.getbuffer())
                    
                    # Transcription
                    stt_engine = STTEngine()
                    transcript_metadata = stt_engine.transcribe_audio(str(audio_path), lang_code)
                    
                    process_claim(transcript_metadata)
    
    elif input_mode == "🎤 Enregistrement direct":
        st.warning("⚠️ Fonctionnalité d'enregistrement direct en développement. Utilisez l'upload ou le mode texte pour la démo.")
    
    elif input_mode == "📝 Texte simulé (démo)":
        st.markdown("#### Exemples de déclarations pré-remplies")
        
        demo_examples = {
            "Accident automobile simple": """
                Bonjour, j'ai eu un accident hier soir vers 19 heures sur l'autoroute A1. 
                Un véhicule m'a percuté à l'arrière alors que j'étais arrêté dans les embouteillages. 
                Mon pare-choc est enfoncé et le coffre ne ferme plus. 
                L'autre conducteur a reconnu sa responsabilité et on a rempli un constat amiable.
                J'ai pris des photos des dommages.
            """,
            "Dégât des eaux complexe": """
                Bonjour, euh, je vous appelle parce que j'ai un gros problème. 
                Il y a une fuite d'eau chez moi depuis peut-être deux jours, je ne sais pas exactement. 
                L'eau vient du plafond mais je ne sais pas d'où ça vient exactement. 
                Mon voisin du dessus dit que ce n'est pas chez lui. 
                Mon parquet est complètement abîmé et il y a des traces sur les murs. 
                Je suis vraiment inquiet parce que ça continue de couler.
            """,
            "Accident avec tiers multiple": """
                Bonjour, j'ai été impliqué dans un accident à un carrefour. 
                Il y avait trois voitures en tout. Je pense que la voiture de devant a freiné brusquement,
                celle du milieu l'a percutée, et moi je n'ai pas pu éviter. 
                Il y a aussi un témoin qui a vu la scène. 
                Les dégâts sont importants, l'avant de ma voiture est très endommagé.
                Le constat est compliqué parce que chacun a sa version.
            """
        }
        
        example_choice = st.selectbox("Choisir un exemple", list(demo_examples.keys()))
        demo_text = st.text_area(
            "Texte de la déclaration",
            value=demo_examples[example_choice],
            height=200
        )
        
        if st.button("🚀 Analyser cette déclaration", type="primary"):
            with st.spinner("🧠 Analyse cognitive en cours..."):
                # Créer des métadonnées simulées
                from models.claim_models import TranscriptMetadata
                
                transcript_metadata = TranscriptMetadata(
                    original_transcript=demo_text,
                    normalized_transcript=demo_text.strip(),
                    language=lang_code or "fr",
                    confidence_score=0.95,
                    emotional_markers=["stress" if "inquiet" in demo_text.lower() else "calme"],
                    hesitations=demo_text.lower().count("euh"),
                    duration_seconds=60.0
                )
                
                process_claim(transcript_metadata)


def process_claim(transcript_metadata):
    """
    Traite une déclaration de sinistre de bout en bout
    
    Args:
        transcript_metadata: Métadonnées de transcription
    """
    progress_bar = st.progress(0)
    status_text = st.empty()
    
    try:
        # 1. Analyse cognitive
        status_text.text("🧠 Analyse cognitive de la déclaration...")
        progress_bar.progress(20)
        
        cognitive_engine = CognitiveClaimEngine(use_llm=False)  # Mode règles pour démo
        cognitive_structure = cognitive_engine.analyze_claim(transcript_metadata)
        
        # 2. Calcul de complexité
        status_text.text("📊 Calcul de l'indice de complexité...")
        progress_bar.progress(40)
        
        complexity_calc = ComplexityCalculator()
        complexity = complexity_calc.calculate(cognitive_structure)
        
        # 3. Création du Digital Twin
        status_text.text("🔄 Création du Digital Twin...")
        progress_bar.progress(60)
        
        claim_id = f"CLM-{datetime.now().strftime('%Y%m%d')}-{uuid.uuid4().hex[:6].upper()}"
        
        digital_twin = ClaimDigitalTwin(
            claim_id=claim_id,
            transcript_metadata=transcript_metadata,
            cognitive_structure=cognitive_structure,
            complexity=complexity,
            current_state=ClaimState.ANALYZING
        )
        
        digital_twin.add_interaction(
            "audio_input",
            "Déclaration vocale reçue",
            {"language": transcript_metadata.language}
        )
        
        # 4. Décision intelligente
        status_text.text("🎯 Prise de décision intelligente...")
        progress_bar.progress(80)
        
        decision_engine = DecisionEngine()
        should_escalate, reason, action = decision_engine.make_decision(digital_twin)
        
        if should_escalate:
            digital_twin.escalate(reason)
        else:
            digital_twin.change_state(ClaimState.AUTONOMOUS, reason)
        
        # 5. Génération des résumés
        status_text.text("📝 Génération des résumés multi-niveaux...")
        progress_bar.progress(90)
        
        summary_gen = SummaryGenerator()
        client_summary = summary_gen.generate_client_summary(digital_twin)
        advisor_brief = summary_gen.generate_advisor_brief(digital_twin)
        
        # 6. Génération de la réponse audio
        status_text.text("🔊 Génération de la réponse audio...")
        progress_bar.progress(95)
        
        audio_response_path = create_client_response(
            claim_id,
            client_summary.dict(),
            language=transcript_metadata.language
        )
        
        # 7. Sauvegarde dans le CRM
        status_text.text("💾 Enregistrement dans le CRM...")
        progress_bar.progress(100)
        
        crm = get_crm()
        crm.create_claim(digital_twin)
        
        # Mise à jour de la session
        st.session_state.current_claim = digital_twin
        st.session_state.client_summary = client_summary
        st.session_state.advisor_brief = advisor_brief
        st.session_state.audio_response_path = audio_response_path
        st.session_state.processing_complete = True
        
        status_text.empty()
        progress_bar.empty()
        
        st.success("✅ Déclaration traitée avec succès!")
        st.balloons()
        
        # Afficher les résultats
        display_claim_results()
        
    except Exception as e:
        st.error(f"❌ Erreur lors du traitement: {e}")
        import traceback
        st.code(traceback.format_exc())


def display_claim_results():
    """Affiche les résultats du traitement d'un sinistre"""
    if not st.session_state.processing_complete:
        return
    
    claim = st.session_state.current_claim
    client_summary = st.session_state.client_summary
    advisor_brief = st.session_state.advisor_brief
    
    st.markdown("---")
    st.markdown("## 📊 Résultats du Traitement")
    
    # En-tête du sinistre
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("ID Sinistre", claim.claim_id)
    
    with col2:
        complexity_class = f"complexity-{claim.complexity.level.value}"
        st.markdown(f"**Complexité**")
        st.markdown(f'<p class="{complexity_class}" style="font-size: 1.5rem;">{claim.complexity.total_score:.1f}/100</p>', 
                    unsafe_allow_html=True)
    
    with col3:
        st.metric("Type", claim.cognitive_structure.claim_type.value.title())
    
    with col4:
        status_icon = "🔴" if claim.is_escalated else "🟢"
        st.metric("Statut", f"{status_icon} {claim.current_state.value}")
    
    # Tabs pour les différentes vues
    tab1, tab2, tab3, tab4, tab5 = st.tabs([
        "📝 Transcription", 
        "🧠 Analyse Cognitive", 
        "👤 Résumé Client",
        "👨‍💼 Brief Conseiller",
        "🔊 Réponse Audio"
    ])
    
    with tab1:
        render_transcription_tab(claim)
    
    with tab2:
        render_cognitive_tab(claim)
    
    with tab3:
        render_client_summary_tab(client_summary)
    
    with tab4:
        render_advisor_tab(advisor_brief)
    
    with tab5:
        render_audio_response_tab()


def render_transcription_tab(claim):
    """Affiche l'onglet transcription"""
    st.markdown("### 🎧 Transcription Originale")
    
    meta = claim.transcript_metadata
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Langue", meta.language.upper())
    with col2:
        st.metric("Confiance", f"{meta.confidence_score*100:.1f}%")
    with col3:
        st.metric("Hésitations", meta.hesitations)
    
    st.text_area("Transcription brute", meta.original_transcript, height=200)
    
    st.markdown("### ✨ Transcription Normalisée")
    st.text_area("Texte normalisé", meta.normalized_transcript, height=150)
    
    if meta.emotional_markers:
        st.markdown("### 💭 Marqueurs Émotionnels")
        st.write(", ".join([f"`{marker}`" for marker in meta.emotional_markers]))


def render_cognitive_tab(claim):
    """Affiche l'analyse cognitive"""
    st.markdown("### 🧠 Structure Cognitive du Sinistre")
    
    cognitive = claim.cognitive_structure
    complexity = claim.complexity
    
    # Informations principales
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📍 Circonstances")
        st.write(f"**Date:** {cognitive.date_incident}")
        st.write(f"**Lieu:** {cognitive.location}")
        st.write(f"**Type:** {cognitive.claim_type.value} ({cognitive.claim_type_confidence*100:.0f}% confiance)")
    
    with col2:
        st.markdown("#### 👥 Parties Impliquées")
        for party in cognitive.parties_involved:
            st.write(f"• **{party.role}:** {party.name or 'Non spécifié'}")
    
    # Dommages
    st.markdown("#### 💥 Description des Dommages")
    st.info(cognitive.damages_description)
    
    # Décomposition de la complexité
    st.markdown("#### 📊 Décomposition de la Complexité")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Garanties", f"{complexity.guarantees_score:.0f}")
        st.metric("Tiers", f"{complexity.third_party_score:.0f}")
    with col2:
        st.metric("Documents", f"{complexity.missing_docs_score:.0f}")
        st.metric("Ambiguïté", f"{complexity.ambiguity_score:.0f}")
    with col3:
        st.metric("Émotionnel", f"{complexity.emotional_score:.0f}")
        st.metric("Incohérences", f"{complexity.inconsistency_score:.0f}")
    
    st.caption(f"**Explication:** {complexity.explanation}")
    
    # Ambiguïtés
    if cognitive.ambiguities:
        st.markdown("#### ⚠️ Zones d'Ambiguïté")
        for amb in cognitive.ambiguities:
            severity_color = ["🟢", "🟡", "🟠", "🔴", "🔴"][min(amb.severity-1, 4)]
            st.warning(f"{severity_color} **{amb.category.title()}:** {amb.description} - *{amb.impact_on_decision}*")
    
    # Faits vs Suppositions
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### ✅ Faits Vérifiés")
        for fact in cognitive.facts[:5]:
            st.write(f"• {fact}")
    
    with col2:
        st.markdown("#### ❓ Suppositions")
        for assumption in cognitive.assumptions[:5]:
            st.write(f"• {assumption}")


def render_client_summary_tab(client_summary):
    """Affiche le résumé client"""
    st.markdown("### 👤 Résumé pour le Client")
    
    st.success(client_summary.message)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("#### 📋 Prochaines Étapes")
        for step in client_summary.next_steps:
            st.write(f"✓ {step}")
    
    with col2:
        st.markdown("#### 📄 Documents Requis")
        if client_summary.documents_required:
            for doc in client_summary.documents_required:
                st.write(f"📎 {doc}")
        else:
            st.write("✅ Aucun document supplémentaire requis")
    
    st.info(f"⏱️ **Délai estimé:** {client_summary.estimated_processing_time}")
    st.info(f"☎️ **Contact:** {client_summary.contact_info}")


def render_advisor_tab(advisor_brief):
    """Affiche le brief conseiller"""
    st.markdown("### 👨‍💼 Brief Conseiller Expert")
    
    # Priorité
    priority_colors = {
        "URGENTE": "🔴",
        "ÉLEVÉE": "🟠",
        "NORMALE": "🟢"
    }
    priority_icon = priority_colors.get(advisor_brief.priority_level, "🟢")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Priorité", f"{priority_icon} {advisor_brief.priority_level}")
    with col2:
        st.metric("Effort Estimé", advisor_brief.estimated_effort)
    with col3:
        st.metric("Stress Client", f"{advisor_brief.client_stress_level}/10")
    
    # Faits structurés
    st.markdown("#### 📋 Vue Structurée")
    for fact in advisor_brief.structured_facts:
        st.write(f"• {fact}")
    
    # Drapeaux de risque
    if advisor_brief.risk_flags:
        st.markdown("#### 🚩 Drapeaux de Risque")
        for flag in advisor_brief.risk_flags:
            st.warning(flag)
    
    # Actions suggérées
    st.markdown("#### 💡 Actions Suggérées")
    for i, action in enumerate(advisor_brief.suggested_actions, 1):
        st.write(f"{i}. {action}")
    
    # Contexte émotionnel
    st.markdown("#### 💭 Contexte Émotionnel")
    st.info(advisor_brief.emotional_context)


def render_audio_response_tab():
    """Affiche la réponse audio"""
    st.markdown("### 🔊 Réponse Audio Générée")
    
    audio_path = st.session_state.audio_response_path
    
    if audio_path and Path(audio_path).exists():
        if audio_path.endswith('.mp3'):
            with open(audio_path, 'rb') as audio_file:
                audio_bytes = audio_file.read()
                st.audio(audio_bytes, format='audio/mp3')
        else:
            # Fichier texte (mode simulation)
            with open(audio_path, 'r', encoding='utf-8') as f:
                audio_text = f.read()
                st.text_area("Transcription de la réponse (simulation)", audio_text, height=300)
                st.caption("💡 En mode simulation, le texte est affiché au lieu de l'audio")
    else:
        st.warning("Aucune réponse audio générée")
    
    st.markdown("#### 📥 Télécharger")
    if audio_path and Path(audio_path).exists():
        with open(audio_path, 'rb') as f:
            st.download_button(
                "Télécharger la réponse",
                f.read(),
                file_name=f"reponse_{st.session_state.current_claim.claim_id}.mp3",
                mime="audio/mp3"
            )


def page_crm_dashboard():
    """Page du tableau de bord CRM"""
    st.markdown("## 📋 Tableau de Bord CRM")
    
    crm = st.session_state.crm
    
    # Filtres
    col1, col2, col3 = st.columns(3)
    with col1:
        filter_state = st.selectbox(
            "Filtrer par état",
            ["Tous", "Reçu", "En analyse", "Escaladé", "Résolu"]
        )
    
    with col2:
        filter_escalated = st.checkbox("Uniquement escaladés")
    
    with col3:
        limit = st.number_input("Nombre de résultats", 10, 100, 50)
    
    # Récupérer les sinistres
    state_filter = None
    if filter_state != "Tous":
        state_mapping = {
            "Reçu": ClaimState.RECEIVED,
            "En analyse": ClaimState.ANALYZING,
            "Escaladé": ClaimState.ESCALATED,
            "Résolu": ClaimState.RESOLVED
        }
        state_filter = state_mapping.get(filter_state)
    
    claims = crm.list_claims(
        state=state_filter,
        escalated_only=filter_escalated,
        limit=limit
    )
    
    st.markdown(f"### 📊 {len(claims)} sinistres trouvés")
    
    # Affichage en tableau
    if claims:
        for claim in claims:
            with st.expander(
                f"🔹 {claim.claim_id} - {claim.cognitive_structure.claim_type.value.title()} "
                f"({'🔴 Escaladé' if claim.is_escalated else '🟢 Autonome'})"
            ):
                col1, col2, col3, col4 = st.columns(4)
                
                with col1:
                    st.write(f"**Créé:** {claim.created_at.strftime('%d/%m/%Y %H:%M')}")
                with col2:
                    st.write(f"**Complexité:** {claim.complexity.total_score:.1f}")
                with col3:
                    st.write(f"**État:** {claim.current_state.value}")
                with col4:
                    if st.button("Voir détails", key=claim.claim_id):
                        st.session_state.current_claim = claim
                        st.session_state.processing_complete = True
                        st.rerun()
    else:
        st.info("Aucun sinistre trouvé")


def page_statistics():
    """Page des statistiques"""
    st.markdown("## 📊 Statistiques et Métriques")
    
    stats = st.session_state.crm.get_statistics()
    
    # Métriques globales
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric("Total Sinistres", stats.get("total_claims", 0))
    
    with col2:
        st.metric("Escaladés", stats.get("escalated_count", 0))
    
    with col3:
        escalation_rate = 0
        if stats.get("total_claims", 0) > 0:
            escalation_rate = (stats.get("escalated_count", 0) / stats["total_claims"]) * 100
        st.metric("Taux d'Escalade", f"{escalation_rate:.1f}%")
    
    with col4:
        st.metric("Complexité Moyenne", f"{stats.get('avg_complexity', 0):.1f}/100")
    
    # Distribution par état
    if stats.get("by_state"):
        st.markdown("### 📈 Distribution par État")
        
        import pandas as pd
        df_states = pd.DataFrame(list(stats["by_state"].items()), columns=["État", "Nombre"])
        st.bar_chart(df_states.set_index("État"))


# ===== CONVERSATION EN TEMPS RÉEL (Intégration app_interactive) =====

def initialize_conversation_session():
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
    st.session_state.session_conversation_initialized = True
    st.session_state.claim_id = claim_id
    st.session_state.conversation_history = []
    
    return digital_twin, conversation_manager, claim_id


def play_audio(audio_path):
    """Joue un fichier audio"""
    if audio_path and Path(audio_path).exists():
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


def page_real_time_conversation():
    """Page de conversation en temps réel avec méthode LAMA"""
    st.markdown("## 💬 Conversation en Temps Réel")
    st.markdown("""
    **Système conversationnel LAMA interactif:**
    - 🎧 **Listen**: Écouter le sinistre
    - 🤝 **Acknowledge**: Empathiser
    - 📝 **Make Statement**: Résumer
    - ❓ **Ask Questions**: Collecter infos
    """)
    
    # Initialiser session si nécessaire
    if "session_conversation_initialized" not in st.session_state:
        st.session_state.session_conversation_initialized = False
        st.session_state.conversation_active = False
        st.session_state.digital_twin = None
        st.session_state.conversation_manager = None
        st.session_state.conversation_history = []
        st.session_state.current_phase = None
    
    # Contrôles de session
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("🎙️ Lancer une conversation", key="start_conversation", use_container_width=True):
            digital_twin, conv_manager, claim_id = initialize_conversation_session()
            
            with st.status("🎙️ Session initialisée...", expanded=True) as status:
                st.write(f"✅ Claim ID: `{claim_id}`")
                st.write(f"✅ État: {digital_twin.current_state.value}")
                
                # Étape 1: Accueil TTS
                st.write("\n📢 **Accueil vocal...**")
                tts_engine = TTSEngine(language="fr")
                greeting_text = conv_manager.get_greeting_prompt()
                
                greeting_audio = Path("data/audio_responses") / f"greeting_{claim_id}.mp3"
                greeting_audio.parent.mkdir(parents=True, exist_ok=True)
                
                try:
                    tts_engine.synthesize(greeting_text, str(greeting_audio), tone="professional")
                    st.write(f"🎙️ **Système**: {greeting_text}")
                    play_audio(str(greeting_audio))
                except:
                    st.write(f"🎙️ **Système**: {greeting_text}")
                
                log_conversation("System", greeting_text, str(greeting_audio))
                
                # Passer à la phase LISTEN après le greeting
                conv_manager.current_phase = ConversationPhase.LISTEN
                
                status.update(label="✅ Accueil terminé - En attente de votre description", state="complete")
    
    with col2:
        if st.button("❌ Fermer conversation", key="end_conversation", use_container_width=True):
            st.session_state.conversation_active = False
            st.session_state.session_conversation_initialized = False
            st.info("Conversation fermée. Cliquez sur 'Lancer' pour recommencer.")
    
    # Enregistrement audio
    if st.session_state.session_conversation_initialized and st.session_state.conversation_active:
        st.divider()
        st.subheader("🎤 Parlez maintenant")
        
        audio_input = st.audio_input("Enregistrez votre réponse:", key="user_audio_input")
        
        if audio_input is not None:
            # Sauvegarder et traiter l'audio
            temp_audio = Path("data/temp_audio") / f"user_input_{datetime.now().strftime('%H%M%S')}.wav"
            temp_audio.parent.mkdir(parents=True, exist_ok=True)
            
            with open(temp_audio, 'wb') as f:
                f.write(audio_input.getbuffer())
            
            # STT + Traitement
            with st.status("🔄 Traitement...", expanded=True) as status:
                st.write("📝 Transcription en cours...")
                
                try:
                    stt_engine = STTEngine()
                    metadata = stt_engine.transcribe_audio(str(temp_audio))
                    
                    st.write(f"✅ Langue détectée: **{metadata.language}**")
                    st.write(f"✅ Transcription: **{metadata.original_transcript[:100]}...**")
                    
                    user_text = metadata.normalized_transcript
                    log_conversation("Client", user_text, str(temp_audio))
                    
                    # Analyse cognitive
                    st.write("\n🧠 Analyse cognitive en cours...")
                    
                    conv_manager = st.session_state.conversation_manager
                    cognitive_engine = CognitiveClaimEngine()
                    cognitive_analysis = cognitive_engine.analyze_claim(metadata)
                    
                    st.write(f"✅ Type de sinistre: {cognitive_analysis.claim_type.value}")
                    st.write(f"✅ Stress émotionnel: {cognitive_analysis.emotional_stress_level}/10")
                    
                    # Traitement LAMA
                    st.write("\n💬 Réponse du système (méthode LAMA)...")
                    
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
                        
                        tts_engine = TTSEngine(language="fr")
                        
                        # ACKNOWLEDGE
                        st.write(f"\n1️⃣ **Empathie**: {ack_text}")
                        ack_audio = Path("data/audio_responses") / f"ack_{datetime.now().strftime('%H%M%S')}.mp3"
                        ack_audio.parent.mkdir(parents=True, exist_ok=True)
                        try:
                            tts_engine.synthesize(ack_text, str(ack_audio), tone="empathetic")
                            play_audio(str(ack_audio))
                        except:
                            pass
                        log_conversation("System", ack_text, str(ack_audio))
                        
                        # MAKE STATEMENT
                        st.write(f"\n2️⃣ **Résumé**: {summary_text}")
                        summary_audio = Path("data/audio_responses") / f"summary_{datetime.now().strftime('%H%M%S')}.mp3"
                        try:
                            tts_engine.synthesize(summary_text, str(summary_audio), tone="professional")
                            play_audio(str(summary_audio))
                        except:
                            pass
                        log_conversation("System", summary_text, str(summary_audio))
                        
                        # ASK QUESTIONS
                        st.write(f"\n3️⃣ **Question**: {next_q}")
                        question_audio = Path("data/audio_responses") / f"q_{datetime.now().strftime('%H%M%S')}.mp3"
                        try:
                            tts_engine.synthesize(next_q, str(question_audio), tone="professional")
                            play_audio(str(question_audio))
                        except:
                            pass
                        log_conversation("System", next_q, str(question_audio))
                        
                        conv_manager.current_phase = ConversationPhase.ASK_CALLER_ID
                    
                    elif conv_manager.current_phase == ConversationPhase.ASK_CALLER_ID:
                        conv_manager.process_caller_identification(user_text)
                        next_q = conv_manager._generate_next_question()
                        
                        st.write(f"✅ Identité enregistrée")
                        st.write(f"\n❓ Question: {next_q}")
                        
                        tts_engine = TTSEngine(language="fr")
                        q_audio = Path("data/audio_responses") / f"q_{datetime.now().strftime('%H%M%S')}.mp3"
                        try:
                            tts_engine.synthesize(next_q, str(q_audio))
                            play_audio(str(q_audio))
                        except:
                            pass
                        log_conversation("System", next_q, str(q_audio))
                        
                        conv_manager.current_phase = ConversationPhase.ASK_VEHICLE
                    
                    # Afficher le statut de collecte
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
                    
                    status.update(label="✅ Tour terminé", state="complete")
                
                except Exception as e:
                    st.error(f"❌ Erreur lors du traitement: {e}")
                    status.update(label="❌ Erreur", state="error")
    
    # Historique de conversation
    if st.session_state.conversation_history:
        st.divider()
        st.subheader("📋 Historique de conversation")
        
        for item in st.session_state.conversation_history:
            with st.expander(f"{item['timestamp'].strftime('%H:%M:%S')} - {item['speaker']}"):
                st.write(f"**{item['speaker']}**: {item['text']}")
                if item['audio'] and Path(item['audio']).exists():
                    play_audio(item['audio'])


def main():
    """Fonction principale de l'application"""
    initialize_session_state()
    render_header()
    
    page = render_sidebar()
    
    if page == "🎙️ Nouvelle Déclaration":
        page_new_declaration()
    elif page == "� Conversation en temps réel":
        page_real_time_conversation()
    elif page == "�📋 Tableau de Bord CRM":
        page_crm_dashboard()
    elif page == "📊 Statistiques":
        page_statistics()


if __name__ == "__main__":
    main()
