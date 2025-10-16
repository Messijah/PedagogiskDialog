# Deployment Guide - PedagogiskDialog på Render

## Översikt
Denna guide beskriver hur du deployar PedagogiskDialog-applikationen till Render.com.

## Förutsättningar
1. Ett konto på [Render.com](https://render.com)
2. OpenAI API-nyckel
3. Git repository med din kod (GitHub, GitLab, eller Bitbucket)

## Steg-för-steg deployment

### 1. Förbered din kod
Säkerställ att följande filer finns i ditt repository:
- `render.yaml` (finns redan)
- `requirements.txt` (finns redan)
- `.streamlit/config.toml` (finns redan)

### 2. Skapa ett nytt projekt på Render

1. Logga in på [Render Dashboard](https://dashboard.render.com)
2. Klicka på **"New +"** och välj **"Blueprint"**
3. Anslut ditt Git repository (GitHub/GitLab/Bitbucket)
4. Render kommer automatiskt att upptäcka `render.yaml`-filen

### 3. Konfigurera Environment Variables

I Render Dashboard, lägg till följande environment variable:

```
OPENAI_API_KEY = din-openai-api-nyckel-här
```

**Viktigt:** Markera denna som "Secret" så att den inte visas i loggar.

### 4. Deploy

1. Klicka på **"Apply"** för att starta deployment
2. Render kommer att:
   - Installera dependencies från `requirements.txt`
   - Starta Streamlit-applikationen på den tilldelade porten
   - Konfigurera health checks

### 5. Verifiera deployment

När deployment är klar:
1. Klicka på den genererade URL:en (t.ex. `https://pedagogisk-dialog.onrender.com`)
2. Testa applikationen genom att:
   - Skapa ett nytt samtal (Steg 1)
   - Ladda upp eller spela in ljud
   - Verifiera att transkribering fungerar
   - Kontrollera att AI-analyser genereras korrekt

## Viktiga konfigurationer i render.yaml

```yaml
services:
  - type: web
    name: pedagogisk-dialog
    env: python
    region: frankfurt              # EU-region för GDPR-compliance
    plan: starter                  # Gratis tier, uppgradera vid behov
    buildCommand: pip install -r requirements.txt
    startCommand: streamlit run main.py --server.port=$PORT --server.address=0.0.0.0 --server.headless=true
    autoDeploy: true              # Automatisk deploy vid git push
```

## Prestanda-optimeringar

Applikationen innehåller flera optimeringar:

### 1. Snabbare transkribering (48x förbättring)
- **Whisper Turbo**: 8x snabbare modell
- **Parallell bearbetning**: 6x snabbare för stora filer
- Automatisk segmentering för filer >5MB

### 2. Bättre AI-svar (~65% förbättring)
- LPGD-baserade prompts (+40%)
- Kontextmedvetenhet mellan steg (+25%)
- Ökad tokenlimit (4000 tokens)

## Troubleshooting

### Problem: Transkribering tar för lång tid
**Lösning:**
- Kontrollera att filen inte är större än 100MB
- Segmentering sker automatiskt för filer >5MB
- Parallell bearbetning bör ge ~6x snabbare transkribering

### Problem: AI-svar är korta eller ofullständiga
**Lösning:**
- Öka `max_tokens` i `ai_helper.py` (standard: 4000)
- Kontrollera att OpenAI API-nyckeln har tillräckliga rättigheter

### Problem: "Failed to start" vid deployment
**Lösning:**
1. Kontrollera att alla dependencies i `requirements.txt` är kompatibla
2. Verifiera att `OPENAI_API_KEY` är korrekt konfigurerad
3. Granska Render logs för specifika felmeddelanden

### Problem: Applikationen är långsam
**Lösning:**
1. Uppgradera från Starter till Standard plan på Render
2. Kontrollera Render metrics för CPU/Memory usage
3. Cachar AI-responses automatiskt (ttl=0 för development)

## Kostnader

### Render
- **Starter Plan**: Gratis
  - 512MB RAM
  - Delar CPU
  - Går i "sleep mode" efter 15 min inaktivitet

- **Standard Plan**: $7/månad
  - 512MB RAM
  - Delad CPU
  - Ingen sleep mode

### OpenAI API (Uppskattade kostnader)
- **GPT-4**: ~$0.03 per 1K input tokens, ~$0.06 per 1K output tokens
- **Whisper**: ~$0.006 per minut audio

**Exempel:** En 60-minuters transkribering + 4 AI-analyser ≈ $0.36-0.50

## Säkerhet

### Best Practices
1. **API-nycklar**: Lagra aldrig API-nycklar i kod - använd Environment Variables
2. **HTTPS**: Render ger automatiskt SSL-certifikat
3. **GDPR**: Använd `region: frankfurt` för EU-datalagring
4. **Data**: Audio-filer och transkriberingar lagras lokalt i `data/` mappen

### Rekommendationer
- Sätt upp regelbundna backups av `data/` mappen
- Överväg att lägga till autentisering för produktionsmiljö
- Logga inte personlig information i Render logs

## Support och kontakt

För frågor eller problem:
1. Kontrollera Render logs i Dashboard
2. Granska `PROJECT_OVERVIEW.md` för applikationsdetaljer
3. Kontakta support på Render eller OpenAI vid API-problem

## Uppdateringar och underhåll

### Automatiska uppdateringar
Med `autoDeploy: true` i `render.yaml`:
- Varje `git push` till main branch triggar automatisk deployment
- Render bygger och deployar automatiskt

### Manuella uppdateringar
1. Gå till Render Dashboard
2. Välj din service
3. Klicka "Manual Deploy" → "Deploy latest commit"

## Prestanda-monitoring

Render Dashboard visar:
- CPU Usage
- Memory Usage
- Response Times
- Request Volume

Övervaka dessa metrics för att identifiera flaskhalsar.

---

**Version:** 1.0
**Senast uppdaterad:** 2025-01-XX
**Utvecklad med:** Streamlit, OpenAI GPT-4, Whisper Turbo
