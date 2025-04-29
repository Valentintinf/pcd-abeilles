# syntax=docker/dockerfile:1
FROM python:3.10-slim

WORKDIR /app

# Copier les requirements
COPY requirements.txt .

# Installer les dépendances
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le projet
COPY . .

# Par défaut, on ne lance rien ici (géré par docker-compose)
CMD ["echo", "Ready to run Flask/FastAPI"]
