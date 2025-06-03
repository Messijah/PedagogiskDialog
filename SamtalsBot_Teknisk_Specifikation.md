# SamtalsBot - Teknisk Specifikation och Implementeringsplan

## Projektöversikt

SamtalsBot är en AI-stödd samtalsmodell för rektorer som hjälper till att leda strukturerade samtal med lärare och annan skolpersonal. Systemet följer en kontrollerad 4-stegs process där användaren har full kontroll över varje steg.

## Systemarkitektur

### Teknisk Stack
- **Frontend/Backend:** Streamlit (Python)
- **Databas:** SQLite
- **AI-integration:** OpenAI GPT-4 + Whisper API
- **Ljudbehandling:** Streamlit Audio Recorder
- **Deployment:** Streamlit Cloud

### Projektstruktur
```
samtalsbot/
├── main.py                 # Huvudapp med navigation
├── pages/
│   ├── steg1.py            # Problembeskrivning
│   ├── steg2.py            # Perspektivinventering
│   ├── steg3.py            # Fördjupad diskussion
│   └── steg4.py            # Handlingsplan
├── utils/
│   ├── ai_helper.py        # AI-integration
│   ├── audio_handler.py    # Ljudinspelning och transkribering
│   ├── database.py         # SQLite databas hantering
│   └── session_manager.py  # Session state hantering
├── data/
│   ├── sessions.db         # SQLite databas
│   └── audio/              # Ljudfiler
├── templates/
│   └── handlingsplan_mall.md # Mall för handlingsplan
├── requirements.txt
├── .streamlit/
│   └── config.toml         # Streamlit konfiguration
└── README.md
```

## Detaljerad Funktionalitet

### Steg 1: Problembeskrivning och Presentation
**Användarinput:**
- Textområde för problembeskrivning
- Dropdown för personalgrupp (Lärare, EHT-personal, Blandad grupp, Annat)
- Fritext för ytterligare kontext

**AI-funktionalitet:**
- Strukturerar problembeskrivningen
- Föreslår presentationsformat för personalgruppen
- Genererar diskussionsfrågor
- Identifierar potentiella utmaningar

**Kontrollpunkt:**
- Användaren granskar AI:s förslag
- Kan revidera eller godkänna
- Måste godkännas innan Steg 2 aktiveras

### Steg 2: Perspektivinventering
**Användarinput:**
- Ljudinspelning av gruppsamtal (via Streamlit Audio Recorder)
- Alternativ: Filuppladdning av ljudfil
- Möjlighet att lägga till manuella anteckningar

**AI-funktionalitet:**
- Transkriberar ljudfilen med Whisper API
- Identifierar olika perspektiv och synvinklar
- Kategoriserar åsikter och förslag
- Föreslår vilka perspektiv som bör fördjupas

**Kontrollpunkt:**
- Användaren granskar transkribering och analys
- Väljer vilka perspektiv som ska fördjupas
- Kan be om omanalys

### Steg 3: Fördjupad Diskussion
**Användarinput:**
- Ny ljudinspelning av fördjupad diskussion
- Fokus på valda perspektiv från Steg 2

**AI-funktionalitet:**
- Transkriberar den fördjupade diskussionen
- Analyserar argumenten i detalj
- Identifierar konsensus och konfliktområden
- Drar slutsatser och föreslår åtgärder

**Kontrollpunkt:**
- Användaren granskar slutsatserna
- Kan be om ytterligare analys
- Godkänner innan handlingsplan skapas

### Steg 4: Handlingsplan
**Användarinput:**
- Godkända slutsatser från Steg 3
- Eventuella tillägg eller justeringar

**AI-funktionalitet:**
- Skapar strukturerad handlingsplan
- Fördelar ansvar och sätter tidsramar
- Föreslår uppföljningsmekanismer
- Skapar mätbara mål

**Slutresultat:**
- Exporterbar handlingsplan (PDF/Word)
- Sammanfattning av hela processen
- Möjlighet att spara session för framtida referens

## Teknisk Implementation

### Databas Schema (SQLite)
```sql
CREATE TABLE sessions (
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
    steg2_selected_perspectives TEXT, -- JSON
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
);
```

### AI Prompts

#### Steg 1 Prompt
```python
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
```

#### Steg 2 Prompt
```python
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
```

#### Steg 3 Prompt
```python
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
```

#### Steg 4 Prompt
```python
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
```

### Säkerhet och GDPR

#### Dataskydd
- Lokal lagring av känslig data
- Kryptering av ljudfiler
- Automatisk radering efter specificerad tid
- Användarens rätt att radera data

#### Integritet
- Ingen delning av data med tredje part
- Säker API-kommunikation med OpenAI
- Anonymisering av data vid behov

### Användargränssnitt Design

#### Navigation
- Tydlig progress-indikator (1/4, 2/4, etc.)
- Steg-för-steg navigation
- Möjlighet att gå tillbaka och revidera
- Låsta steg tills föregående är godkänt

#### Kontrollpunkter
- Tydlig presentation av AI-analys
- "Godkänn och fortsätt" knapp
- "Revidera" knapp med möjlighet till kommentarer
- Visuell feedback på status

#### Responsiv Design
- Fungerar på desktop och tablet
- Optimerad för svenska användare
- Tillgänglighetsanpassad

## Implementeringsplan

### Fas 1: Grundstruktur (Vecka 1)
- [ ] Skapa projektstruktur
- [ ] Implementera main.py med navigation
- [ ] Sätta upp databas (SQLite)
- [ ] Grundläggande session management

### Fas 2: Steg 1 Implementation (Vecka 1-2)
- [ ] Skapa steg1.py
- [ ] Implementera AI-integration för Steg 1
- [ ] Testa och validera funktionalitet
- [ ] Användargränssnitt för Steg 1

### Fas 3: Steg 2 Implementation (Vecka 2-3)
- [ ] Ljudinspelning med Streamlit
- [ ] Whisper API integration
- [ ] AI-analys för perspektiv
- [ ] Steg2.py implementation

### Fas 4: Steg 3 Implementation (Vecka 3-4)
- [ ] Fördjupad diskussion funktionalitet
- [ ] AI-analys för slutsatser
- [ ] Steg3.py implementation
- [ ] Integration med föregående steg

### Fas 5: Steg 4 Implementation (Vecka 4-5)
- [ ] Handlingsplan generering
- [ ] Export funktionalitet (PDF/Word)
- [ ] Steg4.py implementation
- [ ] Slutgiltig integration

### Fas 6: Testing och Deployment (Vecka 5-6)
- [ ] Omfattande testning av hela flödet
- [ ] Säkerhetsvalidering
- [ ] GDPR-compliance kontroll
- [ ] Deployment till Streamlit Cloud
- [ ] Dokumentation och användarguide

## Tekniska Krav

### Python Paket (requirements.txt)
```
streamlit>=1.28.0
openai>=1.0.0
whisper-openai>=20231117
sqlite3
pandas>=2.0.0
plotly>=5.15.0
streamlit-audio-recorder>=0.0.8
python-docx>=0.8.11
reportlab>=4.0.0
python-dotenv>=1.0.0
```

### Miljövariabler (.env)
```
OPENAI_API_KEY=your_openai_api_key_here
STREAMLIT_THEME=light
MAX_AUDIO_DURATION=3600  # 1 hour in seconds
AUTO_DELETE_DAYS=90      # Auto delete sessions after 90 days
```

### Streamlit Konfiguration (.streamlit/config.toml)
```toml
[theme]
primaryColor = "#1f77b4"
backgroundColor = "#ffffff"
secondaryBackgroundColor = "#f0f2f6"
textColor = "#262730"

[server]
maxUploadSize = 200
enableCORS = false
```

## Framtida Utveckling

### Fas 2 Funktioner
- [ ] Multi-user support med autentisering
- [ ] Avancerad rapportering och analytics
- [ ] Integration med skolans befintliga system
- [ ] Mobile app version
- [ ] Offline-funktionalitet

### Förbättringar
- [ ] Bättre AI-modeller för svensk kontext
- [ ] Automatisk sentiment-analys
- [ ] Integrerad videoinspelning
- [ ] Kollaborativa funktioner
- [ ] API för externa integrationer

## Slutsats

Denna tekniska specifikation ger en komplett roadmap för utveckling av SamtalsBot. Systemet är designat för att vara enkelt att använda samtidigt som det ger kraftfull AI-stödd funktionalitet för rektorer i svenska skolor.

Nästa steg är att växla till Code-mode för att börja implementera denna specifikation.