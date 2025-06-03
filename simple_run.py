#!/usr/bin/env python3
"""
Enkel startskript för SamtalsBot utan Streamlit-konfigurationsproblem
"""

import sys
import os
import subprocess
import tempfile

def main():
    """Huvudfunktion"""
    print("🗣️  SamtalsBot - Enkel start...")
    
    # Skapa temporär config-katalog
    temp_dir = tempfile.mkdtemp()
    config_dir = os.path.join(temp_dir, '.streamlit')
    os.makedirs(config_dir, exist_ok=True)
    
    # Sätt STREAMLIT_CONFIG_DIR
    env = os.environ.copy()
    env['STREAMLIT_CONFIG_DIR'] = config_dir
    
    print("🚀 Startar SamtalsBot på http://localhost:8501")
    print("🛑 Tryck Ctrl+C för att stoppa")
    
    try:
        # Starta Streamlit med ren miljö
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "main.py",
            "--server.port", "8501",
            "--server.headless", "false"
        ], env=env)
    except KeyboardInterrupt:
        print("\n👋 SamtalsBot stängd")
    except Exception as e:
        print(f"\n❌ Fel vid start: {e}")
        print("\n💡 Alternativ: Ladda upp till Streamlit Cloud")
        print("1. Gå till https://share.streamlit.io/")
        print("2. Anslut ditt GitHub-repo")
        print("3. Välj main.py som huvudfil")

if __name__ == "__main__":
    main()