import streamlit as st
from utils.session_manager import get_current_session, is_step_accessible
from utils.ai_helper import get_ai_suggestion_steg1
from utils.database import update_session_step1

# Konfigurera sida
st.set_page_config(
    page_title="Steg 1 - Problembeskrivning",
    page_icon="🎯",
    layout="wide"
)

# Kontrollera åtkomst
if not is_step_accessible(1):
    st.error("Du har inte åtkomst till detta steg ännu.")
    st.stop()

current_session = get_current_session()
if not current_session:
    st.error("Ingen aktiv session. Gå tillbaka till startsidan.")
    if st.button("← Tillbaka till start"):
        st.switch_page("main.py")
    st.stop()

# Header
st.title("🎯 Steg 1: Problembeskrivning och Presentation")
st.markdown(f"**Session:** {current_session['session_name']} | **Rektor:** {current_session['rektor_name']}")

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
            st.switch_page("pages/steg2.py")
    
    # Om inte i redigeringsläge, stoppa här
    if not st.session_state.get('edit_steg1', False):
        st.stop()

# Formulär för problembeskrivning
st.subheader("Beskriv problemet eller frågan")
st.markdown("""
Börja med att tydligt beskriva det problem eller den fråga som du vill diskutera med din personalgrupp. 
AI:n kommer sedan att hjälpa dig att strukturera hur du bäst presenterar detta för gruppen.
""")

with st.form("problem_form"):
    # Problem beskrivning
    problem_beskrivning = st.text_area(
        "Problembeskrivning *",
        value=current_session.get('problem_beskrivning', ''),
        height=150,
        help="Beskriv tydligt det problem eller den fråga som ska diskuteras",
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
        help="Lägg till relevant bakgrundsinformation som kan hjälpa AI:n att ge bättre förslag",
        placeholder="Exempel: Detta är en uppföljning av tidigare diskussioner om... Vi har tidigare provat... Utmaningen är att..."
    )
    
    # Submit knapp
    submit_button = st.form_submit_button("🤖 Få AI-förslag", type="primary")

# Hantera formulärinlämning
if submit_button:
    if not problem_beskrivning.strip():
        st.error("Du måste beskriva problemet innan du kan få AI-förslag.")
    else:
        # Spara input i session state
        st.session_state.current_problem = problem_beskrivning
        st.session_state.current_personal_grupp = personal_grupp
        st.session_state.current_kontext = kontext
        
        # Hämta AI-förslag
        with st.spinner("AI analyserar ditt problem och skapar förslag..."):
            ai_suggestion = get_ai_suggestion_steg1(problem_beskrivning, personal_grupp, kontext)
            
            if ai_suggestion:
                st.session_state.ai_suggestion_steg1 = ai_suggestion
                st.rerun()
            else:
                st.error("Kunde inte hämta AI-förslag. Kontrollera din internetanslutning och API-nyckel.")

# Visa AI-förslag om de finns
if 'ai_suggestion_steg1' in st.session_state:
    st.markdown("---")
    st.subheader("🤖 AI-förslag för presentation")
    
    # Visa input som användes
    with st.expander("Visa input som användes"):
        st.write(f"**Problem:** {st.session_state.current_problem}")
        st.write(f"**Personalgrupp:** {st.session_state.current_personal_grupp}")
        if st.session_state.current_kontext:
            st.write(f"**Kontext:** {st.session_state.current_kontext}")
    
    # Visa AI-förslag
    st.markdown(st.session_state.ai_suggestion_steg1)
    
    # Kontrollknappar
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
            st.switch_page("pages/steg2.py")
    
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
with st.expander("💡 Tips för en bra problembeskrivning"):
    st.markdown("""
    **En bra problembeskrivning innehåller:**
    
    - **Tydlig formulering** av vad som ska diskuteras
    - **Bakgrund** till varför detta är viktigt nu
    - **Konkreta exempel** om möjligt
    - **Önskad utkomst** av diskussionen
    
    **Exempel på bra problembeskrivningar:**
    
    *"Vi behöver diskutera hur vi kan förbättra elevernas digitala kompetens. Många lärare känner sig osäkra på hur de ska integrera digitala verktyg i undervisningen på ett meningsfullt sätt. Vi vill komma fram till konkreta åtgärder för kompetensutveckling."*
    
    *"Flera föräldrar har uttryckt oro över elevernas stress och arbetsbörda. Vi behöver diskutera hur vi kan skapa en mer hållbar lärmiljö utan att sänka våra akademiska krav."*
    """)

# Footer
st.markdown("---")
st.caption("Steg 1 av 4 | SamtalsBot - AI-stödd samtalsmodell för rektorer")