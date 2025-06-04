import streamlit as st
from utils.audio_handler import record_audio_streamlit, save_recorded_audio, transcribe_audio_openai

st.set_page_config(page_title="Test WebRTC Audio", layout="wide")

st.title("🎤 Test av WebRTC Ljudinspelning")

st.markdown("""
Detta är en test av den nya WebRTC-baserade ljudinspelningsfunktionen.
""")

# Test session data
session_id = "test_session"
step_number = 1

st.markdown("---")
st.subheader("Ljudinspelning med WebRTC")

# Test ljudinspelning
audio_bytes = record_audio_streamlit(session_id, step_number, "test")

if audio_bytes:
    st.success("✅ Ljudinspelning lyckades!")
    
    # Spara ljudfilen
    if st.button("💾 Spara och transkribera"):
        with st.spinner("Sparar ljudfil..."):
            audio_path = save_recorded_audio(audio_bytes, session_id, step_number)
            
        if audio_path:
            st.success(f"Ljudfil sparad: {audio_path}")
            
            # Transkribera
            with st.spinner("Transkriberar ljud..."):
                transcription = transcribe_audio_openai(audio_path)
                
            if transcription:
                st.success("✅ Transkribering klar!")
                st.markdown("### Transkribering:")
                st.write(transcription)
            else:
                st.error("❌ Transkribering misslyckades")
        else:
            st.error("❌ Kunde inte spara ljudfil")

st.markdown("---")
st.markdown("**Instruktioner:**")
st.markdown("""
1. Klicka på 'START' för att börja spela in
2. Prata in ditt meddelande
3. Klicka på 'STOP' för att avsluta inspelningen
4. Klicka på 'Spara och transkribera' för att testa hela flödet
""")