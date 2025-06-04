import streamlit as st

st.title("Test av ljudinspelning")

try:
    from st_audiorec import st_audiorec
    st.success("✅ st_audiorec importerades framgångsrikt!")
    
    st.write("🎤 **Testa ljudinspelning:**")
    audio_bytes = st_audiorec()
    
    if audio_bytes is not None:
        st.success("✅ Ljudinspelning fungerar!")
        st.audio(audio_bytes, format="audio/wav")
    else:
        st.info("Klicka på mikrofon-knappen för att spela in ljud")
        
except ImportError as e:
    st.error(f"❌ Kunde inte importera st_audiorec: {e}")
    
    try:
        from streamlit_audiorec import st_audiorec
        st.success("✅ streamlit_audiorec importerades framgångsrikt!")
        
        st.write("🎤 **Testa ljudinspelning:**")
        audio_bytes = st_audiorec()
        
        if audio_bytes is not None:
            st.success("✅ Ljudinspelning fungerar!")
            st.audio(audio_bytes, format="audio/wav")
        else:
            st.info("Klicka på mikrofon-knappen för att spela in ljud")
            
    except ImportError as e2:
        st.error(f"❌ Kunde inte importera streamlit_audiorec heller: {e2}")
        
        try:
            from streamlit_audio_recorder import audio_recorder
            st.success("✅ streamlit_audio_recorder importerades framgångsrikt!")
            
            st.write("🎤 **Testa ljudinspelning:**")
            audio_bytes = audio_recorder(
                text="Spela in",
                recording_color="#e8b62c",
                neutral_color="#6aa36f",
                icon_name="microphone",
                icon_size="2x",
                key="test_recorder"
            )
            
            if audio_bytes is not None:
                st.success("✅ Ljudinspelning fungerar!")
                st.audio(audio_bytes, format="audio/wav")
            else:
                st.info("Klicka på mikrofon-knappen för att spela in ljud")
                
        except ImportError as e3:
            st.error(f"❌ Kunde inte importera någon ljudinspelningskomponent: {e3}")