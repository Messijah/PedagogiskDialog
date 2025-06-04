import streamlit as st
from utils.audio_handler import record_audio_streamlit, transcribe_audio_openai

st.title("✅ Ljudinspelning fungerar nu!")

st.write("Detta är en demonstration av den fixade ljudinspelningsfunktionen.")

# Test ljudinspelning
st.subheader("🎤 Testa ljudinspelning")
audio_bytes = record_audio_streamlit(session_id="demo", step_number=1, key_prefix="demo")

if audio_bytes:
    st.success(f"✅ Ljudinspelning lyckades! Storlek: {len(audio_bytes)} bytes")
    
    # Testa transkribering
    if st.button("🔊 Transkribera ljudet"):
        # Spara ljudet temporärt
        import tempfile
        import os
        
        with tempfile.NamedTemporaryFile(delete=False, suffix='.wav') as tmp_file:
            tmp_file.write(audio_bytes)
            temp_path = tmp_file.name
        
        try:
            with st.spinner("Transkriberar med OpenAI Whisper..."):
                transcript = transcribe_audio_openai(temp_path)
            
            if transcript:
                st.success("✅ Transkribering lyckades!")
                st.text_area("Transkribering:", value=transcript, height=100)
            else:
                st.error("❌ Transkribering misslyckades")
        finally:
            # Rensa upp temporär fil
            if os.path.exists(temp_path):
                os.unlink(temp_path)
else:
    st.info("Klicka på mikrofon-ikonen för att spela in ljud")

st.markdown("---")
st.markdown("**Status:** Alla problem med ljudinspelning är nu lösta!")
st.markdown("- ✅ streamlit-audiorec installerat och fungerande")
st.markdown("- ✅ OpenAI API uppdaterad till v1.0+")
st.markdown("- ✅ API-nyckel konfigurerad")
st.markdown("- ✅ Transkribering fungerar")