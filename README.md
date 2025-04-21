# Résumé

<p align="center"><img src="https://github.com/SachaaBoris/OC_13_OCL/blob/main/static/assets/img/logo.png" width="273"/></p>
Site web d'Orange County Lettings


## Développement local

### Prérequis

- Compte GitHub avec accès en lecture à ce repository
- Git CLI
- SQLite3 CLI
- Interpréteur Python, version 3.6 ou supérieure

Dans le reste de la documentation sur le développement local, il est supposé que la commande `python` de votre OS shell exécute l'interpréteur Python ci-dessus (à moins qu'un environnement virtuel ne soit activé).

### macOS / Linux

#### Cloner le repository

- `cd /path/to/put/project/in`
- `git clone https://github.com/OpenClassrooms-Student-Center/Python-OC-Lettings-FR.git`

#### Créer l'environnement virtuel

- `cd /path/to/Python-OC-Lettings-FR`
- `python -m venv venv`
- `apt-get install python3-venv` (Si l'étape précédente comporte des erreurs avec un paquet non trouvé sur Ubuntu)
- Activer l'environnement `source venv/bin/activate`
- Confirmer que la commande `python` exécute l'interpréteur Python dans l'environnement virtuel
`which python`
- Confirmer que la version de l'interpréteur Python est la version 3.6 ou supérieure `python --version`
- Confirmer que la commande `pip` exécute l'exécutable pip dans l'environnement virtuel, `which pip`
- Pour désactiver l'environnement, `deactivate`

#### Exécuter le site

- `cd /path/to/Python-OC-Lettings-FR`
- `source venv/bin/activate`
- `pip install --requirement requirements.txt`
- Créer un fichier `.env` pour y indiquer :
```
SECRET_KEY=<la SECRET_KEY de votre projet Django>
SENTRY_DSN=<le lien vers votre projet Sentry>
DEBUG=True
```
- `python manage.py runserver`
- Aller sur `http://localhost:8000` dans un navigateur.
- Confirmer que le site fonctionne et qu'il est possible de naviguer (vous devriez voir plusieurs profils et locations).

#### Linting

- `cd /path/to/Python-OC-Lettings-FR`
- `source venv/bin/activate`
- `flake8`

#### Tests unitaires

- `cd /path/to/Python-OC-Lettings-FR`
- `source venv/bin/activate`
- `pytest`

#### Base de données

- `cd /path/to/Python-OC-Lettings-FR`
- Ouvrir une session shell `sqlite3`
- Se connecter à la base de données `.open oc-lettings-site.sqlite3`
- Afficher les tables dans la base de données `.tables`
- Afficher les colonnes dans le tableau des profils, `pragma table_info(Python-OC-Lettings-FR_profile);`
- Lancer une requête sur la table des profils, `select user_id, favorite_city from Python-OC-Lettings-FR_profile where favorite_city like 'B%';`
- `.quit` pour quitter

#### Panel d'administration

- Aller sur `http://localhost:8000/admin`
- Connectez-vous avec l'utilisateur `admin`, mot de passe `Abc1234!`

### Windows

Utilisation de PowerShell, comme ci-dessus sauf :

- Pour activer l'environnement virtuel, `.\venv\Scripts\Activate.ps1`
- Remplacer `which <my-command>` par `(Get-Command <my-command>).Path`

### Monitoring Sentry

Sentry est une plateforme qui signale automatiquement les éventuels bugs et exceptions du projet. Il permet également la surveillance des performances.

- Créer un compte [Sentry](https://sentry.io/signup/?original_referrer=https%3A%2F%2Fdocs.sentry.io%2F)
- Créer un projet avec la plateforme `Django`
- Récupérer la clé dsn et l'intégrer dans votre fichier .env
`SENTRY_DSN=<la clé dsn de votre projet Sentry>`
- Se connecter sur votre compte Sentry pour visualiser les logs récupérés 
  par Sentry

### Docker local

Docker est une plateforme sous linux permettant de lancer des applications en 
utilisant des conteneurs logiciels.

- Créer un compte [DockerHub](https://hub.docker.com/)
- Installer Docker pour [Windows](https://docs.docker.com/desktop/install/windows-install/) ou pour [Mac](https://docs.docker.com/desktop/install/mac-install/)
- Récupérer l'image docker pour exécuter l'application en local, `docker pull dockerhub-username/oc-lettings:latest`
- S'assurer que le serveur n'est pas déjà en cours d'exécution avec `docker container rm -f oc13-ocl` *Optionnel*
- Lancer le serveur avec la commande `docker run <img>`
```
docker run --name oc13-ocl -p 8000:8000 \
  -e SECRET_KEY='DJANGO_SECRETKEY' \
  -e SENTRY_DSN='LINK_SENTRY' \
  -e CSRF_TRUSTED_ORIGINS='http://localhost:8000 http://127.0.0.1:8000 http://192.168.99.100:8000' \
  oc-lettings:latest
```
- Pour arrêter un serveur : `docker stop <container_id_or_name>` ou `ctrl+c`
- Pour supprimer un container : `docker container rm -f oc13-ocl`
- Pour supprimer une image : `docker image rm -f oc13-ocl`

## Production

### DockerHub

DockerHub est une plateforme d'hébergement d'images Docker sur le cloud.

- Créer un compte [DockerHub](https://hub.docker.com/#)
- Générer un token depuis votre compte dockerhub
- Noter votre token et votre username précieusement

### Render

Render est un webservice de déploiement et de rendu de site internet.

- Créer un compte [Render](https://dashboard.render.com/#)
- Cliquer sur "Nouveau" puis "Web Service"
- Sélectionner Docker, Image et insérez votre docker:img
- Générer une clé API depuis votre "Account Settings"
- Noter votre clé et votre srv-ID précieusement
- Désactiver le déploiement automatique à chaque commit

### Déploiement

Un pipeline CI/CD est mis en place pour le développement et le déploiement de cette application. A chaque push sur la branche "main" du repository GitHub, un travail de linting et de tests est lancé. Ensuite, si ce dernier est validé, une image Docker de l'application est construite, pushée sur DockerHub puis déployée sur Render.

Prérequis pour déployer :
- Avoir configuré son compte DockerHub
- Avoir configuré son compte Render
- Avoir configuré les clés secrètes GitHub actions
```
DOCKERHUB_USERNAME - DOCKERHUB_TOKEN
RENDER_SERVICE_ID - RENDER_API_KEY
SECRET_KEY - SENTRY_KEY
```
- Avoir pushé le repository sur son propre compte GitHub


## Documentation
  
[Read The Docs](https://oc-13-ocl.readthedocs.io/en/latest/#)
  
  
---  
  
[![CC BY 4.0][cc-by-shield]][cc-by]  
  
This work is licensed under a [Creative Commons Attribution 4.0 International License][cc-by].  
  
[cc-by]: http://creativecommons.org/licenses/by/4.0/  
[cc-by-shield]: https://img.shields.io/badge/License-CC%20BY%204.0-lightgrey.svg  