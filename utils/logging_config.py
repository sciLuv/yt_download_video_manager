import logging
import os

# Assurez-vous que le dossier de logs existe
os.makedirs("./config/logs", exist_ok=True)

# Configuration de base
logging.basicConfig(
    level=logging.DEBUG,  # Niveau de logging enrichi pour inclure les messages de débogage
    format="%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s",  # Ajout du fichier et de la ligne
    filename="./config/logs/app.log",  # Fichier de logs
    filemode="a",  # Ajouter au fichier existant
)

# Optionnel : Ajout d'un gestionnaire pour la console
console_handler = logging.StreamHandler()
console_handler.setLevel(logging.DEBUG)
console_formatter = logging.Formatter(
    "%(asctime)s - %(levelname)s - [%(filename)s:%(lineno)d] - %(message)s"
)
console_handler.setFormatter(console_formatter)

# Création de l'objet logger
logger = logging.getLogger("youtube_downloader")
logger.addHandler(console_handler)
