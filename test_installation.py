#!/usr/bin/env python3
"""
Test script för att kontrollera att SamtalsBot är korrekt installerat
"""

import sys
import os
from pathlib import Path

def test_python_version():
    """Testa Python-version"""
    print("🐍 Testar Python-version...")
    if sys.version_info >= (3, 8):
        print(f"✅ Python {sys.version_info.major}.{sys.version_info.minor} OK")
        return True
    else:
        print(f"❌ Python {sys.version_info.major}.{sys.version_info.minor} - Kräver 3.8+")
        return False

def test_imports():
    """Testa att alla nödvändiga moduler kan importeras"""
    print("\n📦 Testar imports...")
    
    modules = [
        ("streamlit", "Streamlit"),
        ("openai", "OpenAI"),
        ("pandas", "Pandas"),
        ("sqlite3", "SQLite3"),
        ("dotenv", "Python-dotenv")
    ]
    
    all_ok = True
    for module, name in modules:
        try:
            __import__(module)
            print(f"✅ {name}")
        except ImportError:
            print(f"❌ {name} - Kör: pip install -r requirements.txt")
            all_ok = False
    
    return all_ok

def test_file_structure():
    """Testa att alla nödvändiga filer finns"""
    print("\n📁 Testar filstruktur...")
    
    required_files = [
        "main.py",
        "requirements.txt",
        ".env.example",
        "README.md",
        "utils/database.py",
        "utils/session_manager.py",
        "utils/ai_helper.py",
        "utils/audio_handler.py",
        "pages/steg1.py",
        "pages/steg2.py",
        "pages/steg3.py",
        "pages/steg4.py"
    ]
    
    all_ok = True
    for file_path in required_files:
        if Path(file_path).exists():
            print(f"✅ {file_path}")
        else:
            print(f"❌ {file_path} saknas")
            all_ok = False
    
    return all_ok

def test_env_file():
    """Testa .env konfiguration"""
    print("\n🔧 Testar .env konfiguration...")
    
    env_file = Path(".env")
    if not env_file.exists():
        print("⚠️  .env fil saknas - kopiera från .env.example")
        return False
    
    try:
        with open(".env", "r") as f:
            content = f.read()
            if "OPENAI_API_KEY=" in content:
                if "your_openai_api_key_here" in content:
                    print("⚠️  OpenAI API-nyckel inte konfigurerad")
                    return False
                else:
                    print("✅ OpenAI API-nyckel konfigurerad")
                    return True
            else:
                print("❌ OPENAI_API_KEY saknas i .env")
                return False
    except Exception as e:
        print(f"❌ Kunde inte läsa .env: {e}")
        return False

def test_database():
    """Testa databasanslutning"""
    print("\n🗄️  Testar databas...")
    
    try:
        from utils.database import create_tables, get_connection
        
        # Skapa tabeller
        create_tables()
        print("✅ Databastabeller skapade")
        
        # Testa anslutning
        conn = get_connection()
        conn.close()
        print("✅ Databasanslutning OK")
        
        return True
    except Exception as e:
        print(f"❌ Databasfel: {e}")
        return False

def test_ai_helper():
    """Testa AI-helper utan att göra API-anrop"""
    print("\n🤖 Testar AI-helper...")
    
    try:
        from utils.ai_helper import validate_api_key
        
        if validate_api_key():
            print("✅ AI-helper konfigurerad")
            return True
        else:
            print("⚠️  API-nyckel inte giltig")
            return False
    except Exception as e:
        print(f"❌ AI-helper fel: {e}")
        return False

def main():
    """Huvudfunktion"""
    print("🗣️  SamtalsBot - Installationstest")
    print("=" * 50)
    
    tests = [
        test_python_version,
        test_imports,
        test_file_structure,
        test_env_file,
        test_database,
        test_ai_helper
    ]
    
    results = []
    for test in tests:
        results.append(test())
    
    print("\n" + "=" * 50)
    print("📊 TESTRESULTAT:")
    
    passed = sum(results)
    total = len(results)
    
    if passed == total:
        print(f"🎉 Alla tester godkända! ({passed}/{total})")
        print("\n🚀 SamtalsBot är redo att användas!")
        print("Kör: python run.py")
    else:
        print(f"⚠️  {passed}/{total} tester godkända")
        print("\n🔧 Åtgärda problemen ovan innan du kör applikationen")
    
    return passed == total

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)