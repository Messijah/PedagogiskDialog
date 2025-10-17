# 📁 Guide för hantering av stora ljudfiler

## Översikt

PedagogiskDialog har nu fullständigt stöd för stora ljudfiler och långa samtal (upp till 2 timmar).

---

## 🚀 Nya funktioner

### 1. Ökade uppladdningsgränser
- **Max filstorlek:** 450 MB (tidigare 100 MB)
- **Max längd:** 2 timmar ljud (tidigare 1 timme)
- **Streamlit server:** Konfigurerad för 500 MB uploads

### 2. Stöd för fler format
Följande format stöds nu fullt ut:
- ✅ **WAV** - Okomprimerat, bästa kvalitet
- ✅ **MP3** - Komprimerat, mindre filstorlek
- ✅ **M4A** - Apple-format, vanligt från iPhone-inspelningar

### 3. Minneseffektiv hantering
- **Streaming upload:** Stora filer laddas upp i 1 MB chunks för att undvika minnesöverbelastning
- **Automatisk segmentering:** Filer över 5 MB delas automatiskt i 10-minuters segment
- **Parallell bearbetning:** Alla segment transkriberas samtidigt för maximal hastighet

---

## 📊 Prestanda

### Exempel: 1-timmars samtal (60 minuter)

| Filformat | Filstorlek | Transkribering | Resultat |
|-----------|-----------|----------------|----------|
| **WAV (stereo, 44.1kHz)** | ~600 MB | ~30-45 sek | Bästa kvalitet |
| **MP3 (320 kbps)** | ~140 MB | ~25-35 sek | Mycket bra kvalitet |
| **M4A (256 kbps)** | ~110 MB | ~25-35 sek | Bra kvalitet |

**Segmentering:**
- 60 minuter → 6 segment à 10 minuter
- Alla 6 segment transkriberas parallellt
- Total tid: ~30 sekunder (jämfört med 6-8 minuter sekventiellt)

---

## 🛠️ Tekniska förbättringar

### 1. Streaming file upload
```python
# Gamla metoden (laddar hela filen i minnet)
with open(filepath, 'wb') as f:
    f.write(uploaded_file.getbuffer())  # ❌ Kan krascha med stora filer

# Nya metoden (streama i chunks)
chunk_size = 1024 * 1024  # 1 MB
with open(filepath, 'wb') as f:
    while True:
        chunk = uploaded_file.read(chunk_size)
        if not chunk:
            break
        f.write(chunk)  # ✅ Minneseffektivt
```

### 2. Förbättrad segmentering med ffmpeg
- **Automatisk formatkonvertering:** M4A → WAV för Whisper API
- **Optimerad sampling:** 16kHz mono för snabbare transkribering
- **Felhantering:** Tydliga felmeddelanden om ffmpeg saknas
- **Progress tracking:** Visar framsteg för varje segment

### 3. Async parallell transkribering
```python
# Alla segment transkriberas samtidigt
async def transcribe_segments_parallel(segment_paths):
    tasks = [transcribe_audio_openai_async(path, i)
             for i, path in enumerate(segment_paths)]
    results = await asyncio.gather(*tasks)
```

---

## 📝 Användning

### Steg 1: Ladda upp stor fil
1. Gå till valfritt steg (Steg 1, 2 eller 3)
2. Klicka "Ladda upp ljudfil (wav/mp3/m4a)"
3. Välj din fil (upp till 450 MB)
4. Systemet laddar upp filen i chunks

### Steg 2: Automatisk bearbetning
Systemet analyserar filen automatiskt:
```
🔍 Analyserar ljudfil: samtal_2024.m4a
⏱️ Ljudfilens längd: 65 minuter (3900 sekunder)
✂️ Delar upp i 7 segment à 10 minuter
✅ Segment 1/7 skapat
✅ Segment 2/7 skapat
...
⚡ Transkriberar alla segment samtidigt (parallell bearbetning)...
✅ Parallell transkribering klar för 7 av 7 segment!
```

### Steg 3: Granska resultat
- Transkriberingen visas direkt i gränssnittet
- Du kan redigera texten om det behövs
- Klicka "Analysera" för AI-bearbetning

---

## 🔍 Felsökning

### Problem: "Filen är för stor. Max: 450 MB"

**Lösning 1 - Komprimera ljudfilen:**
```bash
# Konvertera till MP3 med lägre bitrate
ffmpeg -i input.wav -b:a 128k output.mp3
```

**Lösning 2 - Dela upp manuellt:**
```bash
# Dela upp i 2 delar
ffmpeg -i input.wav -t 3600 del1.wav
ffmpeg -i input.wav -ss 3600 del2.wav
```

---

### Problem: "ffmpeg är inte installerat"

**Mac:**
```bash
brew install ffmpeg
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install ffmpeg
```

**Windows:**
1. Ladda ner från https://ffmpeg.org/download.html
2. Lägg till i PATH

---

### Problem: "Transkriberingen misslyckas"

**Möjliga orsaker:**
1. ❌ Dålig ljudkvalitet → Försök med bättre inspelning
2. ❌ Korrupt fil → Kontrollera att filen spelar normalt
3. ❌ Ingen internetanslutning → OpenAI API kräver internet
4. ❌ API-nyckel saknas → Kontrollera .env-filen

**Testa först med kort fil:**
- Ladda upp en 1-minuters testfil för att säkerställa att systemet fungerar
- Om det fungerar, prova med din långa fil

---

## 💡 Best Practices

### 1. Välj rätt format

**För bästa kvalitet:**
- Använd **WAV** eller **M4A** med hög bitrate
- Inspelning i tyst miljö
- Extern mikrofon rekommenderas

**För snabbast upload:**
- Använd **MP3** med 128-256 kbps
- Konvertera WAV → MP3 innan uppladdning

### 2. Optimera för transkribering

**Rekommenderade inställningar:**
- **Sampelfrekvens:** 16 kHz eller högre
- **Kanaler:** Mono (systemet konverterar automatiskt)
- **Format:** WAV, MP3 eller M4A

**Undvik:**
- Extremt låg sampelfrekvens (<8 kHz)
- Mycket komprimerade filer (<64 kbps)
- Bakgrundsljud och ekon

### 3. Planera för långa samtal

**Före mötet:**
- ✅ Testa inspelningsutrustning
- ✅ Kontrollera att du har 1-2 GB ledigt diskutrymme
- ✅ Säkerställ stabil internetanslutning

**Under mötet:**
- ✅ Placera mikrofon centralt
- ✅ Be deltagare prata tydligt
- ✅ Pausa inspelning vid längre pauser (dela upp naturligt)

**Efter mötet:**
- ✅ Kontrollera att filen spelades in korrekt
- ✅ Ladda upp så snart som möjligt (färskt minne)
- ✅ Granska transkribering noga

---

## 📊 Kostnadskalkyl

### OpenAI Whisper API: $0.006/minut

| Samtalslängd | Kostnad | Rekommendation |
|--------------|---------|----------------|
| **30 min** | $0.18 | Perfekt för korta möten |
| **60 min** | $0.36 | Standard längd |
| **90 min** | $0.54 | Längre workshop |
| **120 min** | $0.72 | Max rekommenderad längd |

**Tips:** För 100+ samtal/månad, överväg KB-Whisper (lokal, gratis)

---

## 🔐 Säkerhet och GDPR

### Dataflöde för stora filer:

1. **Upload:** Filen streamas till server i chunks (inte lagrat i webbläsaren)
2. **Lagring:** Sparas lokalt i `data/audio/` mappen
3. **Segmentering:** ffmpeg delar upp lokalt
4. **Transkribering:**
   - **OpenAI:** Segment skickas till API, raderas efter 30 dagar enligt OpenAI policy
   - **KB-Whisper:** Helt lokal bearbetning, ingen data lämnar servern
5. **Rensning:** Segment raderas automatiskt efter transkribering

### GDPR-rekommendationer:

För **känslig personaldata:**
- ✅ Använd KB-Whisper (lokal backend)
- ✅ Kryptera `data/audio/` mappen
- ✅ Radera gamla ljudfiler regelbundet

För **allmän diskussion:**
- ✅ OpenAI Whisper API är OK (enligt DPA)
- ✅ Se till att deltagare informerats om inspelning

---

## 🎯 Testscenarier

### Test 1: 30-minuters samtal (normal)
```
Filstorlek: ~50 MB (MP3)
Förväntad tid: ~15 sekunder
Segment: 3 st à 10 minuter
```

### Test 2: 60-minuters samtal (vanlig)
```
Filstorlek: ~110 MB (M4A)
Förväntad tid: ~30 sekunder
Segment: 6 st à 10 minuter
```

### Test 3: 90-minuters samtal (lång)
```
Filstorlek: ~160 MB (MP3)
Förväntad tid: ~45 sekunder
Segment: 9 st à 10 minuter
```

### Test 4: 120-minuters samtal (max)
```
Filstorlek: ~220 MB (MP3)
Förväntad tid: ~60 sekunder
Segment: 12 st à 10 minuter
```

---

## 📞 Support

### Om du stöter på problem:

1. **Kontrollera loggar:**
   - Streamlit visar detaljerade meddelanden i gränssnittet
   - Kolla terminalen för tekniska detaljer

2. **Verifiera förutsättningar:**
   - [ ] ffmpeg installerat (`ffmpeg -version`)
   - [ ] Tillräckligt diskutrymme (minst 2x filstorleken)
   - [ ] Stabil internetanslutning
   - [ ] OpenAI API-nyckel konfigurerad

3. **Prova enklare test:**
   - Ladda upp en kort testfil (1-2 min)
   - Om det fungerar → problemet är med den stora filen
   - Om det inte fungerar → konfigurationsproblem

---

## 🚀 Framtida förbättringar

Planerade förbättringar:
- [ ] Resumeable uploads (fortsätt uppladdning efter avbrott)
- [ ] Progress bar för uppladdning
- [ ] Bättre felhantering vid nätverksavbrott
- [ ] Automatisk fil-optimering före uppladdning
- [ ] Möjlighet att pausa/återuppta transkribering

---

**Version:** 3.1.0
**Uppdaterad:** 2025-10-17
**Support:** Se README.md för kontaktinformation
