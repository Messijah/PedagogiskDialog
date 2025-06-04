import streamlit as st
import os
from datetime import datetime

def save_uploaded_audio(uploaded_file, session_id, step_number):
    """
    Spara uppladdad ljudfil (wav/mp3) på disk under data/audio.
    """
    if not os.path.exists('data/audio'):
        os.makedirs('data/audio')
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = uploaded_file.name.split('.')[-1]
    filename = f"session_{session_id}_steg_{step_number}_{timestamp}.{file_extension}"
    filepath = os.path.join('data/audio', filename)
    
    with open(filepath, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    
    return filepath

def save_recorded_audio(audio_bytes: bytes, session_id, step_number):
    """
    Spara binärt WAV‐innehåll (bytes) från streamlit_audiorec till disk.
    Returnerar sökväg till sparad fil.
    """
    if not audio_bytes:
        return None

    if not os.path.exists('data/audio'):
        os.makedirs('data/audio')
    
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"session_{session_id}_steg_{step_number}_recorded_{timestamp}.wav"
    filepath = os.path.join('data/audio', filename)
    
    with open(filepath, 'wb') as f:
        f.write(audio_bytes)
    
    st.write(f"DEBUG: Sparade ljudfil i {filepath}")
    return filepath

def transcribe_audio_openai(audio_file_path):
    """
    Transkribera sparad ljudfil med OpenAI Whisper‐API (via openai-paketet).
    Returnerar transkriberingen som sträng eller None vid fel.
    """
    try:
        from openai import OpenAI
        
        api_key = os.getenv("OPENAI_API_KEY")
        if not api_key:
            st.error("Ingen OPENAI_API_KEY hittad i miljön.")
            return None

        client = OpenAI(api_key=api_key)
        
        with open(audio_file_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return response.text
    except Exception as e:
        st.error(f"Fel vid transkribering med OpenAI: {e}")
        return None

def transcribe_uploaded_file(uploaded_file, session_id, step_number):
    """
    Spara och transkribera en uppladdad ljudfil.
    Returnerar tuple: (transcription_text, audio_file_path)
    """
    try:
        # Spara filen först
        audio_path = save_uploaded_audio(uploaded_file, session_id, step_number)
        
        if audio_path:
            # Transkribera filen
            transcription = transcribe_audio_openai(audio_path)
            return transcription, audio_path
        else:
            return None, None
            
    except Exception as e:
        st.error(f"Fel vid hantering av uppladdad fil: {e}")
        return None, None

def validate_audio_file(uploaded_file, max_duration_seconds=36):
    """
    Kontrollera att uppladdad fil är under maxstorlek (MB).
    """
    max_size_mb = 5
    if uploaded_file.size > max_size_mb * 1024 * 1024:
        return False, f"Filen är för stor. Max: {max_size_mb} MB."
    return True, "OK"

def display_audio_player(audio_file_path):
    """
    Visa en Streamlit-spelare för den sparade ljudfilen.
    """
    if audio_file_path and os.path.exists(audio_file_path):
        with open(audio_file_path, 'rb') as f:
            audio_bytes = f.read()
            st.audio(audio_bytes, format='audio/wav')

def record_audio_streamlit(session_id, step_number, key_prefix=""):
    """
    Placeholder för ljudinspelning - använd filuppladdning istället.
    """
    st.warning("⚠️ Direktinspelning är inte tillgänglig i denna miljö.")
    st.info("""
    **Använd istället:**
    1. Spela in ljud med din telefon eller dator
    2. Spara som .wav eller .mp3 fil
    3. Ladda upp filen med "Browse files" ovan
    4. Klicka "Transkribera uppladdad fil"
    """)
    return None