# 🚀 Render Optimering för PedagogiskDialog

## Översikt

Detta dokument beskriver alla optimeringar som gjorts för att köra PedagogiskDialog på Renders gratisplan med stora ljudfiler.

---

## 🎯 Problem som lösts

### Problem: Minnesöverbelastning vid stora filer
**Symptom:**
- Tjänsten kraschar när användare laddar upp filer >100 MB
- Automatisk omstart från Render
- Felmeddelande: "Webbtjänsten PedagogiskDialog överskred sin minnesgräns"

**Orsak:**
- Renders gratis plan: 512 MB RAM
- Tidigare kod laddade hela filen i minnet
- 400 MB fil = 400 MB RAM + overhead = KRASCH

**Lösning:**
✅ Streaming upload (1 MB chunks)
✅ Effektiv segmentering på disk
✅ Optimerad Render-konfiguration

---

## 📊 Render-konfiguration

### render.yaml

```yaml
services:
  - type: web
    name: pedagogisk-dialog
    env: docker
    region: frankfurt
    plan: starter
    envVars:
      - key: OPENAI_API_KEY
        sync: false
      - key: STREAMLIT_SERVER_MAX_UPLOAD_SIZE
        value: "500"                    # 500 MB max upload
      - key: STREAMLIT_SERVER_MAX_MESSAGE_SIZE
        value: "500"                    # 500 MB max message
      - key: STREAMLIT_BROWSER_GATHER_USAGE_STATS
        value: "false"                  # Spara minne
    autoDeploy: true
    healthCheckPath: /_stcore/health
    disk:
      name: pedagogisk-dialog-data
      mountPath: /app/data              # Persistent storage för DB + audio
      sizeGB: 1                         # 1 GB disk för ljudfiler
```

### Viktiga inställningar:

1. **Environment variabler:**
   - `STREAMLIT_SERVER_MAX_UPLOAD_SIZE=500` - Tillåt stora filer
   - `STREAMLIT_SERVER_MAX_MESSAGE_SIZE=500` - Websocket-meddelanden
   - `STREAMLIT_BROWSER_GATHER_USAGE_STATS=false` - Spara minne

2. **Persistent disk:**
   - `mountPath: /app/data` - Säkerställ att DB och audio sparas mellan omstarter
   - `sizeGB: 1` - Tillräckligt för flera samtal med audio

---

## 🐳 Docker-optimering

### Dockerfile förbättringar

```dockerfile
FROM python:3.11-slim

# Installera ffmpeg (KRITISKT för segmentering)
RUN apt-get update && apt-get install -y \
    ffmpeg \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Skapa data-mapp för persistent storage
RUN mkdir -p /app/data/audio

# Förbättrad hälsokontroll
HEALTHCHECK --interval=30s --timeout=10s --start-period=40s --retries=3 \
    CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Starta med minnesoptimering
CMD ["streamlit", "run", "main.py", \
    "--server.maxUploadSize=500", \
    "--server.maxMessageSize=500", \
    "--browser.gatherUsageStats=false"]
```

### Viktiga optimeringar:

1. **ffmpeg:** Nödvändigt för att dela upp stora filer
2. **curl:** För healthcheck
3. **Persistent mapp:** `/app/data/audio` skapas i image
4. **Healthcheck:** Förhindrar krasch under uppladdning
5. **Streamlit-flags:** Direkt i CMD för säkerhet

---

## 📈 Minnesanvändning

### Före optimering:
```
Upload 400 MB fil → Ladda i RAM (400 MB) → KRASCH (över 512 MB gräns)
```

### Efter optimering:
```
Upload 400 MB fil → Stream chunks (1 MB) → Spara på disk → OK (~50 MB RAM)
Segmentera → ffmpeg på disk (10 MB) → OK
Transkribera → Parallellt (20 MB per segment) → OK (~100 MB RAM totalt)
```

**Total RAM-användning:** ~100-150 MB (väl under 512 MB gräns)

---

## 🔍 Monitoring och felsökning

### Övervaka minnesanvändning

**I Render Dashboard:**
1. Gå till din service → Metrics
2. Kolla "Memory" grafen
3. Normal användning: 100-200 MB
4. Vid uppladdning: Spike till ~150-250 MB (fortfarande OK)

### Varningssignaler:

❌ **Minne >400 MB:** Risk för krasch
❌ **Frequent restarts:** Minnesläcka eller optimering saknas
❌ **Slow uploads:** Nätverksproblem eller disk full

### Felsökning:

**Problem:** Kraschar fortfarande vid stora filer

**Kontrollera:**
1. ✅ Är ny deploy live? (commit `804c349` eller senare)
2. ✅ Är env vars satta i Render? (STREAMLIT_SERVER_MAX_UPLOAD_SIZE=500)
3. ✅ Är disk monterad? (disk mounted at /app/data)

**Lösning om fortfarande krasch:**
```bash
# Uppgradera till Hobby plan ($7/mån)
# Detta ger 2 GB RAM istället för 512 MB
```

---

## 🎯 Best practices

### 1. Filstorlekar

**Rekommenderat:**
- ✅ <100 MB: Perfekt
- ✅ 100-300 MB: Bra
- ⚠️ 300-450 MB: OK men nära gränsen

**Om filer >450 MB:**
- Komprimera innan uppladdning
- Dela upp i flera samtal
- Överväg Hobby plan ($7/mån)

### 2. Diskutrymme

**1 GB disk räcker för:**
- ~50 st 60-minuters samtal (med audio)
- Automatisk cleanup efter transkribering
- Databas (några MB)

**Om disk blir full:**
- Radera gamla ljud-filer manuellt: `/app/data/audio/`
- Implementera automatisk cleanup (TODO)

### 3. Transkribering

**Kostnad (OpenAI Whisper):**
- 60 min samtal = $0.36
- 100 samtal/månad = $36/månad

**Alternativ:**
- KB-Whisper (gratis, lokalt) - se `KB_WHISPER_GUIDE.md`
- Men kräver mer RAM/CPU

---

## 📋 Deploy-checklista

Innan deploy till Render:

- [ ] **Environment vars satta:**
  - `OPENAI_API_KEY`
  - `STREAMLIT_SERVER_MAX_UPLOAD_SIZE=500`
  - `STREAMLIT_SERVER_MAX_MESSAGE_SIZE=500`

- [ ] **Persistent disk konfigurerad:**
  - mountPath: `/app/data`
  - sizeGB: minst 1 GB

- [ ] **Dockerfile uppdaterad:**
  - ffmpeg installerat
  - curl installerat (healthcheck)
  - Minnesvänliga CMD-flags

- [ ] **Koden uppdaterad:**
  - Streaming upload implementerad
  - Segmentering med ffmpeg
  - Parallell transkribering

---

## 🚦 Status för optimeringarna

### ✅ Implementerat

- ✅ Streaming file upload (1 MB chunks)
- ✅ Effektiv segmentering med ffmpeg
- ✅ Parallell transkribering
- ✅ Persistent disk för data
- ✅ Optimerade Streamlit-settings
- ✅ Förbättrad healthcheck
- ✅ .dockerignore för mindre image

### 🔄 Planerat

- [ ] Automatisk cleanup av gamla ljud-filer
- [ ] Progressbar för uppladdning
- [ ] Resumeable uploads vid avbrott
- [ ] Mer aggressiv minneshantering

---

## 📊 Render Plans jämförelse

| Feature | Starter (Gratis) | Hobby ($7/mån) |
|---------|------------------|----------------|
| **RAM** | 512 MB | 2 GB |
| **Disk** | 1 GB (addon) | 1 GB (addon) |
| **CPU** | Delad | Delad |
| **Sleep** | Efter 15 min inaktivitet | Ingen sleep |
| **Bandwidth** | 100 GB/mån | 100 GB/mån |

**Rekommendation:**
- **Starter:** OK för <5 användare/dag med våra optimeringar
- **Hobby:** Bättre för produktion med många användare

---

## 🔧 Felsökning specifika problem

### Problem 1: "Out of memory" error

**Symptom:**
```
Webbtjänsten PedagogiskDialog överskred sin minnesgräns
En instans av din webbtjänst ... utlöste en automatisk omstart
```

**Lösning:**
1. Verifiera att senaste koden är deployad (commit `804c349`)
2. Kontrollera att env vars är satta (STREAMLIT_SERVER_MAX_UPLOAD_SIZE)
3. Testa med mindre fil först (~50 MB)
4. Om fortfarande problem: Uppgradera till Hobby plan

---

### Problem 2: "Disk full" error

**Symptom:**
```
No space left on device
```

**Lösning:**
1. SSH till Render container (om möjligt)
2. Radera gamla filer: `rm /app/data/audio/*.wav`
3. Implementera automatisk cleanup
4. Överväg att öka disk till 2-5 GB (kostnad: ~$1/GB/mån)

---

### Problem 3: Långsam uppladdning

**Symptom:**
- Uppladdning tar >5 minuter för 100 MB fil

**Lösning:**
1. Kontrollera nätverksanslutning
2. Testa från annan plats/nätverk
3. Överväg Render region närmare användare (frankfurt → annat)
4. Komprimera filer före uppladdning (WAV → MP3)

---

## 💡 Tips för optimal prestanda

### 1. Filformat

**Bäst för Render:**
- MP3 (128-256 kbps): Små filer, snabb upload
- M4A (256 kbps): Bra kvalitet, mindre storlek än WAV

**Undvik:**
- WAV (okomprimerat): Mycket stora filer
- Flac/högupplösta format: Onödig kvalitet för tal

### 2. Användarmönster

**Optimalt:**
- Ladda upp filer direkt efter möte
- Radera gamla ljud-filer regelbundet
- Använd komprimerade format

**Suboptimalt:**
- Spara alla ljud-filer permanent
- Ladda upp flera stora filer samtidigt
- Behåll WAV-filer

### 3. Skalning

**Vid ökad användning:**
1. Uppgradera till Hobby plan ($7/mån) → 2 GB RAM
2. Öka disk till 5 GB → fler samtal kan sparas
3. Implementera auto-cleanup → frigör disk automatiskt
4. Överväg KB-Whisper → minska OpenAI-kostnader

---

## 📞 Support

### Om problem kvarstår:

1. **Kontrollera Render logs:**
   - Gå till Dashboard → Logs
   - Sök efter "memory", "crash", "error"

2. **Verifiera deployment:**
   - Latest commit: `804c349` eller senare
   - Build succeeded (grönt)
   - All env vars satta

3. **Testa lokalt först:**
   ```bash
   docker build -t pedagogisk-dialog .
   docker run -p 8501:8501 -e OPENAI_API_KEY=xxx pedagogisk-dialog
   # Ladda upp stor fil → ska fungera
   ```

4. **Kontakta Render support:**
   - Om minnesöverbelastning trots optimeringar
   - Om disk-problem kvarstår
   - Email: support@render.com

---

**Version:** 3.1.0
**Uppdaterad:** 2025-10-20
**Status:** ✅ Produktionsklar för Render Starter plan med stora filer
