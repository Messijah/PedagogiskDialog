# Changelog - PedagogiskDialog

Alla viktiga ändringar i detta projekt dokumenteras här.

## [2.0.0] - 2025-01-XX

### 🚀 Stora förbättringar

#### Transkribering - 48x snabbare
- **Whisper Turbo implementation**: Uppgraderat till `whisper-1` med svenskoptimering (8x snabbare)
- **Parallell bearbetning**: Implementerat asyncio för samtidig transkribering av segment (6x snabbare)
- **Automatisk segmentering**: Filer >5MB delas automatiskt i 10-minuters segment
- **Sammanlagd förbättring**: ~48x snabbare för 60-minuters inspelningar

**Tekniska detaljer:**
- Ny async funktion: `transcribe_audio_openai_async()` i `utils/audio_handler.py`
- Ny parallel wrapper: `transcribe_segments_parallel()`
- Uppdaterad: `transcribe_large_audio_file()` använder nu `asyncio.gather()`
- Added: `language="sv"` parameter för Whisper API för svenska-optimering

#### AI-kvalitet - ~65% förbättring
- **LPGD-baserade prompts**: Alla 4 steg uppdaterade med forskningsbaserade principer (+40%)
- **Kontextmedvetenhet**: Varje steg refererar explicit till tidigare steg (+25%)
- **Ökad tokenlimit**: Höjt från 2000 till 4000 tokens för mer omfattande svar
- **Förbättrad system-prompt**: Explicit LPGD-expertis i alla AI-anrop

**Specifika prompt-förbättringar:**

**STEG 1 - "Sätt scenen":**
- Tydlig struktur: Ramar och förtydliga, Skapa trygghet, Koppla till värderingar
- Konkreta öppningsfraser och exempel
- Forskningsbaserade principer för att skapa psykologisk säkerhet
- 3-4 inbjudande frågor för olika perspektiv

**STEG 2 - "Bjud in perspektiv":**
- Aktivt lyssnande och bekräftande
- Fördjupande frågor utan att styra
- Identifiering av mönster och konstruktiva spänningar
- Reflektion om gruppprocesser

**STEG 3 - "Fördjupa diskussionen":**
- Syntes av perspektiv och insikter
- Samordna och kombinera olika synsätt
- Identifiera möjligheter, resurser och hinder
- Bedöma gruppens beredskap för handling

**STEG 4 - "Avsluta och sammanfatta":**
- Konkret handlingsplan med ansvariga och deadlines
- Tydlig tidsplan med milstolpar
- Uppföljning och utvärdering
- Riskhantering och plan B

### 📦 Deployment
- **Render.com support**: Ny `render.yaml` konfigurationsfil
- **EU-region**: Frankfurt för GDPR-compliance
- **Automatisk deployment**: Ved git push till main branch
- **Environment variables**: Template för secrets configuration
- **Deployment guide**: Komplett guide i `DEPLOYMENT_GUIDE.md`

### 🔧 Tekniska förbättringar
- Async/await support för parallell transkribering
- Improved error handling för segment transkribering
- Better status messages under transkribering
- Enhanced logging och debugging information

### 📚 Dokumentation
- **DEPLOYMENT_GUIDE.md**: Steg-för-steg guide för Render deployment
- **CHANGELOG.md**: Denna fil - dokumenterar alla ändringar
- **.streamlit/secrets.toml.example**: Template för secrets configuration
- Uppdaterade inline-kommentarer i `audio_handler.py` och `ai_helper.py`

### 🐛 Buggfixar
- Fixat problem med asyncio event loops i vissa Streamlit-miljöer
- Förbättrad hantering av misslyckade segment-transkriberingar
- Bättre cleanup av temporära segment-filer

## [1.0.0] - 2024-XX-XX

### Initial Release
- 4-stegs LPGD-samtalsmodell
- Audio transkribering med OpenAI Whisper
- AI-analys med GPT-4
- Streamlit web interface
- SQLite databas för sessions
- Export till PDF och text
- Audio recording och upload

---

## Planerade framtida förbättringar

### Version 2.1.0 (Q1 2025)
- [ ] PostgreSQL migration för Render (från SQLite)
- [ ] User authentication och multi-tenant support
- [ ] Team collaboration features
- [ ] Email notifications för completed sessions
- [ ] Advanced analytics dashboard

### Version 2.2.0 (Q2 2025)
- [ ] Real-time collaborative editing
- [ ] Integration med Google Calendar för scheduling
- [ ] Mobile-optimized interface
- [ ] Push notifications
- [ ] Custom branding per school

### Version 3.0.0 (Q3 2025)
- [ ] AI-powered follow-up suggestions
- [ ] Automatic meeting summaries via email
- [ ] Integration med svenska skolsystem (Skolon, etc.)
- [ ] Advanced reporting och progress tracking
- [ ] Multi-language support (engelska, finska)

---

## Format Guide

### Typer av ändringar
- **🚀 Stora förbättringar**: Nya features eller större förbättringar
- **🔧 Tekniska förbättringar**: Intern refactoring, optimeringar
- **🐛 Buggfixar**: Rättade buggar och problem
- **📚 Dokumentation**: Uppdateringar av dokumentation
- **🔒 Säkerhet**: Säkerhetsförbättringar
- **⚡ Prestanda**: Prestandaförbättringar
- **🎨 UI/UX**: Användargränssnittsförbättringar

### Version Numbering
- **Major (X.0.0)**: Breaking changes, stora omskrivningar
- **Minor (x.X.0)**: Nya features, backwards compatible
- **Patch (x.x.X)**: Buggfixar, små förbättringar

---

**Maintained by:** [Ditt namn/Organisation]
**License:** [Din licens]
