import streamlit as st
from utils.session_manager import get_current_session, is_step_accessible
from utils.ai_helper import analyze_perspectives_steg2
from utils.database import update_session_step2
from utils.audio_handler import validate_audio_file, display_audio_player, save_recorded_audio, transcribe_audio_openai
from utils.audio_text_input import audio_text_input

# Konfigurera sida
st.set_page_config(
    page_title="Steg 2 - Perspektivinventering",
    page_icon=None,
    layout="wide"
)

# Kontrollera åtkomst
if not is_step_accessible(2):
    st.error("Du måste först slutföra Steg 1 innan du kan komma åt Steg 2.")
    if st.button("← Gå till Steg 1"):
        st.switch_page("pages/steg 1.py")
    st.stop()

current_session = get_current_session()
if not current_session:
    st.error("Inget aktivt samtal. Gå tillbaka till startsidan.")
    if st.button("← Tillbaka till start"):
        st.switch_page("main.py")
    st.stop()

# Header
st.title("Steg 2: Perspektivinventering")
st.markdown(f"Samtal: {current_session['session_name']} | Samtalsledare: {current_session['rektor_name']}")

# === NY INSTRUKTION ===
st.info("""
**Nu ska du genomföra ett samtal med din personalgrupp utifrån problemformuleringen från Steg 1.**\n\nEfter samtalet laddar du upp eller klistrar in transkriberingen från detta samtal här nedan.\n\n> Steg 2 handlar om att samla in olika perspektiv på problemet genom ett samtal, inte att analysera samma text som i Steg 1.
""")
# === SLUT NY INSTRUKTION ===

# Navigation
col1, col2, col3 = st.columns([1, 1, 3])
with col1:
    if st.button("← Steg 1"):
        st.switch_page("pages/steg 1.py")
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
            st.switch_page("pages/steg 1.py")
    
    with col3:
        if st.button("➡️ Gå till Steg 3"):
            st.switch_page("pages/steg 3.py")
    
    # Om inte i redigeringsläge, stoppa här
    if not st.session_state.get('edit_steg2', False):
        st.stop()

# Instruktioner
st.subheader("Instruktioner för Steg 2")
st.markdown("""
Genomför ett samtal med din personalgrupp där olika perspektiv på problemet får komma fram.
Så här gör du:
1. Presentera problemet för gruppen
2. Spela in samtalet eller ladda upp en ljudfil
3. Analysera de olika perspektiv som framkommer
4. Välj vilka perspektiv som ska fördjupas i Steg 3
""")

# === NYTT: Gemensam komponent för ljud/text ===
transcript, audio_path = audio_text_input(2, current_session['id'], key_prefix="steg2")
if transcript:
    st.session_state.transcript_steg2 = transcript
    if audio_path:
        st.session_state.audio_path_steg2 = audio_path
# === SLUT NYTT ===

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
    if st.button("Analysera perspektiv", type="primary"):
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
    st.subheader("Analys av perspektiv")
    st.markdown(analysis)
    
    # Val av perspektiv för fördjupning
    st.markdown("---")
    st.subheader("Välj perspektiv för fördjupning i Steg 3")
    st.markdown("Baserat på analysen ovan, vilka 2-3 perspektiv vill du fördjupa i nästa steg?")
    
    # Knapp för att få AI-förslag på perspektiv
    if st.button("Få förslag på perspektiv att fördjupa", type="secondary"):
        with st.spinner("AI föreslår perspektiv baserat på analysen..."):
            # Extrahera förslag från analysen
            suggestion_prompt = f"""
            Baserat på denna analys av perspektiv, föreslå 2-3 konkreta perspektiv som bör fördjupas i nästa steg.
            
            ANALYS:
            {analysis}
            
            Ge endast en kort lista med 2-3 perspektiv som är viktigast att fördjupa, formaterat som:
            1. [Perspektiv 1]
            2. [Perspektiv 2]
            3. [Perspektiv 3]
            """
            
            from utils.ai_helper import get_ai_response
            suggestions = get_ai_response(suggestion_prompt, max_tokens=300)
            if suggestions:
                st.session_state.perspective_suggestions = suggestions
                st.rerun()
    
    # Visa AI-förslag om de finns
    if 'perspective_suggestions' in st.session_state:
        st.info("**AI-förslag på perspektiv att fördjupa:**")
        st.markdown(st.session_state.perspective_suggestions)
        
        # Knapp för att godkänna AI-förslag
        col1, col2 = st.columns([1, 3])
        with col1:
            if st.button("✅ Godkänn AI-förslag", type="secondary"):
                st.session_state.selected_perspectives_text = st.session_state.perspective_suggestions
                st.rerun()
        with col2:
            st.markdown("*Eller skriv egna perspektiv nedan:*")
    
    selected_perspectives = st.text_area(
        "Beskriv de perspektiv som ska fördjupas:",
        value=st.session_state.get('selected_perspectives_text', ''),
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
                st.switch_page("pages/steg 3.py")
    
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
with st.expander("Tips för ett bra perspektivsamtal"):
    st.markdown("""
    För att få fram olika perspektiv:
    - Ställ öppna frågor som uppmuntrar reflektion
    - Låt alla komma till tals
    - Undvik att döma olika åsikter
    - Uppmuntra konkreta exempel
    - Dokumentera även minoritetsåsikter
    """)

# Footer
st.markdown("---")
st.caption("Steg 2 av 4")