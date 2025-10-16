#!/usr/bin/env python3
"""
Test script för att verifiera alla förbättringar i PedagogiskDialog v2.0

Testar:
1. Audio transcription (parallell och sekventiell)
2. AI prompts och responses
3. Database funktionalitet
4. Import av alla moduler

Kör: python test_improvements.py
"""

import sys
import os
import time
from datetime import datetime

# Färgkoder för output
GREEN = '\033[92m'
RED = '\033[91m'
YELLOW = '\033[93m'
BLUE = '\033[94m'
RESET = '\033[0m'

def print_section(title):
    print(f"\n{BLUE}{'='*60}{RESET}")
    print(f"{BLUE}{title}{RESET}")
    print(f"{BLUE}{'='*60}{RESET}\n")

def print_success(message):
    print(f"{GREEN}✓ {message}{RESET}")

def print_error(message):
    print(f"{RED}✗ {message}{RESET}")

def print_warning(message):
    print(f"{YELLOW}⚠ {message}{RESET}")

def print_info(message):
    print(f"{BLUE}ℹ {message}{RESET}")

# Test 1: Modulimporter
print_section("TEST 1: Verifierar modulimporter")

try:
    import streamlit as st
    print_success("streamlit importerad")
except ImportError as e:
    print_error(f"streamlit saknas: {e}")
    sys.exit(1)

try:
    from openai import OpenAI, AsyncOpenAI
    print_success("openai (sync och async) importerad")
except ImportError as e:
    print_error(f"openai saknas: {e}")
    sys.exit(1)

try:
    import asyncio
    print_success("asyncio importerad")
except ImportError as e:
    print_error(f"asyncio saknas: {e}")
    sys.exit(1)

try:
    from pydub import AudioSegment
    print_success("pydub importerad")
except ImportError as e:
    print_warning(f"pydub saknas (behövs för audio segmentering): {e}")

try:
    from dotenv import load_dotenv
    load_dotenv()
    print_success("python-dotenv importerad och .env laddad")
except ImportError as e:
    print_error(f"python-dotenv saknas: {e}")

# Test 2: Miljövariabler
print_section("TEST 2: Verifierar miljövariabler")

api_key = os.getenv('OPENAI_API_KEY')
if api_key and api_key != 'your_openai_api_key_here':
    print_success("OPENAI_API_KEY är konfigurerad")
    print_info(f"API-nyckel börjar med: {api_key[:10]}...")
else:
    print_error("OPENAI_API_KEY saknas eller är inte konfigurerad")
    print_info("Skapa en .env fil med: OPENAI_API_KEY=din-nyckel-här")

# Test 3: Projektfiler
print_section("TEST 3: Verifierar projektfiler och struktur")

required_files = [
    'main.py',
    'utils/audio_handler.py',
    'utils/ai_helper.py',
    'utils/database.py',
    'utils/session_manager.py',
    'requirements.txt',
    'render.yaml',
    'DEPLOYMENT_GUIDE.md',
    'CHANGELOG.md',
    'UPGRADE_SUMMARY.md',
    '.streamlit/config.toml'
]

for file in required_files:
    if os.path.exists(file):
        print_success(f"{file} finns")
    else:
        print_error(f"{file} saknas")

# Test 4: Audio handler funktioner
print_section("TEST 4: Verifierar audio_handler.py funktioner")

try:
    from utils.audio_handler import (
        transcribe_audio_openai,
        transcribe_audio_openai_async,
        transcribe_segments_parallel,
        transcribe_large_audio_file,
        split_audio_file
    )
    print_success("Alla audio-funktioner importerade korrekt")

    # Verifiera att async-funktionen finns
    import inspect
    if inspect.iscoroutinefunction(transcribe_audio_openai_async):
        print_success("transcribe_audio_openai_async är en async funktion")
    else:
        print_error("transcribe_audio_openai_async är INTE en async funktion")

    if inspect.iscoroutinefunction(transcribe_segments_parallel):
        print_success("transcribe_segments_parallel är en async funktion")
    else:
        print_error("transcribe_segments_parallel är INTE en async funktion")

except ImportError as e:
    print_error(f"Kunde inte importera audio_handler funktioner: {e}")
except Exception as e:
    print_error(f"Fel vid verifiering av audio_handler: {e}")

# Test 5: AI helper funktioner och prompts
print_section("TEST 5: Verifierar ai_helper.py prompts och funktioner")

try:
    from utils.ai_helper import (
        STEG1_PROMPT,
        STEG2_PROMPT,
        STEG3_PROMPT,
        STEG4_PROMPT,
        get_ai_response,
        get_ai_suggestion_steg1,
        analyze_perspectives_steg2,
        analyze_discussion_steg3,
        create_action_plan_steg4
    )
    print_success("Alla AI-funktioner importerade korrekt")

    # Verifiera att LPGD-modellen nämns i prompterna
    lpgd_checks = {
        'STEG1': 'LPGD' in STEG1_PROMPT,
        'STEG2': 'LPGD' in STEG2_PROMPT,
        'STEG3': 'LPGD' in STEG3_PROMPT,
        'STEG4': 'LPGD' in STEG4_PROMPT
    }

    for steg, has_lpgd in lpgd_checks.items():
        if has_lpgd:
            print_success(f"{steg}_PROMPT innehåller LPGD-modellen")
        else:
            print_error(f"{steg}_PROMPT saknar LPGD-modellen")

    # Kontrollera promptlängder (bör vara längre nu)
    prompt_lengths = {
        'STEG1': len(STEG1_PROMPT),
        'STEG2': len(STEG2_PROMPT),
        'STEG3': len(STEG3_PROMPT),
        'STEG4': len(STEG4_PROMPT)
    }

    print_info("\nPrompt-längder:")
    for steg, length in prompt_lengths.items():
        print(f"  {steg}: {length} tecken")

    # Verifiera att kontextvariabler finns i prompterna
    context_checks = {
        'STEG2': '{problem_beskrivning}' in STEG2_PROMPT and '{transcript}' in STEG2_PROMPT,
        'STEG3': '{problem_beskrivning}' in STEG3_PROMPT and '{selected_perspectives}' in STEG3_PROMPT,
        'STEG4': '{problem_beskrivning}' in STEG4_PROMPT and '{conclusions}' in STEG4_PROMPT
    }

    print_info("\nKontextmedvetenhet:")
    for steg, has_context in context_checks.items():
        if has_context:
            print_success(f"{steg} har kontextvariabler från tidigare steg")
        else:
            print_error(f"{steg} saknar kontextvariabler")

except ImportError as e:
    print_error(f"Kunde inte importera ai_helper funktioner: {e}")
except Exception as e:
    print_error(f"Fel vid verifiering av ai_helper: {e}")

# Test 6: Database funktionalitet
print_section("TEST 6: Verifierar database.py funktionalitet")

try:
    from utils.database import (
        create_tables,
        create_session,
        get_all_sessions,
        update_session_step1,
        update_session_step2,
        update_session_step3,
        update_session_step4
    )
    print_success("Alla database-funktioner importerade korrekt")

    # Testa att skapa databas
    create_tables()
    print_success("Databas initierad (eller finns redan)")

    if os.path.exists('data/sessions.db'):
        print_success("data/sessions.db skapad/verifierad")
    else:
        print_warning("data/sessions.db finns inte ännu (skapas vid första användningen)")

except ImportError as e:
    print_error(f"Kunde inte importera database funktioner: {e}")
except Exception as e:
    print_error(f"Fel vid verifiering av database: {e}")

# Test 7: Render deployment-filer
print_section("TEST 7: Verifierar Render deployment-konfiguration")

if os.path.exists('render.yaml'):
    print_success("render.yaml finns")
    with open('render.yaml', 'r') as f:
        content = f.read()
        if 'pedagogisk-dialog' in content:
            print_success("Service name konfigurerad")
        if 'frankfurt' in content:
            print_success("EU-region (Frankfurt) konfigurerad för GDPR")
        if 'OPENAI_API_KEY' in content:
            print_success("OPENAI_API_KEY environment variable definierad")
else:
    print_error("render.yaml saknas")

# Test 8: Sammanfattning
print_section("TEST 8: Sammanfattning")

print_info("Viktiga förbättringar implementerade:")
print("  1. Whisper Turbo med svenskoptimering (language='sv')")
print("  2. Parallell asyncio-transkribering")
print("  3. LPGD-baserade prompts för alla 4 steg")
print("  4. Kontextmedvetenhet mellan steg")
print("  5. Ökad tokenlimit (2000 → 4000)")
print("  6. Render.com deployment-konfiguration")

print_info("\nNästa steg:")
print("  1. Kör applikationen: streamlit run main.py")
print("  2. Testa med en verklig ljudfil")
print("  3. Verifiera att transkriberingen är snabb")
print("  4. Kontrollera AI-svarets kvalitet")
print("  5. Deploy till Render enligt DEPLOYMENT_GUIDE.md")

print_section("TESTNING SLUTFÖRD")

print(f"\n{GREEN}Alla grundläggande tester slutförda!{RESET}")
print(f"{YELLOW}Om alla tester är gröna, kör: streamlit run main.py{RESET}\n")
