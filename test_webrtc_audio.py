import streamlit as st
from utils.audio_handler import record_and_transcribe_audio

st.set_page_config(page_title="Test WebRTC Audio", layout="wide")

st.title("🎤 Test av WebRTC Ljudinspelning med Automatisk Transkribering")

st.markdown("""
Detta är en test av den nya WebRTC-baserade ljudinspelningsfunktionen som automatiskt sparar och transkriberar ljud.
""")

# Test session data
session_id = "test_session"
step_number = 1

st.markdown("---")
st.subheader("Automatisk Ljudinspelning och Transkribering")

# Test ljudinspelning med automatisk sparning och transkribering
audio_path, transcription = record_and_transcribe_audio(session_id, step_number, "test")

if audio_path and transcription:
    st.markdown("---")
    st.subheader("🎯 Resultat")
    st.success("✅ Komplett process lyckades!")
    st.write(f"**Ljudfil:** {audio_path}")
    st.write(f"**Transkribering:** {transcription}")
    
    # Visa AI-förslag baserat på transkriberingen
    if st.button("🤖 Generera AI-förslag"):
        from utils.ai_helper import get_ai_suggestions
        
        with st.spinner("Genererar AI-förslag..."):
            suggestions = get_ai_suggestions(transcription, "test_problem")
            
        if suggestions:
            st.markdown("### 🎯 AI-förslag:")
            st.write(suggestions)
        else:
            st.error("❌ Kunde inte generera AI-förslag")

st.markdown("---")
st.markdown("**Instruktioner:**")
st.markdown("""
1. Klicka på 'START' för att börja spela in
2. Prata in ditt meddelande (t.ex. "Hej, detta är ett test av ljudinspelningen")
3. Klicka på 'STOP' för att avsluta inspelningen
4. Systemet sparar och transkriberar automatiskt
5. Testa AI-förslag baserat på transkriberingen
""")