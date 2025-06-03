# 🗣️ SamtalsBot - AI-stödd Samtalsmodell för Rektorer

SamtalsBot är en AI-driven applikation som hjälper rektorer att leda strukturerade samtal med sin personal genom en kontrollerad 4-stegs process. Systemet använder OpenAI:s GPT-4 och Whisper för att analysera diskussioner och skapa handlingsplaner.

## 🎯 Funktioner

### Steg 1: Problembeskrivning
- Definiera problemet eller frågan som ska diskuteras
- Få AI-förslag på hur du bäst presenterar det för gruppen
- Strukturerade diskussionsfrågor och mötesformat

### Steg 2: Perspektivinventering  
- Spela in eller ladda upp gruppsamtal
- Automatisk transkribering med Whisper
- AI-analys av olika perspektiv och synvinklar

### Steg 3: Fördjupad diskussion
- Fördjupa diskussionen kring utvalda perspektiv
- AI-analys för att dra slutsatser och identifiera konsensus
- Strukturerade rekommendationer för handlingsplan

### Steg 4: Handlingsplan
- Automatisk generering av strukturerad handlingsplan
- Exportfunktion för färdig plan
- Ansvar, tidsramar och uppföljning

## 🚀 Installation

### Förutsättningar
- Python 3.8 eller senare
- OpenAI API-nyckel

### Steg-för-steg installation

1. **Klona projektet**
```bash
git clone <repository-url>
cd SamtalsBot
```

2. **Skapa virtuell miljö**
```bash
python -m venv venv
source venv/bin/activate  # På Windows: venv\Scripts\activate
```

3. **Installera beroenden**
```bash
pip install -r requirements.txt
```

4. **Konfigurera miljövariabler**
```bash
cp .env.example .env
```

Redigera `.env` filen och lägg till din OpenAI API-nyckel:
```
OPENAI_API_KEY=din_openai_api_nyckel_här
```

5. **Starta applikationen**
```bash
streamlit run main.py
```

Applikationen öppnas automatiskt i din webbläsare på `http://localhost:8501`

## 📁 Projektstruktur

```
SamtalsBot/
├── main.py                 # Huvudapplikation
├── pages/                  # Streamlit-sidor för varje steg
│   ├── steg1.py            # Problembeskrivning
│   ├── steg2.py            # Perspektivinventering
│   ├── steg3.py            # Fördjupad diskussion
│   └── steg4.py            # Handlingsplan
├── utils/                  # Hjälpfunktioner
│   ├── ai_helper.py        # AI-integration
│   ├── audio_handler.py    # Ljudbehandling
│   ├── database.py         # Databashantering
│   └── session_manager.py  # Sessionshantering
├── data/                   # Databas och ljudfiler
│   ├── sessions.db         # SQLite databas
│   └── audio/              # Ljudfiler
├── .streamlit/             # Streamlit-konfiguration
│   └── config.toml
├── requirements.txt        # Python-beroenden
├── .env.example           # Exempel på miljövariabler
└── README.md              # Denna fil
```

## 🔧 Konfiguration

### OpenAI API
Du behöver en OpenAI API-nyckel för att använda SamtalsBot. Skaffa en på [OpenAI:s webbplats](https://platform.openai.com/api-keys).

### Ljudinspelning
Applikationen stöder:
- Filuppladdning (WAV, MP3, M4A, MP4)
- Direktinspelning i webbläsaren (kräver `streamlit-audio-recorder`)

### Databas
SamtalsBot använder SQLite för lokal datalagring. Databasen skapas automatiskt vid första körningen.

## 📊 Användning

1. **Skapa en ny session** med sessionens namn och ditt namn som rektor
2. **Steg 1**: Beskriv problemet och få AI-förslag för presentation
3. **Steg 2**: Spela in gruppsamtal och få perspektivanalys
4. **Steg 3**: Fördjupa diskussionen och få slutsatser
5. **Steg 4**: Generera och exportera handlingsplan

### Tips för bästa resultat
- Använd tydliga problembeskrivningar
- Se till att ljudkvaliteten är bra vid inspelning
- Granska och redigera AI-förslag innan godkännande
- Spara regelbundet som utkast

## 🔒 Säkerhet och Integritet

- All data lagras lokalt på din dator
- Ljudfiler krypteras och kan raderas automatiskt
- GDPR-kompatibel datahantering
- Ingen delning av data med tredje part (förutom OpenAI för AI-analys)

## 🛠️ Utveckling

### Köra i utvecklingsläge
```bash
streamlit run main.py --server.runOnSave true
```

### Testa funktionalitet
```bash
python -m pytest tests/  # Om testerna implementeras
```

### Bidra till projektet
1. Forka repositoriet
2. Skapa en feature branch
3. Gör dina ändringar
4. Skicka en pull request

## 📋 Systemkrav

- **Python**: 3.8+
- **RAM**: Minst 4GB (8GB rekommenderat)
- **Lagring**: 1GB för applikation + utrymme för ljudfiler
- **Internet**: Krävs för AI-funktionalitet
- **Webbläsare**: Modern webbläsare med JavaScript aktiverat

## 🔧 Felsökning

### Vanliga problem

**"OpenAI API-nyckel saknas"**
- Kontrollera att `.env` filen finns och innehåller giltig API-nyckel
- Starta om applikationen efter att ha lagt till nyckeln

**"Kunde inte transkribera ljudfil"**
- Kontrollera att filen är i rätt format (WAV, MP3, M4A)
- Se till att filen inte är korrupt
- Kontrollera internetanslutning

**"Databas-fel"**
- Kontrollera att `data/` mappen är skrivbar
- Ta bort `data/sessions.db` för att återställa databasen

### Loggar
Streamlit-loggar visas i terminalen där applikationen körs.

## 📞 Support

För support och frågor:
- Skapa en issue på GitHub
- Kontakta utvecklingsteamet

## 📄 Licens

Detta projekt är licensierat under MIT-licensen. Se LICENSE-filen för detaljer.

## 🙏 Erkännanden

- OpenAI för GPT-4 och Whisper API
- Streamlit för det fantastiska ramverket
- Svenska skolor som inspirerat till denna lösning

## 🔄 Versionshistorik

### v1.0.0 (2024-06-03)
- Initial release
- Komplett 4-stegs process
- AI-integration med OpenAI
- Ljudtranskribering
- Export av handlingsplaner

---

**SamtalsBot** - Utvecklad för svenska rektorer som vill leda mer strukturerade och produktiva personalsamtal med AI-stöd.