# 🚀 SamtalsBot - Streamlit Cloud Setup

## Snabb Setup för Streamlit Cloud

### 1. Ladda upp till GitHub
- Skapa ett **privat** GitHub repository
- Ladda upp alla filer från SamtalsBot-mappen

### 2. Streamlit Cloud
1. Gå till [share.streamlit.io](https://share.streamlit.io)
2. Logga in med GitHub
3. Klicka "New app"
4. Välj ditt SamtalsBot repository
5. Main file: `main.py`

### 3. Lägg till API-nyckel som Secret
I Streamlit Cloud under "Advanced settings" → "Secrets":

```toml
OPENAI_API_KEY = "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"
```

### 4. Deploy
Klicka "Deploy" och vänta några minuter.

## Viktiga filer för Streamlit Cloud:
- ✅ `main.py` (huvudfil)
- ✅ `requirements.txt` (beroenden)
- ✅ `pages/` (alla 4 steg)
- ✅ `utils/` (hjälpfunktioner)

Applikationen kommer att vara tillgänglig på din Streamlit Cloud URL!