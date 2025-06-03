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
Du är en expert på pedagogisk ledning i svenska skolor med lång erfarenhet av att leda personalgrupper.

UPPGIFT: Analysera följande problem och ge strukturerade förslag för hur rektor ska presentera det för personalgruppen.

PROBLEM: {problem_beskrivning}
PERSONALGRUPP: {personal_grupp}
KONTEXT: {kontext}

GE FÖRSLAG PÅ:

## 1. Presentation av problemet
- Hur problemet bäst introduceras
- Vilken ton och approach som är lämplig
- Hur man skapar öppenhet för diskussion

## 2. Diskussionsfrågor
- 3-5 öppna frågor som uppmuntrar olika perspektiv
- Följdfrågor för att fördjupa diskussionen
- Frågor som hjälper gruppen att fokusera

## 3. Mötesstruktur
- Förslag på tidsram
- Hur diskussionen kan struktureras
- Roller och ansvar under mötet

## 4. Potentiella utmaningar
- Vad som kan bli problematiskt
- Hur man hanterar motstånd eller konflikt
- Sätt att hålla diskussionen konstruktiv

Svara på svenska i tydligt strukturerat format med markdown.
"""

STEG2_PROMPT = """
Du är en expert på att analysera gruppsamtal och identifiera olika perspektiv i pedagogiska diskussioner.

UPPGIFT: Analysera denna transkribering från personalgruppens diskussion och identifiera olika perspektiv.

URSPRUNGLIGT PROBLEM: {problem_beskrivning}
TRANSKRIBERING: {transcript}

ANALYSERA OCH IDENTIFIERA:

## 1. Huvudperspektiv
- Lista de olika synsätt som framkommit
- Gruppera liknande åsikter
- Identifiera motsättningar

## 2. Återkommande teman
- Vilka ämnen som diskuteras mest
- Gemensamma bekymmer eller förslag
- Underliggande värderingar

## 3. Konfliktområden
- Där åsikterna går isär
- Potentiella spänningar
- Områden som behöver fördjupning

## 4. Förslag för Steg 3
- Vilka 2-3 perspektiv som bör fördjupas
- Motivering för varför dessa är viktiga
- Förslag på hur fördjupningen kan göras

## 5. Sammanfattning
- Kort sammanfattning av diskussionens huvuddrag
- Vad som fungerade bra
- Vad som behöver utvecklas

Svara på svenska i strukturerat format.
"""

STEG3_PROMPT = """
Du är en expert på att analysera fördjupade diskussioner och dra konstruktiva slutsatser.

UPPGIFT: Analysera den fördjupade diskussionen och formulera tydliga slutsatser.

URSPRUNGLIGT PROBLEM: {problem_beskrivning}
VALDA PERSPEKTIV FRÅN STEG 2: {selected_perspectives}
FÖRDJUPAD DISKUSSION: {transcript}

ANALYSERA OCH DRA SLUTSATSER:

## 1. Konsensus som uppnåtts
- Vad gruppen är överens om
- Gemensamma lösningsförslag
- Delade värderingar och mål

## 2. Kvarvarande meningsskiljaktigheter
- Områden där åsikterna fortfarande går isär
- Hur dessa kan hanteras
- Kompromissmöjligheter

## 3. Konkreta åtgärdsförslag
- Specifika förslag som framkommit
- Vem som kan ansvara för vad
- Resurser som behövs

## 4. Prioriteringar
- Vad som bör göras först
- Långsiktiga vs kortsiktiga åtgärder
- Vad som är mest kritiskt

## 5. Rekommendationer för handlingsplan
- Huvudområden för handlingsplanen
- Förslag på struktur
- Viktiga element att inkludera

Formulera tydliga, handlingsbara slutsatser på svenska.
"""

STEG4_PROMPT = """
Du är en expert på att skapa strukturerade handlingsplaner för svenska skolor.

UPPGIFT: Skapa en professionell handlingsplan baserat på diskussionens slutsatser.

URSPRUNGLIGT PROBLEM: {problem_beskrivning}
SLUTSATSER FRÅN STEG 3: {conclusions}
ÅTGÄRDSFÖRSLAG: {action_suggestions}

SKAPA EN HANDLINGSPLAN MED:

## 1. Sammanfattning
- Kort beskrivning av problemet
- Huvudsakliga slutsatser från diskussionen

## 2. Mål och syfte
- Vad som ska uppnås
- Mätbara resultat
- Tidsram för måluppfyllelse

## 3. Konkreta åtgärder
För varje åtgärd, ange:
- Vad som ska göras (specifikt)
- Vem som ansvarar
- När det ska vara klart
- Resurser som behövs
- Hur framsteg mäts

## 4. Tidsplan
- Milstolpar och deadlines
- Prioritetsordning
- Beroenden mellan åtgärder

## 5. Uppföljning
- Hur och när uppföljning sker
- Vem som ansvarar för uppföljning
- Kriterier för framgång

## 6. Risker och utmaningar
- Potentiella hinder
- Förebyggande åtgärder
- Alternativa lösningar

Använd professionell ton lämplig för svenska skolor. Formatera som en färdig handlingsplan.
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