import streamlit as st
from utils.session_manager import get_current_session, is_step_accessible
from utils.ai_helper import analyze_perspectives_steg2
from utils.database import update_session_step2
from utils.audio_handler import transcribe_uploaded_file, validate_audio_file, display_audio_player, record_audio_streamlit, save_recorded_audio, transcribe_audio_openai

# Konfigurera sida
st.set_page_config(
    page_title="Steg 2 - Perspektivinventering",
    page_icon="👥",
    layout="wide"
)

# Kontrollera åtkomst
if not is_step_accessible(2):
    st.error("Du måste först slutföra Steg 1 innan du kan komma åt Steg 2.")
    if st.button("← Gå till Steg 1"):
        st.switch_page("pages/steg1.py")
    st.stop()

current_session = get_current_session()
if not current_session:
    st.error("Ingen aktiv session. Gå tillbaka till startsidan.")
    if st.button("← Tillbaka till start"):
        st.switch_page("main.py")
    st.stop()

# Header
st.title("👥 Steg 2: Perspektivinventering")
st.markdown(f"**Session:** {current_session['session_name']} | **Rektor:** {current_session['rektor_name']}")

# Navigation
col1, col2, col3 = st.columns([1, 1, 3])
with col1:
    if st.button("← Steg 1"):
        st.switch_page("pages/steg1.py")
with col2:
    if st.button("🏠 Start"):
        st.switch_page("main.py")

st.markdown("---")

# Visa problembeskrivning från Steg 1
st.subheader("📋 Problemformulering från Steg 1")
st.info(current_session['problem_beskrivning'])

# Visa befintlig data om den finns
if current_session['steg2_approved']:
    st.success("✅ Steg 2 är redan slutfört!")
    
    if current_session['steg2_transcript']:
        st.subheader("Transkribering:")
        with st.expander("Visa transkribering"):
            st.write(current_session['steg2_transcript'])
    
    if current_session['steg2_ai_analysis']:
        st.subheader("AI-analys som godkändes:")
        st.markdown(current_session['steg2_ai_analysis'])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📝 Redigera detta steg"):
            st.session_state.edit_steg2 = True
            st.rerun()
    
    with col2:
        if st.button("← Tillbaka till Steg 1"):
            st.switch_page("pages/steg1.py")
    
    with col3:
        if st.button("➡️ Gå till Steg 3"):
            st.switch_page("pages/steg3.py")
    
    # Om inte i redigeringsläge, stoppa här
    if not st.session_state.get('edit_steg2', False):
        st.stop()

# Instruktioner
st.subheader("📝 Instruktioner för Steg 2")
st.markdown("""
Nu ska du genomföra ett samtal med din personalgrupp där olika perspektiv på problemet får komma fram.

**Så här gör du:**
1. **Presentera problemet** för gruppen enligt AI-förslagen från Steg 1
2. **Spela in samtalet** eller ladda upp en ljudfil
3. **Låt AI analysera** de olika perspektiv som framkommer
4. **Välj** vilka perspektiv som ska fördjupas i Steg 3
""")

# Ljudinspelning/uppladdning
st.markdown("---")
st.subheader("🎤 Spela in eller ladda upp samtal")

# Flikar för olika alternativ
tab1, tab2 = st.tabs(["📁 Ladda upp ljudfil", "🎤 Spela in direkt"])

with tab1:
    st.markdown("**Ladda upp en ljudfil från ditt samtal:**")
    
    uploaded_file = st.file_uploader(
        "Välj ljudfil",
        type=['wav', 'mp3', 'm4a', 'mp4'],
        help="Stödda format: WAV, MP3, M4A, MP4. Max storlek: 200 MB"
    )
    
    if uploaded_file:
        # Validera fil
        is_valid, message = validate_audio_file(uploaded_file)
        
        if is_valid:
            st.success(f"✅ Fil uppladdad: {uploaded_file.name}")
            
            # Visa ljudspelare
            st.audio(uploaded_file.getvalue())
            
            # Transkribera knapp
            if st.button("🔤 Transkribera ljudfil", type="primary"):
                with st.spinner("Transkriberar ljudfil... Detta kan ta några minuter."):
                    try:
                        transcript, audio_path = transcribe_uploaded_file(
                            uploaded_file, 
                            current_session['id'], 
                            2
                        )
                        
                        if transcript:
                            st.session_state.transcript_steg2 = transcript
                            st.session_state.audio_path_steg2 = audio_path
                            st.success("✅ Transkribering klar!")
                            st.rerun()
                        else:
                            st.error("Kunde inte transkribera filen. Kontrollera att det är en giltig ljudfil.")
                    except Exception as e:
                        st.error(f"Fel vid transkribering: {str(e)}")
        else:
            st.error(f"❌ {message}")

with tab2:
    st.markdown("**Spela in direkt i webbläsaren:**")
    
    # Försök använda streamlit-audio-recorder
    try:
        audio_bytes = record_audio_streamlit()
        
        if audio_bytes:
            st.success("✅ Inspelning mottagen!")
            
            if st.button("🔤 Transkribera inspelning", type="primary"):
                with st.spinner("Sparar och transkriberar inspelning..."):
                    try:
                        # Spara inspelning
                        audio_path = save_recorded_audio(audio_bytes, current_session['id'], 2)
                        
                        # Transkribera
                        transcript = transcribe_audio_openai(audio_path)
                        
                        if transcript:
                            st.session_state.transcript_steg2 = transcript
                            st.session_state.audio_path_steg2 = audio_path
                            st.success("✅ Transkribering klar!")
                            st.rerun()
                        else:
                            st.error("Kunde inte transkribera inspelningen.")
                    except Exception as e:
                        st.error(f"Fel vid transkribering: {str(e)}")
    except:
        st.warning("Direktinspelning inte tillgänglig. Använd filuppladdning istället.")

# Visa transkribering om den finns
if 'transcript_steg2' in st.session_state or current_session.get('steg2_transcript'):
    transcript = st.session_state.get('transcript_steg2', current_session.get('steg2_transcript'))
    
    st.markdown("---")
    st.subheader("📝 Transkribering av samtalet")
    
    # Visa transkribering i redigerbar textområde
    edited_transcript = st.text_area(
        "Granska och redigera transkriberingen om nödvändigt:",
        value=transcript,
        height=300,
        help="Du kan redigera transkriberingen för att korrigera eventuella fel"
    )
    
    # Uppdatera transcript om den redigerats
    if edited_transcript != transcript:
        st.session_state.transcript_steg2 = edited_transcript
    
    # Analysera perspektiv
    if st.button("🤖 Analysera perspektiv", type="primary"):
        with st.spinner("AI analyserar de olika perspektiven i samtalet..."):
            analysis = analyze_perspectives_steg2(
                current_session['problem_beskrivning'],
                edited_transcript
            )
            
            if analysis:
                st.session_state.analysis_steg2 = analysis
                st.rerun()
            else:
                st.error("Kunde inte analysera perspektiven. Försök igen.")

# Visa AI-analys om den finns
if 'analysis_steg2' in st.session_state or current_session.get('steg2_ai_analysis'):
    analysis = st.session_state.get('analysis_steg2', current_session.get('steg2_ai_analysis'))
    
    st.markdown("---")
    st.subheader("🤖 AI-analys av perspektiv")
    st.markdown(analysis)
    
    # Val av perspektiv för fördjupning
    st.markdown("---")
    st.subheader("🎯 Välj perspektiv för fördjupning i Steg 3")
    st.markdown("Baserat på analysen ovan, vilka 2-3 perspektiv vill du fördjupa i nästa steg?")
    
    selected_perspectives = st.text_area(
        "Beskriv de perspektiv som ska fördjupas:",
        height=150,
        placeholder="Exempel: 1. Lärarnas oro för ökad arbetsbelastning, 2. Elevernas behov av mer individuell support, 3. Föräldrarnas förväntningar på digitala verktyg",
        help="Skriv de 2-3 viktigaste perspektiven som behöver fördjupas"
    )
    
    # Kontrollknappar
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if st.button("✅ Godkänn och fortsätt till Steg 3", type="primary"):
            if not selected_perspectives.strip():
                st.error("Du måste välja perspektiv för fördjupning innan du kan fortsätta.")
            else:
                # Spara i databas
                transcript_to_save = st.session_state.get('transcript_steg2', current_session.get('steg2_transcript'))
                audio_path_to_save = st.session_state.get('audio_path_steg2', current_session.get('steg2_audio_path'))
                
                update_session_step2(
                    current_session['id'],
                    audio_path_to_save,
                    transcript_to_save,
                    analysis,
                    selected_perspectives,
                    approved=True
                )
                
                # Rensa session state
                for key in ['transcript_steg2', 'analysis_steg2', 'audio_path_steg2', 'edit_steg2']:
                    if key in st.session_state:
                        del st.session_state[key]
                
                st.success("Steg 2 godkänt! Går till Steg 3...")
                st.switch_page("pages/steg3.py")
    
    with col2:
        if st.button("🔄 Analysera om"):
            # Ta bort analys så användaren kan köra om
            if 'analysis_steg2' in st.session_state:
                del st.session_state.analysis_steg2
            st.rerun()
    
    with col3:
        if st.button("💾 Spara utkast"):
            # Spara utan att godkänna
            transcript_to_save = st.session_state.get('transcript_steg2', current_session.get('steg2_transcript'))
            audio_path_to_save = st.session_state.get('audio_path_steg2', current_session.get('steg2_audio_path'))
            
            update_session_step2(
                current_session['id'],
                audio_path_to_save,
                transcript_to_save,
                analysis,
                selected_perspectives if selected_perspectives.strip() else None,
                approved=False
            )
            st.success("Utkast sparat!")

# Hjälptext
st.markdown("---")
with st.expander("💡 Tips för ett bra perspektivsamtal"):
    st.markdown("""
    **För att få fram olika perspektiv:**
    
    - **Ställ öppna frågor** som uppmuntrar reflektion
    - **Låt alla komma till tals** - ge tid för tystlåtna deltagare
    - **Undvik att döma** olika åsikter i detta skede
    - **Uppmuntra konkreta exempel** från deltagarnas erfarenheter
    - **Dokumentera** även minoritetsåsikter och avvikande perspektiv
    
    **Bra frågor att ställa:**
    - "Vad är er första reaktion på detta problem?"
    - "Vilka olika sätt finns det att se på denna fråga?"
    - "Vad skulle ni behöva för att känna er trygga med en förändring?"
    - "Vilka hinder ser ni? Vilka möjligheter?"
    
    **Tekniska tips:**
    - Placera inspelningsenheten centralt i rummet
    - Be deltagarna tala tydligt och en i taget
    - Kontrollera ljudkvaliteten innan ni börjar
    - Ha backup-plan om tekniken krånglar
    """)

# Footer
st.markdown("---")
st.caption("Steg 2 av 4 | SamtalsBot - AI-stödd samtalsmodell för rektorer")