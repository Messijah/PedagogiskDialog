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

def transcribe_uploaded_file(uploaded_file, session_id, step_number):
    """
    Spara och transkribera en uppladdad ljudfil.
    Returnerar tuple: (transcription_text, audio_file_path)
    """
    try:
        # Spara filen först
        audio_path = save_uploaded_audio(uploaded_file, session_id, step_number)
        
        if audio_path:
            # Kontrollera filstorlek
            file_size_mb = uploaded_file.size / (1024 * 1024)
            st.info(f"📊 Filstorlek: {file_size_mb:.1f} MB")
            
            # Använd segmenterad transkribering för stora filer
            if file_size_mb > 20:  # Om filen är större än 20 MB
                st.info("🔄 Stor fil upptäckt - använder segmenterad transkribering för bästa resultat...")
                transcription = transcribe_large_audio_file(audio_path)
            else:
                # Transkribera normalt för mindre filer
                transcription = transcribe_audio_openai(audio_path)
            
            return transcription, audio_path
        else:
            return None, None
            
    except Exception as e:
        st.error(f"Fel vid hantering av uppladdad fil: {e}")
        return None, None

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

def split_audio_file(audio_file_path, segment_duration_minutes=15):
    """
    Dela upp en ljudfil i segment för transkribering.
    Returnerar lista med sökvägar till segment-filer.
    """
    try:
        from pydub import AudioSegment
        import math
        
        # Ladda ljudfilen
        audio = AudioSegment.from_file(audio_file_path)
        
        # Beräkna segment-längd i millisekunder
        segment_length_ms = segment_duration_minutes * 60 * 1000
        
        # Beräkna antal segment
        total_length_ms = len(audio)
        num_segments = math.ceil(total_length_ms / segment_length_ms)
        
        segment_paths = []
        base_path = audio_file_path.rsplit('.', 1)[0]
        
        for i in range(num_segments):
            start_ms = i * segment_length_ms
            end_ms = min((i + 1) * segment_length_ms, total_length_ms)
            
            # Extrahera segment
            segment = audio[start_ms:end_ms]
            
            # Spara segment
            segment_path = f"{base_path}_segment_{i+1}.wav"
            segment.export(segment_path, format="wav")
            segment_paths.append(segment_path)
        
        return segment_paths
        
    except Exception as e:
        st.error(f"Fel vid segmentering av ljudfil: {e}")
        return []

def transcribe_large_audio_file(audio_file_path):
    """
    Transkribera en stor ljudfil genom att dela upp den i segment.
    Returnerar sammanslagen transkribering.
    """
    try:
        # Dela upp filen i 15-minuters segment
        st.info("🔄 Delar upp ljudfilen i 15-minuters segment för optimal transkribering...")
        segment_paths = split_audio_file(audio_file_path, segment_duration_minutes=15)
        
        if not segment_paths:
            st.error("Kunde inte dela upp ljudfilen")
            return None
        
        st.info(f"📂 Skapade {len(segment_paths)} segment för transkribering")
        
        # Transkribera varje segment
        transcriptions = []
        for i, segment_path in enumerate(segment_paths):
            st.info(f"🎯 Transkriberar segment {i+1} av {len(segment_paths)}...")
            
            transcription = transcribe_audio_openai(segment_path)
            if transcription:
                transcriptions.append(f"[Segment {i+1}]\n{transcription}")
            else:
                st.warning(f"⚠️ Segment {i+1} kunde inte transkriberas")
            
            # Rensa segment-fil efter transkribering
            try:
                os.remove(segment_path)
            except:
                pass
        
        if transcriptions:
            # Slå ihop alla transkribering
            full_transcription = "\n\n".join(transcriptions)
            st.success(f"✅ Transkribering klar för alla {len(transcriptions)} segment!")
            return full_transcription
        else:
            st.error("❌ Ingen transkribering lyckades")
            return None
            
    except Exception as e:
        st.error(f"Fel vid segmenterad transkribering: {e}")
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
    max_size_mb = 100  # Ökat från 5 MB till 100 MB för längre samtal
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
    Spela in ljud med streamlit-webrtc komponenten.
    Returnerar inspelade ljudet som bytes, annars None.
    """
    st.write("🎤 **Ljudinspelning:**")
    
    try:
        from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
        import av
        import numpy as np
        import io
        import wave
        
        # WebRTC konfiguration
        rtc_configuration = RTCConfiguration({
            "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
        })
        
        component_key = f"{key_prefix}_webrtc_{session_id}_{step_number}"
        
        # Skapa en container för ljuddata
        if f"audio_frames_{component_key}" not in st.session_state:
            st.session_state[f"audio_frames_{component_key}"] = []
        
        def audio_frame_callback(frame):
            """Callback för att samla ljudframes"""
            audio_array = frame.to_ndarray()
            st.session_state[f"audio_frames_{component_key}"].append(audio_array)
            return frame
        
        # WebRTC streamer för ljudinspelning
        webrtc_ctx = webrtc_streamer(
            key=component_key,
            mode=WebRtcMode.SENDONLY,
            audio_frame_callback=audio_frame_callback,
            rtc_configuration=rtc_configuration,
            media_stream_constraints={"video": False, "audio": True},
            async_processing=True,
        )
        
        if webrtc_ctx.state.playing:
            st.info("🔴 Spelar in... Klicka 'STOP' när du är klar")
        elif not webrtc_ctx.state.playing and len(st.session_state[f"audio_frames_{component_key}"]) > 0:
            # Konvertera frames till WAV-bytes
            audio_frames = st.session_state[f"audio_frames_{component_key}"]
            if audio_frames:
                # Kombinera alla frames
                audio_data = np.concatenate(audio_frames, axis=0)
                
                # Konvertera till WAV-format
                sample_rate = 48000  # WebRTC standard
                audio_bytes_io = io.BytesIO()
                
                with wave.open(audio_bytes_io, 'wb') as wav_file:
                    wav_file.setnchannels(1)  # Mono
                    wav_file.setsampwidth(2)  # 16-bit
                    wav_file.setframerate(sample_rate)
                    
                    # Konvertera float till int16
                    audio_int16 = (audio_data * 32767).astype(np.int16)
                    wav_file.writeframes(audio_int16.tobytes())
                
                audio_bytes = audio_bytes_io.getvalue()
                
                st.success("✅ Ljudinspelning klar!")
                st.audio(audio_bytes, format="audio/wav")
                
                # Rensa frames för nästa inspelning
                st.session_state[f"audio_frames_{component_key}"] = []
                
                return audio_bytes
        else:
            st.info("Klicka på 'START' för att börja spela in ljud")
            
        return None
            
    except ImportError:
        # Fallback: Visa instruktioner för manuell uppladdning
        st.warning("⚠️ Ljudinspelningskomponenten är inte tillgänglig.")
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

def record_and_transcribe_audio(session_id, step_number, key_prefix=""):
    """
    Ljudinspelning med Streamlits inbyggda st.audio_input.
    Returnerar tuple: (audio_file_path, transcription_text)
    """
    st.write("🎤 **Ljudinspelning:**")
    
    # Varning för långa samtal
    st.info("💡 **Tips för långa samtal (över 15 min):** Systemet hanterar automatiskt segmentering och transkribering för optimala resultat.")
    
    # Försök använda Streamlits inbyggda audio_input först
    try:
        component_key = f"{key_prefix}_audio_input_{session_id}_{step_number}"
        
        # Använd Streamlits inbyggda ljudinspelning
        audio_bytes = st.audio_input("Spela in ljud", key=component_key)
        
        if audio_bytes is not None:
            st.success("✅ Ljudinspelning mottagen!")
            st.audio(audio_bytes, format="audio/wav")
            
            # Kontrollera filstorlek och längd
            file_size_mb = len(audio_bytes.getvalue()) / (1024 * 1024)
            st.info(f"📊 Filstorlek: {file_size_mb:.1f} MB")
            
            # Spara ljudfilen automatiskt
            with st.spinner("Sparar ljudfil..."):
                audio_file_path = save_recorded_audio(audio_bytes.getvalue(), session_id, step_number)
            
            if audio_file_path:
                st.success(f"💾 Ljudfil sparad: {os.path.basename(audio_file_path)}")
                
                # Kontrollera om filen behöver segmenteras för transkribering
                if file_size_mb > 20:  # Om filen är större än 20 MB, segmentera den
                    st.info("🔄 Stor fil upptäckt - använder segmenterad transkribering för bästa resultat...")
                    transcription = transcribe_large_audio_file(audio_file_path)
                else:
                    # Transkribera normalt för mindre filer
                    with st.spinner("Transkriberar ljud med OpenAI Whisper..."):
                        transcription = transcribe_audio_openai(audio_file_path)
                
                if transcription:
                    st.success("✅ Transkribering klar!")
                    st.markdown("### 📝 Transkribering:")
                    st.write(transcription)
                    
                    return audio_file_path, transcription
                else:
                    st.error("❌ Transkribering misslyckades")
                    return audio_file_path, None
            else:
                st.error("❌ Kunde inte spara ljudfil")
                return None, None
        else:
            st.info("Klicka på mikrofon-ikonen ovan för att spela in ljud")
            return None, None
            
    except Exception as e:
        # Fallback till WebRTC för lokal utveckling
        st.warning("⚠️ Inbyggd ljudinspelning inte tillgänglig. Försöker WebRTC...")
        
        try:
            from streamlit_webrtc import webrtc_streamer, WebRtcMode, RTCConfiguration
            import av
            import numpy as np
            import io
            import wave
            
            # WebRTC konfiguration
            rtc_configuration = RTCConfiguration({
                "iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]
            })
            
            component_key = f"{key_prefix}_webrtc_{session_id}_{step_number}"
            
            # Skapa en container för ljuddata
            if f"audio_frames_{component_key}" not in st.session_state:
                st.session_state[f"audio_frames_{component_key}"] = []
            
            # Skapa state för att hålla koll på om vi redan har processat denna inspelning
            processed_key = f"processed_{component_key}"
            if processed_key not in st.session_state:
                st.session_state[processed_key] = False
            
            def audio_frame_callback(frame):
                """Callback för att samla ljudframes"""
                audio_array = frame.to_ndarray()
                st.session_state[f"audio_frames_{component_key}"].append(audio_array)
                return frame
            
            # WebRTC streamer för ljudinspelning
            webrtc_ctx = webrtc_streamer(
                key=component_key,
                mode=WebRtcMode.SENDONLY,
                audio_frame_callback=audio_frame_callback,
                rtc_configuration=rtc_configuration,
                media_stream_constraints={"video": False, "audio": True},
                async_processing=True,
            )
            
            if webrtc_ctx.state.playing:
                st.info("🔴 Spelar in... Klicka 'STOP' när du är klar")
                # Reset processed state när vi börjar en ny inspelning
                st.session_state[processed_key] = False
                
            elif not webrtc_ctx.state.playing and len(st.session_state[f"audio_frames_{component_key}"]) > 0 and not st.session_state[processed_key]:
                # Konvertera frames till WAV-bytes
                audio_frames = st.session_state[f"audio_frames_{component_key}"]
                if audio_frames:
                    with st.spinner("Bearbetar ljudinspelning..."):
                        # Kombinera alla frames
                        audio_data = np.concatenate(audio_frames, axis=0)
                        
                        # Konvertera till WAV-format
                        sample_rate = 48000  # WebRTC standard
                        audio_bytes_io = io.BytesIO()
                        
                        with wave.open(audio_bytes_io, 'wb') as wav_file:
                            wav_file.setnchannels(1)  # Mono
                            wav_file.setsampwidth(2)  # 16-bit
                            wav_file.setframerate(sample_rate)
                            
                            # Konvertera float till int16
                            audio_int16 = (audio_data * 32767).astype(np.int16)
                            wav_file.writeframes(audio_int16.tobytes())
                        
                        audio_bytes = audio_bytes_io.getvalue()
                    
                    st.success("✅ Ljudinspelning klar!")
                    st.audio(audio_bytes, format="audio/wav")
                    
                    # Spara ljudfilen automatiskt
                    with st.spinner("Sparar ljudfil..."):
                        audio_file_path = save_recorded_audio(audio_bytes, session_id, step_number)
                    
                    if audio_file_path:
                        st.success(f"💾 Ljudfil sparad: {os.path.basename(audio_file_path)}")
                        
                        # Kontrollera filstorlek för segmentering
                        file_size_mb = len(audio_bytes) / (1024 * 1024)
                        st.info(f"📊 Filstorlek: {file_size_mb:.1f} MB")
                        
                        # Transkribera automatiskt med segmentering för stora filer
                        if file_size_mb > 20:
                            st.info("🔄 Stor fil upptäckt - använder segmenterad transkribering för bästa resultat...")
                            transcription = transcribe_large_audio_file(audio_file_path)
                        else:
                            with st.spinner("Transkriberar ljud med OpenAI Whisper..."):
                                transcription = transcribe_audio_openai(audio_file_path)
                        
                        if transcription:
                            st.success("✅ Transkribering klar!")
                            st.markdown("### 📝 Transkribering:")
                            st.write(transcription)
                            
                            # Markera som processat
                            st.session_state[processed_key] = True
                            
                            # Rensa frames för nästa inspelning
                            st.session_state[f"audio_frames_{component_key}"] = []
                            
                            return audio_file_path, transcription
                        else:
                            st.error("❌ Transkribering misslyckades")
                            return audio_file_path, None
                    else:
                        st.error("❌ Kunde inte spara ljudfil")
                        return None, None
            else:
                st.info("Klicka på 'START' för att börja spela in ljud")
                
            return None, None
                
        except Exception as e2:
            # Sista fallback
            st.error("❌ Ingen ljudinspelningsmetod tillgänglig.")
            st.info("""
            **Alternativ för ljudinspelning:**
            1. Använd din telefon eller dator för att spela in ljud
            2. Spara filen som .wav eller .mp3
            3. Ladda upp filen med filuppladdaren ovan
            """)
            return None, None