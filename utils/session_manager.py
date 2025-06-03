import streamlit as st
from utils.database import create_tables, get_session, create_session

def init_session():
    """Initialisera session state"""
    create_tables()
    
    # Initialisera session state variabler
    if 'session_id' not in st.session_state:
        st.session_state.session_id = None
    
    if 'current_step' not in st.session_state:
        st.session_state.current_step = 1
    
    if 'session_data' not in st.session_state:
        st.session_state.session_data = None

def create_new_session(session_name, rektor_name):
    """Skapa ny session och sätt som aktiv"""
    session_id = create_session(session_name, rektor_name)
    st.session_state.session_id = session_id
    st.session_state.current_step = 1
    st.session_state.session_data = get_session(session_id)
    return session_id

def load_session(session_id):
    """Ladda befintlig session"""
    session_data = get_session(session_id)
    if session_data:
        st.session_state.session_id = session_id
        st.session_state.current_step = session_data['current_step']
        st.session_state.session_data = session_data
        return True
    return False

def get_current_session():
    """Hämta aktuell session data"""
    if st.session_state.session_id:
        # Uppdatera session data från databas
        st.session_state.session_data = get_session(st.session_state.session_id)
        return st.session_state.session_data
    return None

def get_current_step():
    """Hämta aktuellt steg"""
    session_data = get_current_session()
    if session_data:
        return session_data['current_step']
    return 1

def is_step_completed(step_number):
    """Kontrollera om ett steg är slutfört"""
    session_data = get_current_session()
    if not session_data:
        return False
    
    step_mapping = {
        1: 'steg1_approved',
        2: 'steg2_approved', 
        3: 'steg3_approved',
        4: 'steg4_approved'
    }
    
    field = step_mapping.get(step_number)
    return session_data.get(field, False) if field else False

def is_step_accessible(step_number):
    """Kontrollera om ett steg är tillgängligt"""
    if step_number == 1:
        return True
    
    # Steg är tillgängligt om föregående steg är slutfört
    return is_step_completed(step_number - 1)

def get_session_progress():
    """Hämta progress för aktuell session"""
    session_data = get_current_session()
    if not session_data:
        return 0
    
    completed_steps = 0
    for i in range(1, 5):
        if is_step_completed(i):
            completed_steps += 1
    
    return completed_steps / 4

def clear_session():
    """Rensa session state"""
    st.session_state.session_id = None
    st.session_state.current_step = 1
    st.session_state.session_data = None
    
    # Rensa eventuella cached AI responses
    for key in list(st.session_state.keys()):
        if key.startswith('ai_') or key.startswith('transcript_'):
            del st.session_state[key]

def update_current_step(step_number):
    """Uppdatera aktuellt steg"""
    st.session_state.current_step = step_number