import streamlit as st
import whisper
import os
import tempfile
from datetime import datetime
import io

def save_uploaded_audio(uploaded_file, session_id, step_number):
    """Spara uppladdad ljudfil"""
    if not os.path.exists('data/audio'):
        os.makedirs('data/audio')
    
    # Skapa unikt filnamn
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    file_extension = uploaded_file.name.split('.')[-1]
    filename = f"session_{session_id}_steg_{step_number}_{timestamp}.{file_extension}"
    filepath = os.path.join('data/audio', filename)
    
    # Spara filen
    with open(filepath, 'wb') as f:
        f.write(uploaded_file.getbuffer())
    
    return filepath

@st.cache_data(show_spinner=False)
def transcribe_audio_whisper(audio_file_path):
    """Transkribera ljudfil med Whisper"""
    try:
        # Ladda Whisper modell
        model = whisper.load_model("base")
        
        # Transkribera
        result = model.transcribe(audio_file_path, language="sv")
        
        return result["text"]
    except Exception as e:
        st.error(f"Fel vid transkribering: {str(e)}")
        return None

def transcribe_audio_openai(audio_file_path):
    """Transkribera ljudfil med OpenAI Whisper API"""
    try:
        import openai
        
        with open(audio_file_path, "rb") as audio_file:
            transcript = openai.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file,
                language="sv"
            )
        
        return transcript.text
    except Exception as e:
        st.error(f"Fel vid transkribering med OpenAI API: {str(e)}")
        return None

def transcribe_uploaded_file(uploaded_file, session_id, step_number, use_openai_api=True):
    """Transkribera uppladdad ljudfil"""
    if uploaded_file is None:
        return None
    
    # Spara filen temporärt
    filepath = save_uploaded_audio(uploaded_file, session_id, step_number)
    
    # Transkribera
    if use_openai_api:
        transcript = transcribe_audio_openai(filepath)
    else:
        transcript = transcribe_audio_whisper(filepath)
    
    return transcript, filepath

def get_audio_duration(audio_file_path):
    """Hämta längd på ljudfil"""
    try:
        import wave
        with wave.open(audio_file_path, 'r') as wav_file:
            frames = wav_file.getnframes()
            sample_rate = wav_file.getframerate()
            duration = frames / float(sample_rate)
            return duration
    except:
        return None

def format_duration(seconds):
    """Formatera duration till läsbar text"""
    if seconds is None:
        return "Okänd längd"
    
    minutes = int(seconds // 60)
    seconds = int(seconds % 60)
    
    if minutes > 0:
        return f"{minutes}m {seconds}s"
    else:
        return f"{seconds}s"

def validate_audio_file(uploaded_file, max_duration_seconds=3600):
    """Validera uppladdad ljudfil"""
    if uploaded_file is None:
        return False, "Ingen fil uppladdad"
    
    # Kontrollera filtyp
    allowed_types = ['audio/wav', 'audio/mp3', 'audio/mpeg', 'audio/m4a', 'audio/x-m4a']
    if uploaded_file.type not in allowed_types:
        return False, f"Filtyp {uploaded_file.type} stöds inte. Använd WAV, MP3 eller M4A."
    
    # Kontrollera filstorlek (ungefärlig kontroll)
    max_size_mb = 200  # 200 MB
    if uploaded_file.size > max_size_mb * 1024 * 1024:
        return False, f"Filen är för stor. Max storlek: {max_size_mb} MB"
    
    return True, "OK"

def display_audio_player(audio_file_path):
    """Visa ljudspelare för uppladdad fil"""
    if audio_file_path and os.path.exists(audio_file_path):
        with open(audio_file_path, 'rb') as audio_file:
            audio_bytes = audio_file.read()
            st.audio(audio_bytes, format='audio/wav')
        
        # Visa duration om möjligt
        duration = get_audio_duration(audio_file_path)
        if duration:
            st.caption(f"Längd: {format_duration(duration)}")

def cleanup_old_audio_files(days_old=7):
    """Rensa gamla ljudfiler"""
    audio_dir = 'data/audio'
    if not os.path.exists(audio_dir):
        return
    
    cutoff_time = datetime.now().timestamp() - (days_old * 24 * 60 * 60)
    
    for filename in os.listdir(audio_dir):
        filepath = os.path.join(audio_dir, filename)
        if os.path.isfile(filepath):
            file_time = os.path.getmtime(filepath)
            if file_time < cutoff_time:
                try:
                    os.remove(filepath)
                except:
                    pass  # Ignorera fel vid borttagning

# Streamlit Audio Recorder integration (om tillgänglig)
def record_audio_streamlit():
    """Spela in ljud med Streamlit Audio Recorder"""
    try:
        from streamlit_audio_recorder import audio_recorder
        
        st.write("🎤 Klicka för att börja spela in:")
        audio_bytes = audio_recorder(
            text="Klicka för att spela in",
            recording_color="#e8b62c",
            neutral_color="#6aa36f",
            icon_name="microphone",
            icon_size="2x"
        )
        
        if audio_bytes:
            st.audio(audio_bytes, format="audio/wav")
            return audio_bytes
        
        return None
    except ImportError:
        st.info("💡 Direktinspelning inte tillgänglig. Använd filuppladdning istället.")
        return None

def save_recorded_audio(audio_bytes, session_id, step_number):
    """Spara inspelat ljud"""
    if not audio_bytes:
        return None
    
    if not os.path.exists('data/audio'):
        os.makedirs('data/audio')
    
    # Skapa filnamn
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"session_{session_id}_steg_{step_number}_recorded_{timestamp}.wav"
    filepath = os.path.join('data/audio', filename)
    
    # Spara filen
    with open(filepath, 'wb') as f:
        f.write(audio_bytes)
    
    return filepath