import streamlit as st
from utils.audio_handler import (
    transcribe_audio_openai,
    validate_audio_file,
    record_audio_streamlit,
    save_uploaded_audio,
    save_recorded_audio,
    display_audio_player
)

def audio_text_input(step_number, session_id, key_prefix=""):
    """
    Komponent för att låta användaren:
     1. Ladda upp ljudfil
     2. Spela in direkt i webbläsaren
     3. Klistra in transkribering manuellt

    Returnerar (transkribering, audio_path) eller (None, None) om inget val gjorts.
    """
    transcript = None
    audio_path = None

    st.markdown("---")
    st.subheader("Ljudalternativ")

    # 1) Uppladdning av befintlig ljudfil
    uploaded_file = st.file_uploader(
        label="1. Ladda upp ljudfil (wav/mp3)",
        type=["wav", "mp3"],
        key=f"{key_prefix}_uploader_{step_number}"
    )
    if uploaded_file:
        ok, msg = validate_audio_file(uploaded_file)
        if not ok:
            st.error(msg)
        else:
            audio_path = save_uploaded_audio(uploaded_file, session_id, step_number)
            st.success(f"Ljudfil uppladdad: `{audio_path}`")
            display_audio_player(audio_path)

            if st.button("🔊 Transkribera uppladdad fil", key=f"{key_prefix}_trans_up_{step_number}"):
                with st.spinner("Transkriberar..."):
                    transcript = transcribe_audio_openai(audio_path)
                if transcript:
                    st.text_area(
                        "Transkribering:",
                        value=transcript,
                        height=200,
                        key=f"{key_prefix}_auto_trans_{step_number}"
                    )
                    return transcript, audio_path

    st.markdown("— eller —")

    # 2) Liveinspelning via webbläsaren
    st.markdown("2. Spela in ljud direkt:")
    audio_bytes = record_audio_streamlit(session_id, step_number, key_prefix=key_prefix)
    if audio_bytes:
        saved_path = save_recorded_audio(audio_bytes, session_id, step_number)
        if saved_path:
            st.success(f"Inspelad ljudfil sparad: `{saved_path}`")
            display_audio_player(saved_path)
            audio_path = saved_path

            if st.button("🔊 Transkribera inspelning", key=f"{key_prefix}_trans_rec_{step_number}"):
                with st.spinner("Transkriberar inspelning..."):
                    transcript = transcribe_audio_openai(audio_path)
                if transcript:
                    st.text_area(
                        "Transkribering:",
                        value=transcript,
                        height=200,
                        key=f"{key_prefix}_auto_trans_rec_{step_number}"
                    )
                    return transcript, audio_path

    st.markdown("— eller —")

    # 3) Manuell inklistring av transkribering
    st.markdown("3. Klistra in transkribering manuellt:")
    manual_transcript = st.text_area(
        label="Klistra in transkribering eller skriv här:",
        value=st.session_state.get(f"{key_prefix}_manual_transcript_{step_number}", ""),
        height=200,
        key=f"{key_prefix}_manual_transcript_{step_number}"
    )
    if st.button("💾 Spara manuell transkribering", key=f"{key_prefix}_save_manual_{step_number}"):
        st.session_state[f"transcript_steg{step_number}"] = manual_transcript
        st.success("Manuell transkribering sparad!")
        return manual_transcript, None

    return None, None 