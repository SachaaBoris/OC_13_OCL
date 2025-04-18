FROM python:3.10-slim

# Définir le répertoire de travail
WORKDIR /app

# Définir les variables d'environnement
ENV PYTHONDONTWRITEBYTECODE 1
ENV PYTHONUNBUFFERED 1
ENV DEBUG False

# Installer les dépendances
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt --progress-bar off

# Copier le code source
COPY . .

# Collecter les fichiers statiques
RUN python manage.py collectstatic --noinput
RUN ls -la /app/staticfiles/

# Exposer le port
EXPOSE 8000

# Commande de démarrage
#CMD ["gunicorn", "--bind", "0.0.0.0:8000", "--log-level=debug", "oc_lettings_site.wsgi:application"]
CMD ["gunicorn", "--config", "gunicorn.conf.py"]