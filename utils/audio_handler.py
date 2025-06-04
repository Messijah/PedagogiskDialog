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
    Spara binärt wav‐innehåll (bytes) som spelats in via streamlit_audio_recorder.
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
    
    return filepath

def transcribe_audio_openai(audio_file_path):
    """
    Transkribera en sparad ljudfil med OpenAI Whisper-API.
    Returnerar transkribering som sträng eller None vid fel.
    """
    try:
        import openai
        # Förväntar att OPENAI_API_KEY är satt i miljövariabler
        with open(audio_file_path, "rb") as audio_file:
            response = openai.Audio.transcribe(
                model="whisper-1",
                file=audio_file
            )
        return response["text"]
    except Exception as e:
        st.error(f"Fel vid transkribering: {e}")
        return None

def get_audio_duration(audio_file_path):
    """
    Hämta ljudfilens längd (sekunder). Kräver pydub.
    """
    try:
        from pydub import AudioSegment
        audio = AudioSegment.from_file(audio_file_path)
        return round(audio.duration_seconds)
    except:
        return None

def format_duration(seconds: int):
    """
    Formatera sekunder till "Xm Ys" eller "Ys".
    """
    minutes = seconds // 60
    seconds = seconds % 60
    if minutes:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

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
        dur = get_audio_duration(audio_file_path)
        if dur:
            st.caption(f"Längd: {format_duration(dur)}")

def record_audio_streamlit(session_id, step_number, key_prefix=""):
    """
    Spela in ljud med Streamlit Audio Recorder-komponenten.
    Returnerar inspelade ljudet som bytes, annars None.
    """
    try:
        # OBS: paketet heter 'streamlit_audiorec' i miljön
        from streamlit_audiorec import audio_recorder
    except ImportError:
        st.error("streamlit_audiorec saknas. Kontrollera att du har 'streamlit-audiorec @ git+https://github.com/stefanrmmr/streamlit-audio-recorder.git' i requirements.txt och redeployat.")
        return None

    st.write("🎤 **Klicka på knappen nedan för att spela in ljud:**")
    component_key = f"{key_prefix}_recorder_{session_id}_{step_number}"
    audio_bytes = audio_recorder(
        text="Spela in",
        recording_color="#e8b62c",
        neutral_color="#6aa36f",
        icon_name="microphone",
        icon_size="2x",
        key=component_key
    )
    if audio_bytes:
        st.audio(audio_bytes, format="audio/wav")
        return audio_bytes
    return None