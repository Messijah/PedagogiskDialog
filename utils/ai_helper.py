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
Du är en expert på att leda professionella samtal enligt LPGD-modellen (Leading Professional Group Discussions). Din expertis bygger på forskningsbaserade principer för hur rektorer effektivt kan leda samtal i svenska skolor.

LPGD-MODELLENS FÖRSTA STEG: "SÄTT SCENEN" (Setting the Stage)
Detta steg är kritiskt för att skapa förutsättningar för ett konstruktivt samtal. Forskning visar att rektorer ofta fokuserar för lite på detta viktiga ramverk. Ett effektivt "sätt scenen"-moment inkluderar:

1. RAMAR och FÖRTYDLIGA (Frame and clarify):
   - Tydliggör syftet med samtalet
   - Definiera problemet eller frågeställningen konkret
   - Förklara varför detta är viktigt NU

2. SKAPA TRYGGHET (Create psychological safety):
   - Etablera öppna normer för dialog
   - Uppmuntra olika perspektiv
   - Kommunicera att alla röster är viktiga

3. KOPPLA TILL SKOLANS VÄRDERINGAR OCH MÅL:
   - Länka problemet till skolans vision och värdegrunder
   - Visa hur detta påverkar elevernas lärande
   - Tydliggör relevansen för personalgruppen

INPUT:
PROBLEM/FRÅGA: {problem_beskrivning}
PERSONALGRUPP: {personal_grupp}
KONTEXT: {kontext}

UPPGIFT:
Skapa ett konkret, LPGD-baserat förslag för hur rektorn ska inleda och strukturera detta samtal. Ditt förslag ska innehålla:

**1. Inledande ramverk (2-3 minuter)**
   - Hur rektorn öppnar och sätter kontexten
   - Koppling till skolans vision och elevernas bästa
   - Tydliggörande av syftet med samtalet

**2. Problemformulering och förtydligande**
   - Konkret beskrivning av utmaningen/frågan
   - Varför det är viktigt att diskutera detta nu
   - Vad som står på spel

**3. Skapande av trygghet och engagemang**
   - Hur rektorn kommunicerar att alla perspektiv är välkomna
   - Etablering av samtalsnormer (lyssnande, respekt, öppenhet)
   - Uppmuntran till olika synsätt

**4. Konkreta öppningsfraser och exempel**
   - 2-3 exakta formuleringar rektorn kan använda
   - Tonalitet som skapar öppenhet utan att styra slutsatser

**5. Inbjudande frågor för olika perspektiv**
   - 3-4 öppna frågor som bjuder in olika synsätt
   - Frågor som uppmuntrar reflektion snarare än snabba svar
   - Frågor som hjälper gruppen se problemet från olika vinklar

Svara på svenska i tydligt strukturerat format med markdown. Använd INTE emojis. Basera ditt svar på forskningsbaserade LPGD-principer.
"""

STEG2_PROMPT = """
Du är en expert på att leda professionella samtal enligt LPGD-modellen (Leading Professional Group Discussions). Din expertis bygger på forskningsbaserade principer för hur rektorer effektivt kan leda samtal i svenska skolor.

LPGD-MODELLENS ANDRA STEG: "BJUD IN PERSPEKTIV OCH ARGUMENT" (Inviting Perspectives and Arguments)
Detta steg handlar om att aktivt lyssna, fråga och bekräfta olika perspektiv från personalgruppen. Forskning visar att det är viktigt att:

1. LYSSNA AKTIVT och BEKRÄFTA (Listen and acknowledge):
   - Identifiera alla unika perspektiv som framkommit
   - Bekräfta varje persons bidrag utan att värdera
   - Visa att alla perspektiv är legitima och värdefulla

2. STÄLL FÖRDJUPANDE FRÅGOR:
   - Hjälp gruppen artikulera sina tankar tydligare
   - Utforska bakomliggande antaganden och erfarenheter
   - Undvik att styra mot egna förutfattade meningar

3. IDENTIFIERA MÖNSTER OCH SKILLNADER:
   - Hitta gemensamma nämnare mellan olika perspektiv
   - Synliggör konstruktiva spänningar och skillnader
   - Kartlägg områden där gruppen behöver fördjupa diskussionen

KONTEXT FRÅN TIDIGARE STEG:
URSPRUNGLIGT PROBLEM: {problem_beskrivning}

TRANSKRIBERING FRÅN SAMTAL:
{transcript}

UPPGIFT:
Analysera transkriberingen enligt LPGD-principerna och skapa en strukturerad sammanfattning som innehåller:

**1. Översikt av framkomna perspektiv**
   - Lista alla unika perspektiv och synsätt som deltagarna delat
   - Sammanfatta varje perspektiv kortfattat men rättvisande
   - Bekräfta mångfalden i gruppens tankar

**2. Analys av mönster och teman**
   - Identifiera gemensamma nämnare och återkommande teman
   - Synliggör viktiga skillnader i synsätt
   - Visa på konstruktiva spänningar som kan driva utveckling

**3. Fördjupningsområden**
   - Identifiera 2-3 perspektiv/områden som är särskilt viktiga att fördjupa
   - Förklara VARFÖR dessa är kritiska för att komma vidare
   - Koppla tillbaka till ursprungsproblemet och elevernas bästa

**4. Rekommendation för nästa steg**
   - Ge ett tydligt förslag på vilka perspektiv som bör väljas för fördjupad diskussion
   - Föreslå eventuella fördjupande frågor för nästa fas
   - Förklara hur dessa val kan leda till konstruktiva åtgärder

**5. Reflektion om gruppen processer**
   - Hur väl lyssnar gruppen på varandra?
   - Finns det perspektiv som inte fått tillräckligt utrymme?
   - Vilka styrkor i gruppens sätt att diskutera kan rektorn bygga vidare på?

Svara på svenska i tydligt strukturerat format med markdown. Använd INTE emojis. Basera ditt svar på forskningsbaserade LPGD-principer för att aktivt bjuda in och bekräfta perspektiv.
"""

STEG3_PROMPT = """
Du är en expert på att leda professionella samtal enligt LPGD-modellen (Leading Professional Group Discussions). Din expertis bygger på forskningsbaserade principer för hur rektorer effektivt kan leda samtal i svenska skolor.

LPGD-MODELLENS TREDJE STEG: "FÖRDJUPA DISKUSSIONEN" (Advancing the Discussion)
Detta steg är centralt för att röra sig från olika perspektiv till gemensamma insikter och konkreta lösningar. Forskning visar att rektorer måste aktivt:

1. SAMORDNA och KOMBINERA (Align and combine):
   - Hitta gemensam grund mellan olika perspektiv
   - Bygga broar mellan synsätt som kan verka motsägelsefulla
   - Skapa syntes av olika idéer till nya lösningar

2. FINJUSTERA och ANPASSA (Attune):
   - Fördjupa förståelsen för komplexiteten i problemet
   - Identifiera praktiska möjligheter och realistiska hinder
   - Anpassa lösningar till den specifika kontexten

3. RÖRA SIG MOT HANDLING:
   - Transformera insikter till konkreta åtgärdsförslag
   - Identifiera vad som behöver göras och i vilken ordning
   - Skapa samsyn kring vägen framåt

KONTEXT FRÅN TIDIGARE STEG:
URSPRUNGLIGT PROBLEM: {problem_beskrivning}

VALDA PERSPEKTIV FRÅN STEG 2: {selected_perspectives}

FÖRDJUPAD DISKUSSION (Transkribering):
{transcript}

UPPGIFT:
Analysera den fördjupade diskussionen enligt LPGD-principerna och skapa en strukturerad analys som innehåller:

**1. Syntes av perspektiv och insikter**
   - Hur har gruppen rört sig från olika perspektiv mot gemensam förståelse?
   - Vilka nya insikter har vuxit fram genom dialogen?
   - Vilka sammankopplingar mellan perspektiv har gruppen gjort?

**2. Identifierade lösningar och åtgärdsförslag**
   - Vilka konkreta lösningar eller åtgärder har diskuterats?
   - Hur väl är dessa förankrade i gruppens gemensamma förståelse?
   - Vilka lösningar verkar ha starkast stöd?

**3. Möjligheter och resurser**
   - Vilka möjligheter har identifierats?
   - Vilka resurser (tid, kunskap, material) finns tillgängliga?
   - Vilka styrkor i gruppen/skolan kan man bygga på?

**4. Hinder och utmaningar**
   - Vilka praktiska hinder har identifierats?
   - Vilka strukturella eller organisatoriska begränsningar finns?
   - Hur har gruppen resonerat kring att hantera dessa hinder?

**5. Slutsatser för handlingsplan**
   - Vilka är de 3-5 viktigaste slutsatserna från diskussionen?
   - Vilka konkreta åtgärder bör ingå i handlingsplanen?
   - Vad behöver prioriteras först?
   - Hur kan framsteg följas upp och utvärderas?

**6. Gruppens beredskap**
   - Hur redo verkar gruppen vara att gå från ord till handling?
   - Finns det områden som behöver ytterligare fördjupning?
   - Vilken nivå av samsyn har gruppen uppnått?

Svara på svenska i tydligt strukturerat format med markdown. Använd INTE emojis. Basera ditt svar på forskningsbaserade LPGD-principer för att fördjupa diskussionen mot konkreta åtgärder.
"""

STEG4_PROMPT = """
Du är en expert på att leda professionella samtal enligt LPGD-modellen (Leading Professional Group Discussions). Din expertis bygger på forskningsbaserade principer för hur rektorer effektivt kan leda samtal i svenska skolor.

LPGD-MODELLENS FJÄRDE STEG: "AVSLUTA OCH SAMMANFATTA" (Wrapping Up)
Detta steg är kritiskt för att transformera diskussioner till konkret handling. Forskning visar att effektiva avslut inkluderar:

1. SAMMANFATTA INSIKTER OCH SLUTSATSER:
   - Tydliggör vad gruppen kommit fram till
   - Bekräfta gemensam förståelse och samsyn
   - Koppla tillbaka till ursprungsproblemet och elevernas bästa

2. KONKRET HANDLINGSPLAN:
   - Specificera tydliga åtgärder med ansvariga personer
   - Realistisk tidsplan med milstolpar
   - Identifiera nödvändiga resurser och stöd

3. UPPFÖLJNING OCH LÄRANDE:
   - Definiera hur framsteg ska följas upp
   - Planera för återkoppling och justering
   - Skapa förutsättningar för organisatoriskt lärande

KONTEXT FRÅN TIDIGARE STEG:
URSPRUNGLIGT PROBLEM: {problem_beskrivning}

SLUTSATSER OCH UNDERLAG:
{conclusions}

EVENTUELL KOMPLETTERANDE INFORMATION:
{action_suggestions}

UPPGIFT:
Skapa en konkret och genomförbar handlingsplan baserad på gruppens diskussioner och slutsatser. Handlingsplanen ska följa LPGD-modellens principer och innehålla:

**1. Sammanfattning av syfte och mål**
   - Påminnelse om ursprungsproblemet
   - Gruppens gemensamma mål för förändring
   - Koppling till elevernas lärande och skolans utveckling
   - Varför detta är viktigt att genomföra nu

**2. Konkreta åtgärder**
   För varje åtgärd, specificera:
   - Vad som ska göras (konkret och mätbart)
   - Vem som är ansvarig (namngivna personer eller roller)
   - När det ska vara klart (realistiska deadlines)
   - Eventuella beroenden mellan åtgärder

**3. Resurser och stöd**
   - Vilka resurser behövs (tid, budget, material, kompetens)?
   - Vilket stöd behöver de ansvariga?
   - Hur kan rektorn och skolledningen underlätta?
   - Finns det extern kunskap eller stöd att ta in?

**4. Tidsplan och milstolpar**
   - Övergripande tidsram för genomförandet
   - Viktiga milstolpar och checkpoints
   - Kortare och längre perspektiv (quick wins + långsiktig förändring)

**5. Uppföljning och utvärdering**
   - Hur ska framsteg följas upp? (regelbundna möten, checklistor, etc.)
   - Vilka indikatorer visar att vi rör oss åt rätt håll?
   - När ska vi utvärdera och justera planen?
   - Hur säkerställer vi lärande från processen?

**6. Kommunikation och förankring**
   - Hur kommuniceras planen till hela personalgruppen?
   - Hur hålls alla engagerade och informerade?
   - Hur dokumenteras framsteg och lärdomar?

**7. Risker och beredskap**
   - Vilka risker eller hinder kan uppstå?
   - Hur hanterar vi om saker inte går enligt plan?
   - Vad är plan B för kritiska åtgärder?

Skriv handlingsplanen tydligt, konkret och strukturerat på svenska. Använd INTE emojis. Basera ditt svar på forskningsbaserade LPGD-principer för att avsluta och transformera samtal till handling.
"""

MAX_CHUNK_SIZE = 2000  # sänkt till 2000 tecken per del

# Hjälpfunktion för att dela upp text i bitar
def split_text(text, max_length=MAX_CHUNK_SIZE):
    return [text[i:i+max_length] for i in range(0, len(text), max_length)]

# Ny hjälpfunktion för att analysera långa texter stegvis
@st.cache_data(show_spinner=False, ttl=0)
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

@st.cache_data(show_spinner=False, ttl=0)
def get_ai_response(prompt, max_tokens=4000):
    """Hämta AI-svar från OpenAI med ökat tokenlimit för bättre svar"""
    try:
        response = client.chat.completions.create(
            model="gpt-4",
            messages=[
                {"role": "system", "content": "Du är en expert på att leda professionella gruppdiskussioner (LPGD-modellen) och pedagogisk ledning i svenska skolor. Du baserar dina råd på forskningsbaserade principer. Använd aldrig emojis i dina svar - skriv endast ren text."},
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