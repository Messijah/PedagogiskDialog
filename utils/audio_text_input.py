import streamlit as st
from utils.audio_handler import (
    transcribe_uploaded_file,
    validate_audio_file,
    record_audio_streamlit,
    save_recorded_audio,
    transcribe_audio_openai
)

def audio_text_input(steg_nummer, session_id, key_prefix=""):
    """
    Återanvändbar komponent för ljuduppladdning, inspelning och inklistring av transkribering.
    Returnerar (transkribering, audio_path) eller (transkribering, None)
    """
    transcript = None
    audio_path = None
    st.markdown("---")
    st.subheader("🎤 Spela in, ladda upp eller klistra in samtal")

    tab1, tab2, tab3 = st.tabs([
        "📁 Ladda upp ljudfil", 
        "🎤 Spela in direkt", 
        "✍️ Klistra in transkribering"
    ])

    with tab1:
        st.markdown("**Ladda upp en ljudfil från samtalet:**")
        uploaded_file = st.file_uploader(
            "Välj ljudfil",
            type=['wav', 'mp3', 'm4a', 'mp4'],
            key=f"{key_prefix}_audio_upload_{steg_nummer}"
        )
        if uploaded_file:
            is_valid, message = validate_audio_file(uploaded_file)
            if is_valid:
                st.success(f"✅ Fil uppladdad: {uploaded_file.name}")
                st.audio(uploaded_file.getvalue())
                if st.button("🔤 Transkribera ljudfil", key=f"{key_prefix}_transcribe_audio_{steg_nummer}"):
                    with st.spinner("Transkriberar ljudfil... Detta kan ta några minuter."):
                        try:
                            transcript, audio_path = transcribe_uploaded_file(
                                uploaded_file, session_id, steg_nummer
                            )
                            if transcript:
                                st.success("✅ Transkribering klar!")
                                return transcript, audio_path
                            else:
                                st.error("Kunde inte transkribera filen. Kontrollera att det är en giltig ljudfil.")
                        except Exception as e:
                            st.error(f"Fel vid transkribering: {str(e)}")
            else:
                st.error(f"❌ {message}")

    with tab2:
        st.markdown("**Spela in direkt i webbläsaren:**")
        try:
            audio_bytes = record_audio_streamlit()
            if audio_bytes:
                st.success("✅ Inspelning mottagen!")
                if st.button("🔤 Transkribera inspelning", key=f"{key_prefix}_transcribe_recording_{steg_nummer}"):
                    with st.spinner("Sparar och transkriberar inspelning..."):
                        try:
                            audio_path = save_recorded_audio(audio_bytes, session_id, steg_nummer)
                            transcript = transcribe_audio_openai(audio_path)
                            if transcript:
                                st.success("✅ Transkribering klar!")
                                return transcript, audio_path
                            else:
                                st.error("Kunde inte transkribera inspelningen.")
                        except Exception as e:
                            st.error(f"Fel vid transkribering: {str(e)}")
        except:
            st.warning("Direktinspelning inte tillgänglig. Använd filuppladdning istället.")

    with tab3:
        st.markdown("**Klistra in transkribering manuellt:**")
        manual_transcript = st.text_area(
            "Klistra in transkriberingen från samtalet här:",
            value=st.session_state.get(f"{key_prefix}_manual_transcript_{steg_nummer}", ''),
            height=300,
            key=f"{key_prefix}_manual_transcript_{steg_nummer}"
        )
        if st.button("💾 Spara transkribering", key=f"{key_prefix}_save_manual_transcript_{steg_nummer}"):
            st.session_state[f"{key_prefix}_manual_transcript_{steg_nummer}"] = manual_transcript
            st.session_state.transcript_steg2 = manual_transcript if steg_nummer == 2 else st.session_state.get('transcript_steg2', None)
            st.session_state.transcript_steg3 = manual_transcript if steg_nummer == 3 else st.session_state.get('transcript_steg3', None)
            st.session_state.transcript_steg4 = manual_transcript if steg_nummer == 4 else st.session_state.get('transcript_steg4', None)
            st.success("Transkribering sparad!")
            return manual_transcript, None

    return None, None 