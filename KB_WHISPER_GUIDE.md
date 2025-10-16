# 🇸🇪 KB-Whisper Integration Guide

## Översikt

Din PedagogiskDialog-applikation har nu stöd för **KBLab's Whisper-modeller** - svenska Whisper-modeller tränade på 50,000 timmar svensk data från Kungliga Biblioteket.

## 🎯 Varför KB-Whisper?

### Fördelar:
- ✅ **47% bättre WER** (Word Error Rate) för svenska jämfört med OpenAI Whisper
- ✅ **Gratis** - inga API-kostnader
- ✅ **Lokal körning** - ingen data skickas ut
- ✅ **GDPR-compliant** - all data stannar på din server
- ✅ **Tränad på svensk data** - bättre hantering av svenska dialekter och ord

### Nackdelar:
- ❌ Kräver lokal hårdvara (GPU rekommenderat för bästa prestanda)
- ❌ Större minnesbehov (2-16GB RAM/VRAM beroende på modell)
- ❌ Längre initial laddningstid första gången

---

## 🚀 Installation

### 1. Installera dependencies

```bash
# Installera KB-Whisper dependencies
pip install -r requirements.txt
```

Detta installerar:
- `transformers` - Hugging Face modellbibliotek
- `torch` - PyTorch för AI-modeller
- `accelerate` - Snabbare modellkörning
- `librosa` - Ljudbehandling
- `soundfile` - Ljudfilshantering

### 2. Konfigurera .env

Redigera din `.env` fil och lägg till:

```bash
# Byt från OpenAI till KB-Whisper
TRANSCRIPTION_BACKEND=kb-whisper

# Välj modellstorlek (tiny, base, small, medium, large)
KB_WHISPER_MODEL=medium

# Välj transkriberingsstil (default, subtitle, strict)
KB_WHISPER_STYLE=default
```

### 3. Testa installationen

```bash
# Starta applikationen
streamlit run main.py

# Ladda upp en ljudfil i Steg 1, 2 eller 3
# Du ska se meddelandet: "🇸🇪 Använder KB-Whisper (lokal svensk modell)"
```

---

## 📊 Modellval

KBLab tillhandahåller 5 olika modellstorlekar:

| Modell | Parametrar | RAM/VRAM | Hastighet | Kvalitet | Användningsfall |
|--------|-----------|----------|-----------|----------|-----------------|
| **tiny** | 57M | ~1GB | Snabbast | Lägst | Snabb prototyping |
| **base** | 99M | ~1.5GB | Mycket snabb | Ok | Utveckling/test |
| **small** | 0.3B | ~2GB | Snabb | Bra | Balans mellan hastighet och kvalitet |
| **medium** | 0.8B | ~5GB | Medel | Hög | **REKOMMENDERAT för produktion** |
| **large** | 2B | ~10GB | Långsam | Bäst | Högsta kvalitet, kräver GPU |

### Rekommendationer:

**För utveckling:**
```bash
KB_WHISPER_MODEL=small
```

**För produktion:**
```bash
KB_WHISPER_MODEL=medium
```

**För bästa kvalitet (om du har GPU):**
```bash
KB_WHISPER_MODEL=large
```

---

## 🎨 Transkriberingsstilar

KB-Whisper stöder 3 olika transkriberingsstilar:

### 1. Default (Rekommenderat)
```bash
KB_WHISPER_STYLE=default
```
Standard transkribering med balanserad noggrannhet.

### 2. Subtitle
```bash
KB_WHISPER_STYLE=subtitle
```
Mer komprimerad stil, bra för undertexter och sammanfattningar.

### 3. Strict
```bash
KB_WHISPER_STYLE=strict
```
Mer verbatim-lik transkribering, inkluderar fler fyllnadsord och pauser.

---

## 💻 Hårdvarukrav

### CPU-only (utan GPU):
- **RAM**: Minst 8GB (16GB rekommenderat)
- **Modeller**: tiny, base, small
- **Hastighet**: 1-2x realtid (60 min audio = 30-60 min transkribering)

### Med GPU (NVIDIA CUDA):
- **VRAM**: Minst 6GB (RTX 3060 eller bättre)
- **Modeller**: Alla (inklusive large)
- **Hastighet**: 10-20x realtid (60 min audio = 3-6 min transkribering)

### Kontrollera GPU:
```python
import torch
print(torch.cuda.is_available())  # True = GPU tillgänglig
```

---

## 🔄 Växla mellan OpenAI och KB-Whisper

Du kan enkelt växla mellan backends genom att ändra `.env`:

### Använd OpenAI Whisper (API):
```bash
TRANSCRIPTION_BACKEND=openai
```
- **Kostar**: $0.006/minut
- **Snabbt**: 8x snabbare än original Whisper
- **Enkelt**: Ingen lokal installation

### Använd KB-Whisper (Lokalt):
```bash
TRANSCRIPTION_BACKEND=kb-whisper
```
- **Gratis**: Inga API-kostnader
- **Bättre för svenska**: 47% bättre WER
- **GDPR**: All data stannar lokalt

---

## 📈 Prestandajämförelse

### 60-minuters ljudfil:

| Backend | Kostnad | Tid | Kvalitet (svenska) | GDPR |
|---------|---------|-----|-------------------|------|
| **OpenAI Whisper** | $0.36 | ~20-30 sek | Bra | ❌ Data skickas till OpenAI |
| **KB-Whisper (CPU, medium)** | Gratis | ~30-60 min | **Bättre** | ✅ Lokalt |
| **KB-Whisper (GPU, medium)** | Gratis | ~3-6 min | **Bättre** | ✅ Lokalt |
| **KB-Whisper (GPU, large)** | Gratis | ~6-12 min | **Bäst** | ✅ Lokalt |

---

## 🛠️ Felsökning

### Problem: "KB-Whisper dependencies saknas"

**Lösning:**
```bash
pip install transformers torch accelerate librosa soundfile
```

### Problem: "CUDA out of memory"

**Lösning 1 - Använd mindre modell:**
```bash
KB_WHISPER_MODEL=small  # Istället för medium/large
```

**Lösning 2 - Använd CPU:**
Modellen detekterar automatiskt om GPU saknas och använder CPU.

### Problem: Långsam transkribering på CPU

**Lösning 1 - Använd mindre modell:**
```bash
KB_WHISPER_MODEL=base  # Snabbast på CPU
```

**Lösning 2 - Byt till OpenAI Whisper för snabbhet:**
```bash
TRANSCRIPTION_BACKEND=openai
```

### Problem: Modellen laddar varje gång

**Detta är normalt!** Första gången laddar modellen ner (~1-5GB), sedan cachas den lokalt i `cache/` mappen.

För att rensa cache:
```bash
rm -rf cache/
```

---

## 📊 Kostnadsberäkning

### Scenario: 100 samtal/månad à 60 minuter

**Med OpenAI Whisper:**
- 100 samtal × 60 min × $0.006/min = **$36/månad**
- Årskostnad: **$432**

**Med KB-Whisper:**
- **$0/månad** (endast el för servern)
- Årskostnad: **$0**

**Break-even:**
Om du har >10 samtal/månad så är KB-Whisper mer ekonomiskt.

---

## 🎯 Best Practices

### 1. Utveckling:
```bash
TRANSCRIPTION_BACKEND=kb-whisper
KB_WHISPER_MODEL=small
KB_WHISPER_STYLE=default
```

### 2. Produktion (utan GPU):
```bash
TRANSCRIPTION_BACKEND=kb-whisper
KB_WHISPER_MODEL=medium
KB_WHISPER_STYLE=default
```

### 3. Produktion (med GPU):
```bash
TRANSCRIPTION_BACKEND=kb-whisper
KB_WHISPER_MODEL=large
KB_WHISPER_STYLE=default
```

### 4. Hybrid-approach:
Använd KB-Whisper för stora volymer, OpenAI för snabba tester:
```bash
# Produktion: KB-Whisper
TRANSCRIPTION_BACKEND=kb-whisper

# Demo/Test: OpenAI Whisper
TRANSCRIPTION_BACKEND=openai
```

---

## 🔐 GDPR och Datasäkerhet

### OpenAI Whisper:
- ❌ Data skickas till OpenAI servrar (USA)
- ❌ Kräver Data Processing Agreement
- ❌ Logarning i 30 dagar enligt OpenAI policy

### KB-Whisper:
- ✅ All data bearbetas lokalt
- ✅ Ingen data lämnar din server
- ✅ Fullt GDPR-compliant
- ✅ Perfekt för känslig personaldata

---

## 📚 Referenser

- **KBLab Whisper Models:** https://huggingface.co/KBLab
- **KBLab Blog:** https://kb-labb.github.io/posts/2025-03-07-welcome-KB-Whisper/
- **Original Whisper Paper:** https://arxiv.org/abs/2212.04356
- **Transformers Library:** https://huggingface.co/docs/transformers

---

## 🆘 Support

### Problem med KB-Whisper?

1. **Kolla att dependencies är installerade:**
```bash
pip show transformers torch accelerate librosa soundfile
```

2. **Testa med OpenAI Whisper istället:**
```bash
TRANSCRIPTION_BACKEND=openai
```

3. **Rapportera buggar:**
Skapa en issue med:
- OS och Python version
- GPU info (`nvidia-smi` eller "ingen GPU")
- Vald modell och stil
- Felmeddelande

---

**Version:** 3.0.0 (KB-Whisper integration)
**Datum:** 2025-10-16
**Utvecklad för:** Lunds kommun - Pedagogiskt Samtalsstöd
