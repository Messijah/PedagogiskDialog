#!/usr/bin/env python3
"""
Database migration script to add participants column to existing sessions table.
Run this script once to update your existing database.
"""

import sqlite3
import os

def migrate_database():
    """Add participants column to sessions table if it doesn't exist"""
    
    # Check if database exists
    db_path = 'data/sessions.db'
    if not os.path.exists(db_path):
        print("No existing database found. No migration needed.")
        return
    
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    
    try:
        # Check if participants column already exists
        cursor.execute("PRAGMA table_info(sessions)")
        columns = [column[1] for column in cursor.fetchall()]
        
        if 'participants' not in columns:
            print("Adding participants column to sessions table...")
            cursor.execute("ALTER TABLE sessions ADD COLUMN participants TEXT")
            conn.commit()
            print("✅ Migration completed successfully!")
        else:
            print("Participants column already exists. No migration needed.")
            
    except Exception as e:
        print(f"❌ Migration failed: {e}")
        conn.rollback()
    finally:
        conn.close()

if __name__ == "__main__":
    migrate_database()