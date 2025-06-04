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
        from openai import OpenAI
        import os
        
        # Kontrollera att API-nyckel finns
        api_key = os.getenv('OPENAI_API_KEY')
        if not api_key:
            st.error("OPENAI_API_KEY saknas i miljövariabler")
            return None
            
        client = OpenAI(api_key=api_key)
        
        with open(audio_file_path, "rb") as audio_file:
            response = client.audio.transcriptions.create(
                model="whisper-1",
                file=audio_file
            )
        return response.text
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
    Spela in ljud med Streamlit WebRTC-komponenten.
    Returnerar inspelade ljudet som bytes, annars None.
    """
    st.write("🎤 **Ljudinspelning:**")
    
    try:
        from streamlit_webrtc import webrtc_streamer, WebRtcMode
        import av
        import threading
        import queue
        
        # Global variabel för att lagra ljuddata
        audio_frames = queue.Queue()
        
        def audio_frame_callback(frame):
            audio_frames.put(frame)
        
        component_key = f"{key_prefix}_webrtc_{session_id}_{step_number}"
        
        webrtc_ctx = webrtc_streamer(
            key=component_key,
            mode=WebRtcMode.SENDONLY,
            audio_frame_callback=audio_frame_callback,
            media_stream_constraints={"video": False, "audio": True},
            rtc_configuration={"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]}
        )
        
        if webrtc_ctx.audio_receiver:
            st.info("🎙️ Ljudinspelning är aktiv. Klicka på 'Stop' för att avsluta.")
            
            if st.button("💾 Spara inspelning", key=f"{key_prefix}_save_{session_id}_{step_number}"):
                # Samla ihop ljudframes
                frames = []
                while not audio_frames.empty():
                    frame = audio_frames.get()
                    frames.append(frame)
                
                if frames:
                    # Konvertera till bytes
                    import io
                    import wave
                    
                    # Skapa WAV-fil i minnet
                    wav_buffer = io.BytesIO()
                    with wave.open(wav_buffer, 'wb') as wav_file:
                        wav_file.setnchannels(1)  # Mono
                        wav_file.setsampwidth(2)  # 16-bit
                        wav_file.setframerate(16000)  # 16kHz
                        
                        for frame in frames:
                            wav_file.writeframes(frame.to_ndarray().tobytes())
                    
                    audio_bytes = wav_buffer.getvalue()
                    st.success("✅ Ljudinspelning sparad!")
                    st.audio(audio_bytes, format="audio/wav")
                    return audio_bytes
                else:
                    st.warning("Ingen ljuddata hittades. Försök spela in igen.")
        
        return None
        
    except ImportError:
        # Fallback: Visa instruktioner för manuell uppladdning
        st.warning("⚠️ WebRTC-ljudinspelning är inte tillgänglig.")
        st.info("""
        **Alternativ för ljudinspelning:**
        1. Använd din telefon eller dator för att spela in ljud
        2. Spara filen som .wav eller .mp3
        3. Ladda upp filen med filuppladdaren ovan
        """)
        return None
    except Exception as e:
        st.error(f"Fel vid ljudinspelning: {e}")
        st.info("""
        **Alternativ för ljudinspelning:**
        1. Använd din telefon eller dator för att spela in ljud
        2. Spara filen som .wav eller .mp3
        3. Ladda upp filen med filuppladdaren ovan
        """)
        return None