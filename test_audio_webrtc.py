import streamlit as st
from utils.audio_handler import record_audio_streamlit

st.title("Test av ljudinspelning med WebRTC")

st.write("Testar den uppdaterade ljudinspelningsfunktionen:")

# Testa ljudinspelning
audio_bytes = record_audio_streamlit(session_id="test", step_number=1, key_prefix="test")

if audio_bytes:
    st.success("✅ Ljudinspelning fungerar!")
    st.write(f"Ljuddata storlek: {len(audio_bytes)} bytes")
else:
    st.info("Ingen ljuddata ännu. Prova att spela in något.")