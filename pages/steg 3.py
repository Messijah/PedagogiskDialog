import streamlit as st
import json
from utils.session_manager import get_current_session, is_step_accessible
from utils.ai_helper import analyze_discussion_steg3
from utils.database import update_session_step3
from utils.audio_handler import transcribe_uploaded_file, validate_audio_file, save_recorded_audio, transcribe_audio_openai
from utils.audio_text_input import audio_text_input

# Konfigurera sida
st.set_page_config(
    page_title="Steg 3 - Fördjupad diskussion",
    page_icon=None,
    layout="wide"
)

# Kontrollera åtkomst
if not is_step_accessible(3):
    st.error("Du måste först slutföra Steg 2 innan du kan komma åt Steg 3.")
    if st.button("← Gå till Steg 2"):
        st.switch_page("pages/steg 2.py")
    st.stop()

current_session = get_current_session()
if not current_session:
    st.error("Inget aktivt samtal. Gå tillbaka till startsidan.")
    if st.button("← Tillbaka till start"):
        st.switch_page("Start.py")
    st.stop()

# Header
st.title("Steg 3: Fördjupad diskussion")
st.markdown(f"Samtal: {current_session['session_name']} | Samtalsledare: {current_session['rektor_name']}")

# Navigation
col1, col2, col3 = st.columns([1, 1, 3])
with col1:
    if st.button("← Steg 2"):
        st.switch_page("pages/steg 2.py")
with col2:
    if st.button("🏠 Start"):
        st.switch_page("Start.py")

st.markdown("---")

# Visa kontext från tidigare steg
st.subheader("📋 Kontext från tidigare steg")

col1, col2 = st.columns(2)
with col1:
    st.markdown("**Problemformulering:**")
    st.info(current_session['problem_beskrivning'])

with col2:
    st.markdown("**Valda perspektiv från Steg 2:**")
    selected_perspectives = current_session.get('steg2_selected_perspectives', '')
    if selected_perspectives:
        st.info(selected_perspectives)
    else:
        st.warning("Inga perspektiv valda från Steg 2")

# Visa befintlig data om den finns
if current_session['steg3_approved']:
    st.success("✅ Steg 3 är redan slutfört!")
    
    if current_session['steg3_transcript']:
        st.subheader("Transkribering av fördjupad diskussion:")
        with st.expander("Visa transkribering"):
            st.write(current_session['steg3_transcript'])
    
    if current_session['steg3_ai_analysis']:
        st.subheader("AI-analys som godkändes:")
        st.markdown(current_session['steg3_ai_analysis'])
    
    if current_session['steg3_conclusions']:
        st.subheader("Slutsatser:")
        st.markdown(current_session['steg3_conclusions'])
    
    col1, col2, col3 = st.columns(3)
    with col1:
        if st.button("📝 Redigera detta steg"):
            st.session_state.edit_steg3 = True
            st.rerun()
    
    with col2:
        if st.button("← Tillbaka till Steg 2"):
            st.switch_page("pages/steg 2.py")
    
    with col3:
        if st.button("➡️ Gå till Steg 4"):
            st.switch_page("pages/steg 4.py")
    
    # Om inte i redigeringsläge, stoppa här
    if not st.session_state.get('edit_steg3', False):
        st.stop()

# Instruktioner
st.subheader("Instruktioner för Steg 3")
st.markdown("""
Genomför en fördjupad diskussion med fokus på de perspektiv som valdes i Steg 2.
Så här gör du:
1. Presentera de valda perspektiven för gruppen
2. Fördjupa diskussionen kring dessa områden
3. Spela in samtalet eller ladda upp en ljudfil
4. Analysera och dra slutsatser från diskussionen
5. Godkänn slutsatserna som grund för handlingsplanen
""")

# Visa förslag på diskussionsfrågor baserat på valda perspektiv
if selected_perspectives:
    with st.expander("💡 Förslag på diskussionsfrågor för fördjupning"):
        st.markdown(f"""
        **Baserat på era valda perspektiv kan ni diskutera:**
        
        - Vad är det viktigaste att komma ihåg när vi arbetar med dessa frågor?
        - Vilka konkreta åtgärder skulle kunna hjälpa oss framåt?
        - Vad behöver vi prioritera först?
        - Vilka resurser eller stöd behöver vi för att lyckas?
        - Hur kan vi mäta om vi gör framsteg?
        - Vilka hinder måste vi överkomma?
        - Vem bör ansvara för vad?
        
        **Era valda perspektiv att fördjupa:**
        {selected_perspectives}
        """)

# === NYTT: Gemensam komponent för ljud/text ===
transcript, audio_path = audio_text_input(3, current_session['id'], key_prefix="steg3")
if transcript:
    st.session_state.transcript_steg3 = transcript
    if audio_path:
        st.session_state.audio_path_steg3 = audio_path
# === SLUT NYTT ===

# Visa transkribering om den finns
if 'transcript_steg3' in st.session_state or current_session.get('steg3_transcript'):
    transcript = st.session_state.get('transcript_steg3', current_session.get('steg3_transcript'))
    
    st.markdown("---")
    st.subheader("📝 Transkribering av fördjupad diskussion")
    
    # Visa transkribering i redigerbar textområde
    edited_transcript = st.text_area(
        "Granska och redigera transkriberingen om nödvändigt:",
        value=transcript,
        height=300,
        help="Du kan redigera transkriberingen för att korrigera eventuella fel",
        key="edit_transcript_steg3"
    )
    
    # Uppdatera transcript om den redigerats
    if edited_transcript != transcript:
        st.session_state.transcript_steg3 = edited_transcript
    
    # Analysera diskussion
    if st.button("🤖 Analysera diskussion och dra slutsatser", type="primary"):
        with st.spinner("AI analyserar den fördjupade diskussionen och drar slutsatser..."):
            analysis = analyze_discussion_steg3(
                current_session['problem_beskrivning'],
                selected_perspectives,
                edited_transcript
            )
            
            if analysis:
                st.session_state.analysis_steg3 = analysis
                st.rerun()
            else:
                st.error("Kunde inte analysera diskussionen. Försök igen.")

# Visa AI-analys om den finns
if 'analysis_steg3' in st.session_state or current_session.get('steg3_ai_analysis'):
    analysis = st.session_state.get('analysis_steg3', current_session.get('steg3_ai_analysis'))
    
    st.markdown("---")
    st.subheader("Analys och slutsatser")
    st.markdown(analysis)
    
    # Möjlighet att redigera slutsatser
    st.markdown("---")
    st.subheader("Granska och komplettera slutsatserna")
    st.markdown("Du kan redigera eller komplettera slutsatserna innan du går vidare till handlingsplanen:")
    
    final_conclusions = st.text_area(
        "Slutgiltiga slutsatser för handlingsplan:",
        value=analysis,
        height=200,
        help="Redigera eller komplettera slutsatserna som ska ligga till grund för handlingsplanen"
    )
    
    # Kontrollknappar
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if st.button("✅ Godkänn slutsatser och fortsätt till Steg 4", type="primary"):
            if not final_conclusions.strip():
                st.error("Du måste ha slutsatser innan du kan fortsätta.")
            else:
                # Spara i databas
                transcript_to_save = st.session_state.get('transcript_steg3', current_session.get('steg3_transcript'))
                audio_path_to_save = st.session_state.get('audio_path_steg3', current_session.get('steg3_audio_path'))
                
                update_session_step3(
                    current_session['id'],
                    audio_path_to_save,
                    transcript_to_save,
                    analysis,
                    final_conclusions,
                    approved=True
                )
                
                # Rensa session state
                for key in ['transcript_steg3', 'analysis_steg3', 'audio_path_steg3', 'edit_steg3']:
                    if key in st.session_state:
                        del st.session_state[key]
                
                st.success("Steg 3 godkänt! Går till Steg 4...")
                st.switch_page("pages/steg 4.py")
    
    with col2:
        if st.button("🔄 Analysera om"):
            # Ta bort analys så användaren kan köra om
            if 'analysis_steg3' in st.session_state:
                del st.session_state.analysis_steg3
            st.rerun()
    
    with col3:
        if st.button("💾 Spara utkast"):
            # Spara utan att godkänna
            transcript_to_save = st.session_state.get('transcript_steg3', current_session.get('steg3_transcript'))
            audio_path_to_save = st.session_state.get('audio_path_steg3', current_session.get('steg3_audio_path'))
            
            update_session_step3(
                current_session['id'],
                audio_path_to_save,
                transcript_to_save,
                analysis,
                final_conclusions if final_conclusions.strip() else None,
                approved=False
            )
            st.success("Utkast sparat!")

# Hjälptext
st.markdown("---")
with st.expander("Tips för fördjupad diskussion"):
    st.markdown("""
    Förslag på diskussionsfrågor:
    - Vad är det viktigaste att komma ihåg när vi arbetar med dessa frågor?
    - Vilka konkreta åtgärder skulle kunna hjälpa oss framåt?
    - Vad behöver vi prioritera först?
    - Vilka resurser eller stöd behöver vi för att lyckas?
    - Hur kan vi mäta om vi gör framsteg?
    - Vilka hinder måste vi överkomma?
    - Vem bör ansvara för vad?
    """)

# Footer
st.markdown("---")
st.caption("Steg 3 av 4")