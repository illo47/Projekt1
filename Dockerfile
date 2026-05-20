FROM mcr.microsoft.com/playwright/python:v1.44.0-jammy

# Arbeitsverzeichnis
WORKDIR /app

# Requirements installieren
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Projektdateien kopieren
COPY . .

# Playwright Browser installieren
RUN playwright install --with-deps chromium

# Startkommando
CMD ["python", "fs2.py"]
