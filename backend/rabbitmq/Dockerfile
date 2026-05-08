FROM python:3.9-slim

WORKDIR /app

# Installation des outils système nécessaires (comme psql)
RUN apt-get update && apt-get install -y postgresql-client && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .