import streamlit as st
from utils.audio_handler import (
    transcribe_audio_openai,
    validate_audio_file,
    record_and_transcribe_audio,
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

            # Automatisk transkribering av uppladdad fil
            with st.spinner("Transkriberar uppladdad fil automatiskt..."):
                transcript = transcribe_audio_openai(audio_path)
            
            if transcript:
                st.success("✅ Automatisk transkribering klar!")
                st.text_area(
                    "Transkribering:",
                    value=transcript,
                    height=200,
                    key=f"{key_prefix}_auto_trans_{step_number}"
                )
                return transcript, audio_path
            else:
                st.error("❌ Transkribering misslyckades")
                # Visa knapp för manuell transkribering om automatisk misslyckas
                if st.button("🔄 Försök transkribera igen", key=f"{key_prefix}_retry_trans_{step_number}"):
                    with st.spinner("Försöker transkribera igen..."):
                        transcript = transcribe_audio_openai(audio_path)
                    if transcript:
                        st.text_area(
                            "Transkribering:",
                            value=transcript,
                            height=200,
                            key=f"{key_prefix}_retry_auto_trans_{step_number}"
                        )
                        return transcript, audio_path

    st.markdown("— eller —")

    # 2) Liveinspelning via webbläsaren med automatisk sparning och transkribering
    st.markdown("2. Spela in ljud direkt (sparas och transkriberas automatiskt):")
    
    # Kontrollera om vi är på Streamlit Cloud
    try:
        audio_path, transcript = record_and_transcribe_audio(session_id, step_number, key_prefix=key_prefix)
        
        if audio_path and transcript:
            st.success("✅ Ljudinspelning och transkribering klar!")
            st.text_area(
                "Automatisk transkribering:",
                value=transcript,
                height=200,
                key=f"{key_prefix}_auto_trans_rec_{step_number}"
            )
            return transcript, audio_path
    except Exception as e:
        st.warning("⚠️ Direktinspelning fungerar inte i denna miljö.")
        st.info("""
        **På Streamlit Cloud:**
        - Använd alternativ 1 (filuppladdning) eller alternativ 3 (manuell text)
        - Spela in ljud med din telefon/dator och ladda upp filen
        """)

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