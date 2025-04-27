FROM python:3.11-slim

WORKDIR /app

# Copier et installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copier tout le projet
COPY . .

# Copier la base SQLite pour db_api
COPY app.db /app/app.db

# Par défaut, on ne lance rien (géré par docker-compose)
CMD ["echo", "Ready for docker-compose"]