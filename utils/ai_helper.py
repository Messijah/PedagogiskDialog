import openai
import streamlit as st
import os
from dotenv import load_dotenv

# Ladda miljövariabler
load_dotenv()

# Konfigurera OpenAI
openai.api_key = os.getenv('OPENAI_API_KEY')

# AI Prompts
STEG1_PROMPT = """
Du är en samtalscoach för rektorer i svensk skola och expert på att leda professionella samtal enligt LPGD-modellen.

UPPGIFT: Utifrån följande beskrivning av ett problem eller en fråga, ge ett förslag på hur rektorn kan presentera detta för sin personalgrupp på ett sätt som:
- Tydligt definierar syftet och målet med samtalet (Sätt scenen)
- Kopplar till skolans mål/vision
- Skapar trygghet och engagemang
- Lägger grunden för en öppen och lösningsfokuserad dialog

PROBLEM/FRÅGA: {problem_beskrivning}
PERSONALGRUPP: {personal_grupp}
KONTEXT: {kontext}

Ge ett konkret förslag på inledning och struktur för samtalet, inklusive:
1. Hur rektorn kan sätta scenen
2. Exempel på öppningsfraser
3. Hur samtalet kan kopplas till skolans mål/vision
4. Hur trygghet och engagemang kan skapas
5. Förslag på 2-3 öppna frågor som bjuder in olika perspektiv

Svara på svenska i tydligt strukturerat format med markdown.
"""

STEG2_PROMPT = """
Du är en samtalscoach för rektorer. Här är en transkribering från ett samtal där olika perspektiv på ett problem har diskuterats.

UPPGIFT: Sammanfatta och strukturera de olika perspektiv, argument och synsätt som framkommit enligt LPGD-modellen:
1. Bjud in olika perspektiv och argument
2. Identifiera mönster, gemensamma nämnare och skillnader
3. Lyft fram 2-3 perspektiv som är särskilt viktiga att fördjupa i nästa steg

URSPRUNGLIGT PROBLEM: {problem_beskrivning}
TRANSKRIBERING: {transcript}

Ge en tydlig och strukturerad sammanfattning som underlag för fördjupad diskussion. Avsluta med rekommendation om vilka perspektiv som bör väljas för fördjupning.
"""

STEG3_PROMPT = """
Du är en samtalscoach för rektorer. Här är en transkribering från en fördjupad diskussion om utvalda perspektiv.

UPPGIFT: Analysera samtalet och dra slutsatser kring:
- Vilka lösningar, insikter eller åtgärdsförslag har diskuterats?
- Vilka hinder och möjligheter har identifierats?
- Vilka slutsatser kan ligga till grund för en konkret handlingsplan?

Följ LPGD-modellen: 1. Fördjupa och strukturera diskussionen, 2. Sammanfatta mönster och insikter, 3. Avsluta med konkreta slutsatser.

URSPRUNGLIGT PROBLEM: {problem_beskrivning}
VALDA PERSPEKTIV FRÅN STEG 2: {selected_perspectives}
FÖRDJUPAD DISKUSSION: {transcript}

Ge en tydlig sammanfattning av slutsatser och möjliga åtgärder.
"""

STEG4_PROMPT = """
Du är en samtalscoach för rektorer. Här är en sammanfattning/slutsats eller transkribering från ett samtal om åtgärder.

UPPGIFT: Skriv en konkret handlingsplan enligt denna mall:
- Syfte och mål
- Viktiga åtgärder och ansvariga
- Tidsplan och uppföljning
- Stöd och resurser

UNDERLAG: {conclusions}

Skriv handlingsplanen tydligt och strukturerat på svenska.
"""

@st.cache_data(show_spinner=False)
def get_ai_response(prompt, max_tokens=2000):
    """Hämta AI-svar från OpenAI"""
    try:
        response = openai.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Du är en expert på pedagogisk ledning i svenska skolor."},
                {"role": "user", "content": prompt}
            ],
            max_tokens=max_tokens,
            temperature=0.7
        )
        return response.choices[0].message.content
    except Exception as e:
        st.error(f"Fel vid AI-anrop: {str(e)}")
        return None

def get_ai_suggestion_steg1(problem_beskrivning, personal_grupp, kontext=""):
    """Hämta AI-förslag för Steg 1"""
    prompt = STEG1_PROMPT.format(
        problem_beskrivning=problem_beskrivning,
        personal_grupp=personal_grupp,
        kontext=kontext
    )
    return get_ai_response(prompt)

def analyze_perspectives_steg2(problem_beskrivning, transcript):
    """Analysera perspektiv för Steg 2"""
    prompt = STEG2_PROMPT.format(
        problem_beskrivning=problem_beskrivning,
        transcript=transcript
    )
    return get_ai_response(prompt)

def analyze_discussion_steg3(problem_beskrivning, selected_perspectives, transcript):
    """Analysera fördjupad diskussion för Steg 3"""
    prompt = STEG3_PROMPT.format(
        problem_beskrivning=problem_beskrivning,
        selected_perspectives=selected_perspectives,
        transcript=transcript
    )
    return get_ai_response(prompt)

def create_action_plan_steg4(problem_beskrivning, conclusions, action_suggestions=""):
    """Skapa handlingsplan för Steg 4"""
    prompt = STEG4_PROMPT.format(
        problem_beskrivning=problem_beskrivning,
        conclusions=conclusions,
        action_suggestions=action_suggestions
    )
    return get_ai_response(prompt, max_tokens=3000)

def validate_api_key():
    """Validera att OpenAI API-nyckel är konfigurerad"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your_openai_api_key_here':
        return False
    return True