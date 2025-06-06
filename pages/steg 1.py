import streamlit as st
from utils.session_manager import get_current_session, is_step_accessible
from utils.ai_helper import get_ai_suggestion_steg1
from utils.database import update_session_step1
from utils.audio_text_input import audio_text_input

# Konfigurera sida
st.set_page_config(
    page_title="Steg 1 - Problembeskrivning",
    page_icon=None,
    layout="wide"
)

# Kontrollera åtkomst
if not is_step_accessible(1):
    st.error("Du har inte åtkomst till detta steg ännu.")
    st.stop()

current_session = get_current_session()
if not current_session:
    st.error("Inget aktivt samtal. Gå tillbaka till startsidan.")
    if st.button("← Tillbaka till start"):
        st.switch_page("main.py")
    st.stop()

# Header
st.title("Steg 1: Problembeskrivning")
st.markdown(f"Samtal: {current_session['session_name']} | Samtalsledare: {current_session['rektor_name']}")

# === NYTT: Gemensam komponent för ljud/text ===
transcript, audio_path = audio_text_input(1, current_session['id'], key_prefix="steg1")
if transcript:
    st.session_state.transcript_steg1 = transcript
    if audio_path:
        st.session_state.audio_path_steg1 = audio_path
# === SLUT NYTT ===

# Navigation
col1, col2 = st.columns([1, 4])
with col1:
    if st.button("← Tillbaka"):
        st.switch_page("main.py")

st.markdown("---")

# Visa befintlig data om den finns
if current_session['steg1_approved']:
    st.success("✅ Steg 1 är redan slutfört!")
    
    st.subheader("Godkänd problembeskrivning:")
    st.write(current_session['problem_beskrivning'])
    
    if current_session['steg1_ai_response']:
        st.subheader("AI-förslag som godkändes:")
        st.markdown(current_session['steg1_ai_response'])
    
    col1, col2 = st.columns(2)
    with col1:
        if st.button("📝 Redigera detta steg"):
            # Tillåt redigering genom att sätta approved till False temporärt
            st.session_state.edit_steg1 = True
            st.rerun()
    
    with col2:
        if st.button("➡️ Gå till Steg 2"):
            st.switch_page("pages/steg 2.py")
    
    # Om inte i redigeringsläge, stoppa här
    if not st.session_state.get('edit_steg1', False):
        st.stop()

# Formulär för problembeskrivning och uppladdning
st.subheader("Beskriv problemet eller frågan")
st.markdown("""
Börja med att tydligt beskriva det problem eller den fråga som du vill diskutera med din personalgrupp. 
Du kan ladda upp eller klistra in samtal högst upp på sidan om du vill använda en transkribering.
""")

with st.form("problem_form"):
    st.markdown("---")
    # Ta bort uppladdning av ljudfil och textfil här!
    # Problem beskrivning
    problem_beskrivning = st.text_area(
        "Problembeskrivning * (eller lämna tomt och ladda upp transkribering högst upp)",
        value=transcript if transcript else current_session.get('problem_beskrivning', ''),
        height=150,
        help="Beskriv tydligt det problem eller den fråga som ska diskuteras eller ladda upp en transkribering högst upp på sidan",
        placeholder="Exempel: Vi behöver diskutera hur vi kan förbättra elevernas digitala kompetens..."
    )
    # Personalgrupp
    personal_grupp = st.selectbox(
        "Vilken personalgrupp ska delta? *",
        options=["Lärare", "EHT-personal", "Blandad grupp (lärare + EHT)", "Ledningsgrupp", "Hela personalstyrkan", "Annat"],
        index=0 if not current_session.get('personal_grupp') else 
              ["Lärare", "EHT-personal", "Blandad grupp (lärare + EHT)", "Ledningsgrupp", "Hela personalstyrkan", "Annat"].index(current_session.get('personal_grupp', 'Lärare'))
    )
    # Ytterligare kontext
    kontext = st.text_area(
        "Ytterligare kontext (valfritt)",
        value=current_session.get('kontext', ''),
        height=100,
        help="Lägg till relevant bakgrundsinformation som kan hjälpa till att ge bättre förslag",
        placeholder="Exempel: Detta är en uppföljning av tidigare diskussioner om... Vi har tidigare provat... Utmaningen är att..."
    )
    # Submit knapp
    submit_button = st.form_submit_button("Få förslag", type="primary")

# Hantera formulärinlämning
if submit_button:
    pb = (problem_beskrivning or "").strip()
    # Om ljudfil är uppladdad, transkribera den nu
    uploaded_audio = st.session_state.get('audio_upload_steg1_form')
    if uploaded_audio:
        from utils.audio_handler import transcribe_uploaded_file, validate_audio_file
        is_valid, message = validate_audio_file(uploaded_audio)
        if is_valid:
            with st.spinner("Transkriberar ljudfil... Detta kan ta några minuter."):
                transcript, audio_path = transcribe_uploaded_file(
                    uploaded_audio, current_session['id'], 1
                )
                if transcript:
                    pb = transcript.strip()
                    st.session_state.transcript_steg1 = pb
                else:
                    st.error("Kunde inte transkribera filen. Kontrollera att det är en giltig ljudfil.")
                    st.stop()
        else:
            st.error(f"❌ {message}")
            st.stop()
    # Om problembeskrivning är tom, men transkribering finns, använd transkriberingen
    if not pb:
        pb = st.session_state.get('transcript_steg1', '').strip()
    if not pb:
        st.error("Du måste antingen beskriva problemet eller ladda upp en transkribering innan du kan få AI-förslag.")
    else:
        st.session_state.current_problem = pb
        st.session_state.current_personal_grupp = personal_grupp
        st.session_state.current_kontext = kontext
        with st.spinner("AI analyserar ditt problem och skapar förslag..."):
            ai_suggestion = get_ai_suggestion_steg1(pb, personal_grupp, kontext)
            if ai_suggestion:
                st.session_state.ai_suggestion_steg1 = ai_suggestion
                st.rerun()
            else:
                st.error("Kunde inte hämta AI-förslag. Kontrollera din internetanslutning och API-nyckel.")

# Visa AI-förslag om de finns
if 'ai_suggestion_steg1' in st.session_state:
    st.markdown("---")
    st.subheader("Förslag för presentation")
    with st.expander("Visa input som användes"):
        st.write(f"Problem: {st.session_state.current_problem}")
        st.write(f"Personalgrupp: {st.session_state.current_personal_grupp}")
        if st.session_state.current_kontext:
            st.write(f"Kontext: {st.session_state.current_kontext}")
    st.markdown(st.session_state.ai_suggestion_steg1)
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if st.button("✅ Godkänn och fortsätt till Steg 2", type="primary"):
            # Spara i databas
            update_session_step1(
                current_session['id'],
                st.session_state.current_problem,
                st.session_state.current_personal_grupp,
                st.session_state.current_kontext,
                st.session_state.ai_suggestion_steg1,
                approved=True
            )
            
            # Rensa session state
            for key in ['ai_suggestion_steg1', 'current_problem', 'current_personal_grupp', 'current_kontext', 'edit_steg1']:
                if key in st.session_state:
                    del st.session_state[key]
            
            st.success("Steg 1 godkänt! Går till Steg 2...")
            st.switch_page("pages/steg 2.py")
    
    with col2:
        if st.button("🔄 Revidera förslag"):
            # Ta bort AI-förslag så användaren kan ändra input
            del st.session_state.ai_suggestion_steg1
            st.rerun()
    
    with col3:
        if st.button("💾 Spara utkast"):
            # Spara utan att godkänna
            update_session_step1(
                current_session['id'],
                st.session_state.current_problem,
                st.session_state.current_personal_grupp,
                st.session_state.current_kontext,
                st.session_state.ai_suggestion_steg1,
                approved=False
            )
            st.success("Utkast sparat!")

# Hjälptext
st.markdown("---")
with st.expander("Tips för en bra problembeskrivning"):
    st.markdown("""
    En bra problembeskrivning innehåller:
    - Tydlig formulering av vad som ska diskuteras
    - Bakgrund till varför detta är viktigt nu
    - Konkreta exempel om möjligt
    - Önskad utkomst av diskussionen
    Exempel på bra problembeskrivningar:
    "Vi behöver diskutera hur vi kan förbättra elevernas digitala kompetens. Många lärare känner sig osäkra på hur de ska integrera digitala verktyg i undervisningen på ett meningsfullt sätt. Vi vill komma fram till konkreta åtgärder för kompetensutveckling."
    "Flera föräldrar har uttryckt oro över elevernas stress och arbetsbörda. Vi behöver diskutera hur vi kan skapa en mer hållbar lärmiljö utan att sänka våra akademiska krav."
    """)

# Footer
st.markdown("---")
st.caption("Steg 1 av 4")