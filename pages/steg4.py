import streamlit as st
from datetime import datetime
from utils.session_manager import get_current_session, is_step_accessible
from utils.ai_helper import create_action_plan_steg4
from utils.database import update_session_step4
import io

# Konfigurera sida
st.set_page_config(
    page_title="Steg 4 - Handlingsplan",
    page_icon="📋",
    layout="wide"
)

# Kontrollera åtkomst
if not is_step_accessible(4):
    st.error("Du måste först slutföra Steg 3 innan du kan komma åt Steg 4.")
    if st.button("← Gå till Steg 3"):
        st.switch_page("pages/steg3.py")
    st.stop()

current_session = get_current_session()
if not current_session:
    st.error("Ingen aktiv session. Gå tillbaka till startsidan.")
    if st.button("← Tillbaka till start"):
        st.switch_page("main.py")
    st.stop()

# Header
st.title("📋 Steg 4: Handlingsplan")
st.markdown(f"**Session:** {current_session['session_name']} | **Rektor:** {current_session['rektor_name']}")

# Navigation
col1, col2, col3 = st.columns([1, 1, 3])
with col1:
    if st.button("← Steg 3"):
        st.switch_page("pages/steg3.py")
with col2:
    if st.button("🏠 Start"):
        st.switch_page("main.py")

st.markdown("---")

# Visa sammanfattning från tidigare steg
st.subheader("📋 Sammanfattning från tidigare steg")

with st.expander("Visa fullständig sammanfattning"):
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown("**Problemformulering (Steg 1):**")
        st.info(current_session['problem_beskrivning'])
        
        st.markdown("**Valda perspektiv (Steg 2):**")
        if current_session.get('steg2_selected_perspectives'):
            st.info(current_session['steg2_selected_perspectives'])
        else:
            st.warning("Inga perspektiv dokumenterade")
    
    with col2:
        st.markdown("**Slutsatser (Steg 3):**")
        if current_session.get('steg3_conclusions'):
            st.info(current_session['steg3_conclusions'])
        else:
            st.warning("Inga slutsatser dokumenterade")

# Visa befintlig handlingsplan om den finns
if current_session['steg4_approved']:
    st.success("✅ Steg 4 är slutfört! Handlingsplanen är klar.")
    
    if current_session['steg4_handlingsplan']:
        st.subheader("📋 Färdig handlingsplan:")
        st.markdown(current_session['steg4_handlingsplan'])
        
        # Export-knappar
        st.markdown("---")
        col1, col2, col3 = st.columns(3)
        
        with col1:
            # Skapa text-fil för nedladdning
            plan_text = f"""
HANDLINGSPLAN - {current_session['session_name']}
Rektor: {current_session['rektor_name']}
Datum: {datetime.now().strftime('%Y-%m-%d')}

PROBLEMFORMULERING:
{current_session['problem_beskrivning']}

VALDA PERSPEKTIV:
{current_session.get('steg2_selected_perspectives', 'Ej dokumenterat')}

SLUTSATSER:
{current_session.get('steg3_conclusions', 'Ej dokumenterat')}

HANDLINGSPLAN:
{current_session['steg4_handlingsplan']}
"""
            
            st.download_button(
                label="📄 Ladda ner som textfil",
                data=plan_text,
                file_name=f"handlingsplan_{current_session['session_name'].replace(' ', '_')}_{datetime.now().strftime('%Y%m%d')}.txt",
                mime="text/plain"
            )
        
        with col2:
            if st.button("📝 Redigera handlingsplan"):
                st.session_state.edit_steg4 = True
                st.rerun()
        
        with col3:
            if st.button("🏠 Tillbaka till start"):
                st.switch_page("main.py")
    
    # Om inte i redigeringsläge, stoppa här
    if not st.session_state.get('edit_steg4', False):
        st.stop()

# Instruktioner
st.subheader("📝 Instruktioner för Steg 4")
st.markdown("""
Nu ska vi skapa en strukturerad handlingsplan baserat på alla diskussioner och slutsatser från de tidigare stegen.

**Handlingsplanen kommer att innehålla:**
- Sammanfattning av problemet och slutsatserna
- Konkreta åtgärder med ansvariga personer
- Tidsplan och milstolpar
- Uppföljningsplan
- Resurser som behövs
""")

# Ytterligare input för handlingsplan
st.markdown("---")
st.subheader("💡 Kompletterande information för handlingsplanen")

additional_info = st.text_area(
    "Finns det ytterligare information eller önskemål för handlingsplanen?",
    height=100,
    placeholder="T.ex. specifika deadlines, budgetbegränsningar, personer som ska involveras, etc.",
    help="Denna information kommer att inkluderas när AI:n skapar handlingsplanen"
)

# Skapa handlingsplan
if st.button("🤖 Skapa handlingsplan", type="primary"):
    if not current_session.get('steg3_conclusions'):
        st.error("Inga slutsatser från Steg 3 hittades. Gå tillbaka och slutför Steg 3 först.")
    else:
        with st.spinner("AI skapar en strukturerad handlingsplan baserat på era diskussioner..."):
            handlingsplan = create_action_plan_steg4(
                current_session['problem_beskrivning'],
                current_session['steg3_conclusions'],
                additional_info
            )
            
            if handlingsplan:
                st.session_state.handlingsplan_steg4 = handlingsplan
                st.rerun()
            else:
                st.error("Kunde inte skapa handlingsplan. Försök igen.")

# Visa handlingsplan om den finns
if 'handlingsplan_steg4' in st.session_state or current_session.get('steg4_handlingsplan'):
    handlingsplan = st.session_state.get('handlingsplan_steg4', current_session.get('steg4_handlingsplan'))
    
    st.markdown("---")
    st.subheader("🤖 AI-genererad handlingsplan")
    
    # Visa handlingsplan i redigerbar form
    edited_plan = st.text_area(
        "Granska och redigera handlingsplanen:",
        value=handlingsplan,
        height=500,
        help="Du kan redigera handlingsplanen för att anpassa den efter era specifika behov"
    )
    
    # Uppdatera handlingsplan om den redigerats
    if edited_plan != handlingsplan:
        st.session_state.handlingsplan_steg4 = edited_plan
    
    # Förhandsvisning av export
    with st.expander("👀 Förhandsvisning av komplett dokument"):
        complete_document = f"""
# HANDLINGSPLAN - {current_session['session_name']}

**Rektor:** {current_session['rektor_name']}  
**Datum:** {datetime.now().strftime('%Y-%m-%d')}

## Problemformulering
{current_session['problem_beskrivning']}

## Perspektiv som diskuterades
{current_session.get('steg2_selected_perspectives', 'Ej dokumenterat')}

## Slutsatser från diskussion
{current_session.get('steg3_conclusions', 'Ej dokumenterat')}

## Handlingsplan
{edited_plan}

---
*Skapad med SamtalsBot - AI-stödd samtalsmodell för rektorer*
"""
        st.markdown(complete_document)
    
    # Kontrollknappar
    st.markdown("---")
    col1, col2, col3 = st.columns([2, 2, 1])
    
    with col1:
        if st.button("✅ Godkänn handlingsplan och slutför", type="primary"):
            # Spara i databas
            update_session_step4(
                current_session['id'],
                edited_plan,
                approved=True
            )
            
            # Rensa session state
            for key in ['handlingsplan_steg4', 'edit_steg4']:
                if key in st.session_state:
                    del st.session_state[key]
            
            st.success("🎉 Handlingsplan godkänd! Processen är nu slutförd.")
            st.balloons()
            st.rerun()
    
    with col2:
        if st.button("🔄 Skapa ny handlingsplan"):
            # Ta bort handlingsplan så användaren kan skapa en ny
            if 'handlingsplan_steg4' in st.session_state:
                del st.session_state.handlingsplan_steg4
            st.rerun()
    
    with col3:
        if st.button("💾 Spara utkast"):
            # Spara utan att godkänna
            update_session_step4(
                current_session['id'],
                edited_plan,
                approved=False
            )
            st.success("Utkast sparat!")

# Hjälptext
st.markdown("---")
with st.expander("💡 Tips för en bra handlingsplan"):
    st.markdown("""
    **En effektiv handlingsplan innehåller:**
    
    **📋 Tydliga åtgärder**
    - Specifika, mätbara aktiviteter
    - Vem som ansvarar för varje åtgärd
    - När åtgärden ska vara klar
    
    **⏰ Realistisk tidsplan**
    - Prioritering av åtgärder
    - Milstolpar och deadlines
    - Hänsyn till andra aktiviteter
    
    **📊 Uppföljning**
    - Hur framsteg ska mätas
    - När uppföljning ska ske
    - Vem som ansvarar för uppföljning
    
    **💰 Resurser**
    - Vilka resurser som behövs
    - Budget och finansiering
    - Kompetensutveckling
    
    **🚧 Riskhantering**
    - Potentiella hinder
    - Alternativa lösningar
    - Förebyggande åtgärder
    
    **Exempel på bra formuleringar:**
    - "Maria ansvarar för att genomföra fortbildning i digitala verktyg senast 15 mars"
    - "Uppföljningsmöte varje månad för att utvärdera framsteg"
    - "Budget på 50 000 kr avsätts för inköp av material"
    """)

# Slutmeddelande om processen är klar
if current_session.get('completed'):
    st.markdown("---")
    st.success("🎉 Grattis! Du har slutfört hela SamtalsBot-processen.")
    st.markdown("""
    **Du har nu:**
    - ✅ Definierat problemet tydligt
    - ✅ Samlat in olika perspektiv från din personal
    - ✅ Fördjupat diskussionen kring viktiga områden
    - ✅ Skapat en strukturerad handlingsplan
    
    **Nästa steg:**
    - Dela handlingsplanen med din personalgrupp
    - Implementera de planerade åtgärderna
    - Följ upp regelbundet enligt planen
    - Kom ihåg att dokumentera framsteg och lärdomar
    """)

# Footer
st.markdown("---")
st.caption("Steg 4 av 4 | SamtalsBot - AI-stödd samtalsmodell för rektorer")