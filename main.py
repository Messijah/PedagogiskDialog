import streamlit as st
import os
from utils.session_manager import init_session, get_current_session, get_session_progress, clear_session, is_step_accessible
from utils.database import get_all_sessions, delete_session
from utils.ai_helper import validate_api_key

# Konfigurera Streamlit
st.set_page_config(
    page_title="SamtalsBot - AI-stödd Samtalsmodell",
    page_icon="🗣️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialisera session
init_session()

# Sidebar för session management
with st.sidebar:
    st.title("🗣️ SamtalsBot")
    st.markdown("*AI-stödd samtalsmodell för rektorer*")
    
    # API Key kontroll
    if not validate_api_key():
        st.error("⚠️ OpenAI API-nyckel saknas!")
        st.markdown("""
        För att använda SamtalsBot behöver du:
        1. Skapa en `.env` fil
        2. Lägg till: `OPENAI_API_KEY=din_nyckel_här`
        3. Starta om applikationen
        """)
        st.stop()
    
    st.divider()
    
    # Aktuell session info
    current_session = get_current_session()
    if current_session:
        st.subheader("Aktuell Session")
        st.write(f"**{current_session['session_name']}**")
        st.write(f"Rektor: {current_session['rektor_name']}")
        
        # Progress
        progress = get_session_progress()
        st.progress(progress)
        st.caption(f"Framsteg: {int(progress * 100)}%")
        
        if st.button("🗑️ Avsluta session", type="secondary"):
            clear_session()
            st.rerun()
    else:
        st.info("Ingen aktiv session. Skapa en ny nedan.")
    
    st.divider()
    
    # Session management
    st.subheader("Sessioner")
    
    # Skapa ny session
    with st.expander("➕ Skapa ny session"):
        with st.form("new_session"):
            session_name = st.text_input("Sessionens namn", placeholder="t.ex. Digitalisering 2024")
            rektor_name = st.text_input("Ditt namn", placeholder="Förnamn Efternamn")
            
            if st.form_submit_button("Skapa session"):
                if session_name and rektor_name:
                    from utils.session_manager import create_new_session
                    session_id = create_new_session(session_name, rektor_name)
                    st.success(f"Session '{session_name}' skapad!")
                    st.rerun()
                else:
                    st.error("Fyll i både sessionens namn och ditt namn")
    
    # Lista befintliga sessioner
    sessions = get_all_sessions()
    if sessions:
        st.write("**Befintliga sessioner:**")
        for session in sessions[:5]:  # Visa max 5 senaste
            col1, col2 = st.columns([3, 1])
            with col1:
                status_icon = "✅" if session['completed'] else f"🔄 {session['current_step']}/4"
                if st.button(f"{status_icon} {session['session_name']}", key=f"load_{session['id']}"):
                    from utils.session_manager import load_session
                    if load_session(session['id']):
                        st.success(f"Laddade session: {session['session_name']}")
                        st.rerun()
            with col2:
                if st.button("🗑️", key=f"delete_{session['id']}", help="Ta bort"):
                    delete_session(session['id'])
                    st.rerun()

# Huvudinnehåll
st.title("🗣️ SamtalsBot")
st.subheader("AI-stödd samtalsmodell för rektorer")

# Kontrollera om vi har en aktiv session
if not current_session:
    st.info("👈 Skapa eller välj en session i sidopanelen för att komma igång.")
    
    # Visa information om systemet
    st.markdown("""
    ## Välkommen till SamtalsBot!
    
    SamtalsBot hjälper dig som rektor att leda strukturerade samtal med din personal genom en 4-stegs process:
    
    ### 🎯 Steg 1: Problembeskrivning
    - Definiera problemet eller frågan som ska diskuteras
    - Få AI-förslag på hur du bäst presenterar det för gruppen
    
    ### 👥 Steg 2: Perspektivinventering  
    - Spela in gruppsamtalet där olika perspektiv framkommer
    - AI analyserar och kategoriserar de olika synvinklarna
    
    ### 🔍 Steg 3: Fördjupad diskussion
    - Fördjupa diskussionen kring utvalda perspektiv
    - AI hjälper till att dra slutsatser och identifiera konsensus
    
    ### 📋 Steg 4: Handlingsplan
    - Skapa en strukturerad handlingsplan baserat på diskussionen
    - Exportera färdig plan med ansvar, tidsramar och uppföljning
    
    **Kom igång genom att skapa en ny session i sidopanelen!**
    """)
    
    st.stop()

# Navigation för stegen
st.markdown("---")

# Progress bar
progress = get_session_progress()
st.progress(progress, text=f"Framsteg: {int(progress * 100)}% ({int(progress * 4)}/4 steg slutförda)")

# Steg-navigation
col1, col2, col3, col4 = st.columns(4)

with col1:
    accessible = is_step_accessible(1)
    if accessible:
        if st.button("🎯 Steg 1: Problem", type="primary" if current_session['current_step'] == 1 else "secondary", use_container_width=True):
            st.switch_page("pages/steg1.py")
    else:
        st.button("🎯 Steg 1: Problem", disabled=True, use_container_width=True)
    
    if current_session['steg1_approved']:
        st.success("✅ Slutfört")

with col2:
    accessible = is_step_accessible(2)
    if accessible:
        if st.button("👥 Steg 2: Perspektiv", type="primary" if current_session['current_step'] == 2 else "secondary", use_container_width=True):
            st.switch_page("pages/steg2.py")
    else:
        st.button("👥 Steg 2: Perspektiv", disabled=True, use_container_width=True)
    
    if current_session['steg2_approved']:
        st.success("✅ Slutfört")

with col3:
    accessible = is_step_accessible(3)
    if accessible:
        if st.button("🔍 Steg 3: Fördjupning", type="primary" if current_session['current_step'] == 3 else "secondary", use_container_width=True):
            st.switch_page("pages/steg3.py")
    else:
        st.button("🔍 Steg 3: Fördjupning", disabled=True, use_container_width=True)
    
    if current_session['steg3_approved']:
        st.success("✅ Slutfört")

with col4:
    accessible = is_step_accessible(4)
    if accessible:
        if st.button("📋 Steg 4: Handlingsplan", type="primary" if current_session['current_step'] == 4 else "secondary", use_container_width=True):
            st.switch_page("pages/steg4.py")
    else:
        st.button("📋 Steg 4: Handlingsplan", disabled=True, use_container_width=True)
    
    if current_session['steg4_approved']:
        st.success("✅ Slutfört")

# Visa aktuell session information
st.markdown("---")
st.subheader("Aktuell Session")

col1, col2 = st.columns(2)
with col1:
    st.write(f"**Session:** {current_session['session_name']}")
    st.write(f"**Rektor:** {current_session['rektor_name']}")
    st.write(f"**Skapad:** {current_session['created_at'][:10]}")

with col2:
    st.write(f"**Aktuellt steg:** {current_session['current_step']}/4")
    st.write(f"**Status:** {'Slutförd' if current_session['completed'] else 'Pågående'}")

# Visa problem om det finns
if current_session['problem_beskrivning']:
    st.markdown("### Problemformulering")
    st.write(current_session['problem_beskrivning'])

# Footer
st.markdown("---")
st.caption("SamtalsBot - AI-stödd samtalsmodell för rektorer | Utvecklad för svenska skolor")
