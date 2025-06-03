#!/usr/bin/env python3
"""
Startskript för SamtalsBot
Kontrollerar beroenden och startar Streamlit-applikationen
"""

import sys
import os
import subprocess
from pathlib import Path

def check_python_version():
    """Kontrollera Python-version"""
    if sys.version_info < (3, 8):
        print("❌ Python 3.8 eller senare krävs")
        print(f"Du kör Python {sys.version}")
        return False
    print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} OK")
    return True

def check_env_file():
    """Kontrollera .env fil"""
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env fil saknas")
        print("Kopierar .env.example till .env...")
        try:
            import shutil
            shutil.copy(".env.example", ".env")
            print("✅ .env fil skapad")
            print("🔧 Redigera .env filen och lägg till din OpenAI API-nyckel")
            return False
        except Exception as e:
            print(f"❌ Kunde inte skapa .env fil: {e}")
            return False
    
    # Kontrollera API-nyckel
    try:
        with open(".env", "r") as f:
            content = f.read()
            if "your_openai_api_key_here" in content:
                print("⚠️  OpenAI API-nyckel inte konfigurerad i .env")
                print("🔧 Redigera .env filen och lägg till din riktiga API-nyckel")
                return False
    except Exception as e:
        print(f"❌ Kunde inte läsa .env fil: {e}")
        return False
    
    print("✅ .env fil OK")
    return True

def check_dependencies():
    """Kontrollera att alla beroenden är installerade"""
    try:
        import streamlit
        import openai
        import pandas
        print("✅ Huvudberoenden installerade")
        return True
    except ImportError as e:
        print(f"❌ Saknade beroenden: {e}")
        print("Kör: pip install -r requirements.txt")
        return False

def create_directories():
    """Skapa nödvändiga mappar"""
    directories = ["data", "data/audio"]
    for directory in directories:
        Path(directory).mkdir(exist_ok=True)
    print("✅ Mappar skapade")

def main():
    """Huvudfunktion"""
    print("🗣️  SamtalsBot - Startar applikation...")
    print("=" * 50)
    
    # Kontroller
    if not check_python_version():
        sys.exit(1)
    
    if not check_dependencies():
        print("\n💡 Installera beroenden med:")
        print("pip install -r requirements.txt")
        sys.exit(1)
    
    if not check_env_file():
        print("\n💡 Konfigurera .env filen och kör sedan:")
        print("python run.py")
        sys.exit(1)
    
    create_directories()
    
    print("=" * 50)
    print("🚀 Startar SamtalsBot...")
    print("📱 Applikationen öppnas i din webbläsare")
    print("🛑 Tryck Ctrl+C för att stoppa")
    print("=" * 50)
    
    # Starta Streamlit
    try:
        subprocess.run([
            sys.executable, "-m", "streamlit", "run", "main.py",
            "--server.headless", "true",
            "--server.enableCORS", "false",
            "--server.enableXsrfProtection", "false"
        ])
    except KeyboardInterrupt:
        print("\n👋 SamtalsBot stängd")
    except Exception as e:
        print(f"\n❌ Fel vid start: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()