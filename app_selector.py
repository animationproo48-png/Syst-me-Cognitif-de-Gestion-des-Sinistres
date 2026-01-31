"""
Comparatif des trois interfaces disponibles
"""

import streamlit as st

st.set_page_config(page_title="Service Gestion Sinistre - Sélection", layout="centered")

st.title("🎙️ Service Gestion Sinistre - Mode Sinistre")
st.markdown("""
Choisissez votre mode d'utilisation :
""")

col1, col2, col3 = st.columns(3)

with col1:
    st.header("📁 Upload Fichier")
    st.markdown("""
    **Meilleure qualité** ✅
    - Upload de fichiers pré-enregistrés
    - Format: MP3, WAV, M4A, OGG
    - Aucune compression supplémentaire
    - **RECOMMANDÉ** pour meilleure qualité de transcription
    """)
    if st.button("Aller à app_upload.py", key="btn_upload", use_container_width=True):
        st.switch_page("pages/app_upload.py")

with col2:
    st.header("🎤 Microphone")
    st.markdown("""
    **Qualité normale** 
    - Enregistrement direct via microphone
    - Nécessite PyAudio
    - WAV haute qualité (16kHz)
    - Mode temps réel
    """)
    if st.button("Aller à app_microphone.py", key="btn_mic", use_container_width=True):
        st.switch_page("pages/app_microphone.py")

with col3:
    st.header("🎙️ Streamlit Audio")
    st.markdown("""
    **Qualité normale**
    - Interface Streamlit standard
    - st.audio_input() intégré
    - WebM compressé
    - Plus simple mais moins précis
    """)
    if st.button("Aller à app_interactive.py", key="btn_interactive", use_container_width=True):
        st.switch_page("pages/app_interactive.py")

st.divider()
st.info("""
**Résumé** :
- 📁 **Upload**: Meilleure qualité (fichiers pré-enregistrés)
- 🎤 **Microphone**: Qualité bonne (enregistrement direct WAV)
- 🎙️ **Streamlit**: Qualité normale (WebM compressé)

**Conseil** : Utilisez **Upload** pour des enregistrements préalables sur PC
""")
