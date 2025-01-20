# YouTube Video Downloader & Manager

Ce projet permet de télécharger et de gérer automatiquement les vidéos YouTube des chaînes spécifiées. Le script fonctionne en tâche de fond pour vérifier les nouvelles vidéos grâce aux flux RSS des chaînes YouTube et utilise `yt_dlp` pour les téléchargements.

## Fonctionnalités

- Suivi des chaînes YouTube via flux RSS.
- Téléchargement automatique des nouvelles vidéos des chaines suivis.
- Téléchargement des vidéos 
- Gestion des fichiers téléchargés.


## Installation (linux)

1. Clonez le dépôt Git :
   ```bash
   git clone https://github.com/votre-utilisateur/yt_everyday_downloader.git
   cd yt_everyday_downloader

2. Lancez deploy.sh comme un programme et suivez les instructions 
3. pour relancer l'application ouvrir l'invite de commande à l'emplacement du projet et écrit `sudo python3 app.py` 


## Déploiement avec Docker

Ce projet inclut une configuration Docker pour simplifier son déploiement. Suivez les étapes ci-dessous pour exécuter le projet avec Docker.

### Prérequis

- [Docker](https://www.docker.com/get-started)
- [Docker Compose](https://docs.docker.com/compose/install/)

### Installation et Exécution

1. Construire l'image Docker et construire un conteneur :
   Depuis la racine du projet, exécutez la commande suivante :
   ```bash
   docker build -t youtube-downloader .
   docker-compose up
   ```

2. Accédez à l'application :
   Une fois le conteneur démarré, ouvrez un navigateur et accédez à :
   ```
   http://localhost:5000
   ```
3. Accès aux vidéos
   Le dossier contenant les vidéos téléchargés est disponible sur la machine hôte avec un bind mount disponible dans le dossier `download` à la racine du projet.



