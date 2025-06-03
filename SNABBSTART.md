# 🚀 Snabbstart - SamtalsBot

## 1. Förberedelser (5 minuter)

### Installera Python
- Ladda ner Python 3.8+ från [python.org](https://python.org)
- Kontrollera installation: `python --version`

### Skaffa OpenAI API-nyckel
1. Gå till [OpenAI Platform](https://platform.openai.com/api-keys)
2. Logga in eller skapa konto
3. Klicka "Create new secret key"
4. Kopiera nyckeln (börjar med `sk-...`)

## 2. Installation (2 minuter)

```bash
# 1. Ladda ner och gå in i mappen
cd SamtalsBot

# 2. Installera beroenden
pip install -r requirements.txt

# 3. Konfigurera API-nyckel
cp .env.example .env
# Redigera .env och lägg till din API-nyckel
```

**Redigera .env filen:**
```
OPENAI_API_KEY=sk-din_riktiga_nyckel_här
```

## 3. Starta applikationen (30 sekunder)

```bash
python run.py
```

Eller direkt med Streamlit:
```bash
streamlit run main.py
```

Applikationen öppnas automatiskt i din webbläsare på `http://localhost:8501`

## 4. Första användning (10 minuter)

### Skapa din första session
1. **Klicka "Skapa ny session"** i sidopanelen
2. **Ange sessionens namn**: t.ex. "Digitalisering 2024"
3. **Ange ditt namn** som rektor
4. **Klicka "Skapa session"**

### Genomför 4-stegs processen

#### 🎯 Steg 1: Problembeskrivning (2 min)
- Beskriv problemet du vill diskutera
- Välj personalgrupp
- Klicka "Få AI-förslag"
- Granska och godkänn förslaget

#### 👥 Steg 2: Perspektivinventering (3 min)
- Genomför samtal med din personal
- Ladda upp ljudfil ELLER spela in direkt
- Låt AI transkribera och analysera
- Välj perspektiv för fördjupning

#### 🔍 Steg 3: Fördjupad diskussion (3 min)
- Fördjupa diskussionen kring valda perspektiv
- Ladda upp ny ljudfil
- Låt AI dra slutsatser
- Godkänn slutsatserna

#### 📋 Steg 4: Handlingsplan (2 min)
- Låt AI skapa handlingsplan
- Granska och redigera
- Godkänn och exportera

## 5. Tips för bästa resultat

### 🎤 Ljudinspelning
- **Placera mikrofonen centralt** i rummet
- **Be deltagarna tala tydligt** och en i taget
- **Undvik bakgrundsljud** (stäng fönster, tysta telefoner)
- **Testa ljudkvaliteten** innan viktiga samtal

### 💬 Problembeskrivning
- **Var specifik** - undvik vaga formuleringar
- **Ge kontext** - varför är detta viktigt nu?
- **Inkludera exempel** om möjligt
- **Beskriv önskad utkomst**

### 🤖 AI-förslag
- **Granska alltid** AI:ns förslag innan godkännande
- **Redigera** för att passa er specifika situation
- **Komplettera** med lokal kunskap och erfarenhet
- **Spara utkast** regelbundet

## 6. Felsökning

### "OpenAI API-nyckel saknas"
```bash
# Kontrollera .env filen
cat .env
# Ska innehålla: OPENAI_API_KEY=sk-...
```

### "Kunde inte transkribera"
- Kontrollera att ljudfilen är i rätt format (WAV, MP3, M4A)
- Se till att filen inte är korrupt
- Kontrollera internetanslutning

### "Streamlit startar inte"
```bash
# Installera om beroenden
pip install --upgrade streamlit
pip install -r requirements.txt
```

## 7. Exempel på användning

### Scenario: Förbättra elevernas digitala kompetens

**Steg 1 - Problem:**
```
"Vi behöver diskutera hur vi kan förbättra elevernas digitala kompetens. 
Många lärare känner sig osäkra på hur de ska integrera digitala verktyg 
i undervisningen på ett meningsfullt sätt. Vi vill komma fram till 
konkreta åtgärder för kompetensutveckling."
```

**Steg 2 - Samtal:**
- Genomför 30-45 min samtal med lärargruppen
- Låt alla perspektiv komma fram
- Spela in eller anteckna

**Steg 3 - Fördjupning:**
- Fokusera på 2-3 viktigaste perspektiven
- Diskutera konkreta lösningar
- Sök konsensus

**Steg 4 - Handlingsplan:**
- AI skapar strukturerad plan
- Inkluderar ansvar, tidsramar, resurser
- Exportera för implementation

## 8. Nästa steg

Efter första sessionen:
- **Implementera** handlingsplanen
- **Följ upp** regelbundet
- **Dokumentera** lärdomar
- **Skapa nya sessioner** för andra frågor

## 🆘 Behöver hjälp?

- **README.md** - Fullständig dokumentation
- **GitHub Issues** - Rapportera problem
- **OpenAI Dokumentation** - API-hjälp

---

**Lycka till med dina strukturerade personalsamtal! 🗣️**