import os
from utils.logging_config import logger
import shutil

def transfer_videos(old_folder, new_folder):
    """
    Transfère les vidéos du dossier précédent vers le nouveau dossier,
    puis supprime l'ancien dossier.
    """
    try:
        # Vérifie si l'ancien dossier existe
        if not os.path.exists(old_folder):
            logger.warning(f"L'ancien dossier {old_folder} n'existe pas.")
            return

        # Transfert les fichiers
        for root, _, files in os.walk(old_folder):
            relative_path = os.path.relpath(root, old_folder)
            target_folder = os.path.join(new_folder, relative_path)

            os.makedirs(target_folder, exist_ok=True)

            for file in files:
                old_file_path = os.path.join(root, file)
                new_file_path = os.path.join(target_folder, file)

                if not os.path.exists(new_file_path):  # Évite les doublons
                    shutil.move(old_file_path, new_file_path)
                    logger.info(f"Fichier déplacé : {old_file_path} -> {new_file_path}")
                else:
                    logger.warning(f"Fichier déjà présent : {new_file_path}")

        # Supprime l'ancien dossier
        shutil.rmtree(old_folder)
        logger.info(f"Ancien dossier supprimé : {old_folder}")

    except Exception as e:
        logger.error(f"Erreur lors du transfert des vidéos : {e}")


def verify_and_create_folder(chemin_dossier):
    """
    Vérifie si un dossier existe. Si non, le crée.
    
    Args:
        chemin_dossier (str): Chemin du dossier à vérifier ou créer.

    Returns:
        str: Message indiquant si le dossier existait déjà ou a été créé.
    """
    try:
        if not os.path.exists(chemin_dossier):
            os.makedirs(chemin_dossier)
            logger.info(f"Dossier créé : {chemin_dossier}")
            return True
        else:
            logger.info(f"Dossier existant : {chemin_dossier}")
            return True
    except PermissionError:
        logger.error(f"Erreur : Permission refusée pour créer le dossier {chemin_dossier}")
        return False
    except Exception as e:
        logger.info(f"Une erreur inattendue s'est produite : {e}")
        return False


# verify if the file of channels list exist or not
def verify_file_existence(file):
    if os.path.exists(file):
        logger.info(f"Le fichier {file} existe.")
    else:
        logger.info(f"Le fichier {file} n'existe pas.")
        with open(file, 'w'):
            logger.info(f"Le fichier {file} est crée.")
            pass

def delete_file(folder):
    # Parcours récursif du dossier
    for racine, _, files in os.walk(folder):
        for file in files:
            # Vérifie si "f303" ou "f251" est dans le nom du fichier
            if 'f303' in file or 'f251' in file:
                path_file = os.path.join(racine, file)
                try:
                    # Suppression du fichier
                    os.remove(path_file)
                    logger.info(f"Fichier supprimé: {path_file}")
                except Exception as e:
                    logger.error(f"Erreur lors de la suppression de {path_file}: {e}")

def read_file(file_path):
    try:
        with open(file_path, 'r', encoding='utf-8') as file:
            content = ''.join(file)  
        return content
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du fichier {file_path}: {e}")
        return None

def get_download_folder():
    """Retourne le chemin du dossier de téléchargement défini dans un fichier."""
    try:
        with open('./config/video_folder.txt', 'r') as file:
            folder_path = file.read().strip()
            return folder_path if folder_path else './download'
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du fichier de configuration : {e}")
        return './download'

def channel_folder_exists(channel_title):
    """Vérifie si un dossier au nom de la chaîne existe dans le dossier de téléchargement."""
    sanitized_title = channel_title.replace(" ", "_")  # Remplace les espaces par des underscores
    channel_folder = os.path.join(get_download_folder(), sanitized_title)
    return os.path.isdir(channel_folder)