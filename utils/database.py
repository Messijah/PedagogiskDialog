import sqlite3
import os
from datetime import datetime
import json

def get_connection():
    """Skapa anslutning till SQLite databas"""
    # Skapa data mapp om den inte finns
    if not os.path.exists('data'):
        os.makedirs('data')
    
    return sqlite3.connect('data/sessions.db')

def create_tables():
    """Skapa databastabeller om de inte finns"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sessions (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            session_name TEXT,
            rektor_name TEXT,
            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
            
            -- Steg 1
            problem_beskrivning TEXT,
            personal_grupp TEXT,
            kontext TEXT,
            steg1_ai_response TEXT,
            steg1_approved BOOLEAN DEFAULT FALSE,
            steg1_completed_at TIMESTAMP,
            
            -- Steg 2
            steg2_audio_path TEXT,
            steg2_transcript TEXT,
            steg2_ai_analysis TEXT,
            steg2_selected_perspectives TEXT,
            steg2_approved BOOLEAN DEFAULT FALSE,
            steg2_completed_at TIMESTAMP,
            
            -- Steg 3
            steg3_audio_path TEXT,
            steg3_transcript TEXT,
            steg3_ai_analysis TEXT,
            steg3_conclusions TEXT,
            steg3_approved BOOLEAN DEFAULT FALSE,
            steg3_completed_at TIMESTAMP,
            
            -- Steg 4
            steg4_handlingsplan TEXT,
            steg4_approved BOOLEAN DEFAULT FALSE,
            steg4_completed_at TIMESTAMP,
            
            -- Status
            current_step INTEGER DEFAULT 1,
            completed BOOLEAN DEFAULT FALSE
        )
    ''')
    
    conn.commit()
    conn.close()

def create_session(session_name, rektor_name):
    """Skapa ny session"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        INSERT INTO sessions (session_name, rektor_name)
        VALUES (?, ?)
    ''', (session_name, rektor_name))
    
    session_id = cursor.lastrowid
    conn.commit()
    conn.close()
    
    return session_id

def get_session(session_id):
    """Hämta session data"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('SELECT * FROM sessions WHERE id = ?', (session_id,))
    row = cursor.fetchone()
    conn.close()
    
    if row:
        columns = [description[0] for description in cursor.description]
        return dict(zip(columns, row))
    return None

def update_session_step1(session_id, problem_beskrivning, personal_grupp, kontext, ai_response, approved=False):
    """Uppdatera Steg 1 data"""
    conn = get_connection()
    cursor = conn.cursor()
    
    completed_at = datetime.now() if approved else None
    current_step = 2 if approved else 1
    
    cursor.execute('''
        UPDATE sessions 
        SET problem_beskrivning = ?, personal_grupp = ?, kontext = ?, 
            steg1_ai_response = ?, steg1_approved = ?, steg1_completed_at = ?,
            current_step = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (problem_beskrivning, personal_grupp, kontext, ai_response, 
          approved, completed_at, current_step, session_id))
    
    conn.commit()
    conn.close()

def update_session_step2(session_id, audio_path, transcript, ai_analysis, selected_perspectives, approved=False):
    """Uppdatera Steg 2 data"""
    conn = get_connection()
    cursor = conn.cursor()
    
    completed_at = datetime.now() if approved else None
    current_step = 3 if approved else 2
    perspectives_json = json.dumps(selected_perspectives) if selected_perspectives else None
    
    cursor.execute('''
        UPDATE sessions 
        SET steg2_audio_path = ?, steg2_transcript = ?, steg2_ai_analysis = ?,
            steg2_selected_perspectives = ?, steg2_approved = ?, steg2_completed_at = ?,
            current_step = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (audio_path, transcript, ai_analysis, perspectives_json,
          approved, completed_at, current_step, session_id))
    
    conn.commit()
    conn.close()

def update_session_step3(session_id, audio_path, transcript, ai_analysis, conclusions, approved=False):
    """Uppdatera Steg 3 data"""
    conn = get_connection()
    cursor = conn.cursor()
    
    completed_at = datetime.now() if approved else None
    current_step = 4 if approved else 3
    
    cursor.execute('''
        UPDATE sessions 
        SET steg3_audio_path = ?, steg3_transcript = ?, steg3_ai_analysis = ?,
            steg3_conclusions = ?, steg3_approved = ?, steg3_completed_at = ?,
            current_step = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (audio_path, transcript, ai_analysis, conclusions,
          approved, completed_at, current_step, session_id))
    
    conn.commit()
    conn.close()

def update_session_step4(session_id, handlingsplan, approved=False):
    """Uppdatera Steg 4 data"""
    conn = get_connection()
    cursor = conn.cursor()
    
    completed_at = datetime.now() if approved else None
    completed = approved
    
    cursor.execute('''
        UPDATE sessions 
        SET steg4_handlingsplan = ?, steg4_approved = ?, steg4_completed_at = ?,
            completed = ?, updated_at = CURRENT_TIMESTAMP
        WHERE id = ?
    ''', (handlingsplan, approved, completed_at, completed, session_id))
    
    conn.commit()
    conn.close()

def get_all_sessions():
    """Hämta alla sessioner"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('''
        SELECT id, session_name, rektor_name, created_at, current_step, completed
        FROM sessions 
        ORDER BY created_at DESC
    ''')
    
    rows = cursor.fetchall()
    conn.close()
    
    columns = ['id', 'session_name', 'rektor_name', 'created_at', 'current_step', 'completed']
    return [dict(zip(columns, row)) for row in rows]

def delete_session(session_id):
    """Ta bort session"""
    conn = get_connection()
    cursor = conn.cursor()
    
    cursor.execute('DELETE FROM sessions WHERE id = ?', (session_id,))
    conn.commit()
    conn.close()