FROM python:3.11-slim

# Installera ffmpeg och andra system dependencies
RUN apt-get update && apt-get install -y \
    ffmpeg \
    && rm -rf /var/lib/apt/lists/*

# Skapa arbets-directory
WORKDIR /app

# Kopiera requirements först för bättre caching
COPY requirements.txt .

# Installera Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Kopiera resten av applikationen
COPY . .

# Exponera port
EXPOSE 8501

# Hälsokontroll
HEALTHCHECK CMD curl --fail http://localhost:8501/_stcore/health || exit 1

# Starta Streamlit
CMD ["streamlit", "run", "main.py", "--server.port=8501", "--server.address=0.0.0.0", "--server.headless=true"]
