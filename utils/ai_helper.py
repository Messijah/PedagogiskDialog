from openai import OpenAI
import streamlit as st
import os
from dotenv import load_dotenv
import math

# Ladda miljövariabler
load_dotenv()

# Konfigurera OpenAI client
client = OpenAI(api_key=os.getenv('OPENAI_API_KEY'))

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

MAX_CHUNK_SIZE = 2000  # sänkt till 2000 tecken per del

# Hjälpfunktion för att dela upp text i bitar
def split_text(text, max_length=MAX_CHUNK_SIZE):
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

# Ny hjälpfunktion för att analysera långa texter stegvis
@st.cache_data(show_spinner=False)
def analyze_long_text(prompt_template, **kwargs):
    text = kwargs.get('transcript') or kwargs.get('conclusions')
    if not text:
        return None
    chunks = split_text(text)
    if len(chunks) == 1:
        prompt = prompt_template.format(**kwargs)
        return get_ai_response(prompt)
    else:
        st.info(f"Transkriberingen är lång ({len(text)} tecken). AI:n analyserar i {len(chunks)} steg – detta kan ta lite längre tid.")
        delanalyser = []
        for idx, chunk in enumerate(chunks):
            st.info(f"Analyserar del {idx+1} av {len(chunks)}...")
            local_kwargs = kwargs.copy()
            local_kwargs['transcript'] = chunk
            prompt = prompt_template.format(**local_kwargs)
            try:
                delanalys = get_ai_response(prompt)
                if delanalys:
                    delanalyser.append(delanalys)
                else:
                    st.warning(f"Delanalys {idx+1} misslyckades och hoppas över.")
            except Exception as e:
                st.warning(f"Fel vid AI-analys av del {idx+1}: {e}. Hoppas över denna del.")
        if not delanalyser:
            st.error("Ingen delanalys lyckades. Försök korta ner texten eller dela upp samtalet manuellt.")
            return None
        # Slå ihop delanalyserna, men om det blir för långt, dela även dessa
        sammanfattningsprompt = (
            "Du är en samtalscoach för rektorer. Här är delanalyser av ett långt samtal. Sammanfatta och strukturera huvuddragen, viktiga perspektiv och slutsatser så att det blir en helhetsbild enligt LPGD-modellen.\n\nDELANALYSER:\n" + "\n\n".join(delanalyser)
        )
        # Om prompten är för lång, dela även delanalyserna i mindre grupper
        if len(sammanfattningsprompt) > MAX_CHUNK_SIZE * 2:
            st.info("Slutlig sammanfattning delas upp i flera steg...")
            sammanfattningar = []
            delgrupper = split_text("\n\n".join(delanalyser), MAX_CHUNK_SIZE)
            for i, grupp in enumerate(delgrupper):
                st.info(f"Sammanfattar delgrupp {i+1} av {len(delgrupper)}...")
                prompt = (
                    "Du är en samtalscoach för rektorer. Här är delanalyser av ett långt samtal. Sammanfatta och strukturera huvuddragen, viktiga perspektiv och slutsatser så att det blir en helhetsbild enligt LPGD-modellen.\n\nDELANALYSER:\n" + grupp
                )
                sammanfattning = get_ai_response(prompt)
                if sammanfattning:
                    sammanfattningar.append(sammanfattning)
                else:
                    st.warning(f"Sammanfattning av delgrupp {i+1} misslyckades.")
            # Slutlig sammanfattning av alla delgruppssammanfattningar
            slutprompt = (
                "Du är en samtalscoach för rektorer. Här är flera del-sammanfattningar av ett långt samtal. Slå ihop till en slutlig, övergripande sammanfattning enligt LPGD-modellen.\n\nSAMMANFATTNINGAR:\n" + "\n\n".join(sammanfattningar)
            )
            return get_ai_response(slutprompt)
        else:
            return get_ai_response(sammanfattningsprompt)

@st.cache_data(show_spinner=False)
def get_ai_response(prompt, max_tokens=2000):
    """Hämta AI-svar från OpenAI"""
    try:
        response = client.chat.completions.create(
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
    """Analysera perspektiv för Steg 2, stöd för långa transkriberingar"""
    return analyze_long_text(
        STEG2_PROMPT,
        problem_beskrivning=problem_beskrivning,
        transcript=transcript
    )

def analyze_discussion_steg3(problem_beskrivning, selected_perspectives, transcript):
    """Analysera fördjupad diskussion för Steg 3, stöd för långa transkriberingar"""
    return analyze_long_text(
        STEG3_PROMPT,
        problem_beskrivning=problem_beskrivning,
        selected_perspectives=selected_perspectives,
        transcript=transcript
    )

def create_action_plan_steg4(problem_beskrivning, conclusions, action_suggestions=""):
    """Skapa handlingsplan för Steg 4, stöd för långa slutsatser/transkriberingar"""
    return analyze_long_text(
        STEG4_PROMPT,
        problem_beskrivning=problem_beskrivning,
        conclusions=conclusions,
        action_suggestions=action_suggestions
    )

def validate_api_key():
    """Validera att OpenAI API-nyckel är konfigurerad"""
    api_key = os.getenv('OPENAI_API_KEY')
    if not api_key or api_key == 'your_openai_api_key_here':
        return False
    return True