FROM python:3.12-slim

# Empêche apt de poser des questions interactives
ENV DEBIAN_FRONTEND=noninteractive

# Installer psycopg2 et dépendances
RUN apt-get update \
    && apt-get install -y --no-install-recommends \
       gcc \
       libpq-dev \
    && apt-get clean \
    && rm -rf /var/lib/apt/lists/*

WORKDIR /app

# Copier requirements et installer
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le projet
COPY . .

EXPOSE 8080 8000

CMD ["python3", "-m", "server.server"]
