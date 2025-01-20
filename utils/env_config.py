import os
import shutil
from utils.logging_config import logger

# Fichiers de configuration
PORT="5000"
CONFIG_FOLDER_PATH = "./config/"
CHANNELS_LIST_PATH = os.path.join(CONFIG_FOLDER_PATH, "channels_list.txt")
LAST_CHECK_HOUR_PATH = os.path.join(CONFIG_FOLDER_PATH, "last_check_hour.txt")
LOGS_FOLDER_PATH = os.path.join(CONFIG_FOLDER_PATH, "logs")

# URL de base pour les vidéos YouTube
BASE_URL_YT_VIDEO = "https://www.youtube.com/watch?v="

DEFAULT_DOWNLOAD_FOLDER = "./download/"

def validate_and_create_paths():
    """Valide et crée les fichiers/dossiers nécessaires."""
    paths = [
        CONFIG_FOLDER_PATH,
        LOGS_FOLDER_PATH,
        CHANNELS_LIST_PATH,
        LAST_CHECK_HOUR_PATH,
    ]
    try:
        for path in paths:
            if path.endswith(".txt"):
                if not os.path.exists(path):
                    with open(path, 'w'):  # Crée un fichier vide
                        logger.info(f"Fichier créé : {path}")
            else:
                os.makedirs(path, exist_ok=True)
                logger.info(f"Dossier vérifié/créé : {path}")
    except Exception as e:
        logger.error(f"Erreur lors de la validation des chemins : {e}")
    return DEFAULT_DOWNLOAD_FOLDER

