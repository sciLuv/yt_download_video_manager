import os
import time
import pytz

import schedule
import time

from datetime import datetime
from dateutil import parser

from utils import env_config as config
from utils import folder_and_file_manager
from utils import web_utils
from utils.logging_config import logger
import threading

from utils.url_validation import is_valid_url

from concurrent.futures import ThreadPoolExecutor

verification_lock = threading.Lock()

# Constantes / Variables globales
CHANNELS_LIST_FILE = config.CHANNELS_LIST_PATH
LAST_CHECK_HOUR_FILE = config.LAST_CHECK_HOUR_PATH
DOWNLOAD_FOLDER = config.DEFAULT_DOWNLOAD_FOLDER
BASE_URL_YT_VIDEO = config.BASE_URL_YT_VIDEO
CONFIG_FOLDER_PATH = config.CONFIG_FOLDER_PATH

# Variables globales pour contrôler les intervalles
VIDEO_CHECK_INTERVAL = 0.1  # Intervalle entre les vérifications des vidéos (en heures)
LAST_CHECK_UPDATE_INTERVAL = 0.2  # Intervalle pour mettre à jour last_check_hour (en heures)


# Fuseau horaire utilisé pour l'horodatage
TIMEZONE = pytz.timezone("UTC")

def comparer_dates(date_reference: str, date_video: str) -> bool:
    """
    Compare deux dates au format ISO 8601 (e.g. "2021-07-01T12:00:00Z")
    et détermine si la date_video est postérieure à la date_reference.

    Args:
        date_reference (str): Date de dernière vérification.
        date_video (str): Date de publication de la vidéo.

    Returns:
        bool: True si date_video > date_reference (vidéo plus récente),
              False sinon.
    """
    try:
        # Nettoyage et parsing
        date_ref_obj = parser.isoparse(date_reference.strip())
        date_vid_obj = parser.isoparse(date_video.strip())

        # Comparaison
        if date_vid_obj > date_ref_obj:
            logger.info("Une nouvelle vidéo est disponible.")
            return True
        elif date_vid_obj < date_ref_obj:
            logger.info("Aucune nouvelle vidéo disponible (vidéo plus ancienne).")
            return False
        else:
            logger.info("Une vidéo est sortie exactement au même moment, on la considère comme nouvelle.")
            return True
    except ValueError as e:
        logger.error(f"Erreur lors de la comparaison des dates : {e}")
        return False

def search_last_video_upload(feed_url: str) -> list:

    if not is_valid_url(feed_url):
        logger.error(f"URL de flux RSS invalide : {feed_url}")
        return []
    
    """
    Récupère la liste des vidéos depuis un flux RSS/Atom YouTube au format XML.

    Args:
        feed_url (str): URL du flux RSS/Atom d'une chaîne YouTube.

    Returns:
        list: Liste de dictionnaires contenant 'video_id' et 'published_date'.
    """
    soup = web_utils.soup_xml(feed_url)
    entries = soup.find_all("entry")
    video_data_list = []

    for entry in entries:
        video_id_tag = entry.find("yt:videoId").text if entry.find("yt:videoId") else None
        published_date = entry.find("published").text if entry.find("published") else None

        # Ajout seulement si on a bien l'ID et la date
        if video_id_tag and published_date:
            video_data_list.append({
                "video_id": video_id_tag,
                "published_date": published_date
            })

    logger.info(f"Liste des vidéos récupérées : {video_data_list}")
    return video_data_list

def read_channel_list(fichier: str) -> list:
    """
    Lit la liste des chaînes à suivre depuis un fichier (chaque ligne contient 3 colonnes,
    séparées par '|-|': nom, url, qualité).

    Args:
        fichier (str): Chemin vers le fichier des chaînes (channels_list_file).

    Returns:
        list: Liste de dictionnaires { title, url, quality }.
    """
    yt_channel_array = []
    try:
        with open(fichier, 'r', encoding='utf-8') as f:
            for line in f:
                line = line.strip()
                if line:
                    nom, url, quality = line.split('|-|')
                    yt_channel_array.append({'title': nom, 'url': url, 'quality': quality})
    except FileNotFoundError:
        logger.error(f"Fichier introuvable : {fichier}")
    except Exception as e:
        logger.error(f"Erreur lors de la lecture du fichier {fichier} : {e}")
    return yt_channel_array

def last_check_hour() -> str:
    """
    Lit le contenu du fichier LAST_CHECK_HOUR_FILE (dernière vérification).

    Returns:
        str: Chaîne représentant la date/heure de la dernière vérification.
    """
    try:
        with open(LAST_CHECK_HOUR_FILE, 'r', encoding='utf-8') as fichier:
            return fichier.read().strip()
    except Exception as e:
        logger.error(f"Erreur lors de la lecture de {LAST_CHECK_HOUR_FILE} : {e}")
        return ""

def download_video(channel_title: str, channel_quality: str, video_id: str):
    """
    Télécharge une vidéo pour une chaîne donnée dans le dossier correspondant.

    Args:
        channel_title (str): Nom de la chaîne (utilisé pour créer le dossier).
        channel_quality (str): Qualité de la vidéo à télécharger (e.g., "bestvideo+bestaudio").
        video_id (str): ID de la vidéo à télécharger.
    """

    try:
        # Crée un sous-dossier pour la chaîne (en remplaçant les espaces par des underscores)
        channel_folder = os.path.join(DOWNLOAD_FOLDER, channel_title.replace(" ", "_"))

        # Vérifie et crée le dossier de la chaîne s'il n'existe pas
        if not folder_and_file_manager.verify_and_create_folder(channel_folder):
            logger.error(f"Impossible de créer ou accéder au dossier : {channel_folder}")
            return

        # Prépare la commande yt-dlp pour télécharger la vidéo
        command = (
            f'./yt-dlp -f "{channel_quality}" --match-filter "!is_live" '
            f'-o "{channel_folder}/[%(upload_date)s]%(title)s{define_quality_title(channel_quality)}" '
            f'{BASE_URL_YT_VIDEO}{video_id}'
        )

        # Journalise et exécute la commande
        logger.info(f"Lancement de la commande : {command}")
        os.system(command)

    except Exception as e:
        logger.error(f"Erreur lors du téléchargement de la vidéo : {e}")

def fetch_channel_videos(channel):

    if not is_valid_url(channel['url']):
        logger.error(f"URL de chaîne invalide : {channel['url']}")
        return []
    videos = search_last_video_upload(channel['url'])

    """Récupère les vidéos disponibles pour une chaîne."""
    try:
        videos = search_last_video_upload(channel['url'])
        if not videos:
            logger.warning(f"Aucune vidéo trouvée pour la chaîne : {channel['title']}.")
        return videos
    except Exception as e:
        logger.error(f"Erreur lors de la récupération des vidéos pour {channel['title']} : {e}")
        return []

def is_video_new(video_date, last_check):
    """Compare les dates pour déterminer si une vidéo est nouvelle."""
    return comparer_dates(last_check, video_date)

def download_videos(channel, videos):
    """Télécharge les vidéos nouvelles pour une chaîne."""
    for video in videos:
        try:
            if is_video_new(video['published_date'], last_check_hour()):
                logger.info(f"Téléchargement de la vidéo : {video['video_id']} (Chaîne : {channel['title']})")
                download_video(channel['title'], channel['quality'], video['video_id'])
            else:
                logger.info(f"Vidéo plus ancienne ou égale à la dernière vérification : {video['video_id']}")
        except Exception as e:
            logger.error(f"Erreur lors du téléchargement de la vidéo {video['video_id']} pour {channel['title']} : {e}")

def process_channel(channel):
    """Gère la vérification et le téléchargement pour une chaîne."""
    logger.info(f"Traitement de la chaîne : {channel['title']}")
    videos = fetch_channel_videos(channel)
    if videos:
        download_videos(channel, videos)

def update_last_check_hour():
    """Mise à jour de l'heure de référence."""
    with open(LAST_CHECK_HOUR_FILE, "w") as fichier:
        actual_hour = datetime.now(TIMEZONE).strftime("%Y-%m-%dT%H:%M:%S%z")
        fichier.write(actual_hour)
        logger.info(f"Heure mise à jour : {actual_hour}")

def routine_task():
    """Routine principale pour vérifier et télécharger les vidéos."""
    logger.info("Début de la routine principale.")

    # Vérification des dossiers/fichiers nécessaires
    folder_and_file_manager.verify_and_create_folder(config.CONFIG_FOLDER_PATH)
    folder_and_file_manager.verify_file_existence(CHANNELS_LIST_FILE)
    folder_and_file_manager.verify_file_existence(LAST_CHECK_HOUR_FILE)

    # Initialisation du fichier de dernière vérification s'il est vide
    if os.path.getsize(LAST_CHECK_HOUR_FILE) == 0:
        update_last_check_hour()

    # Vérification des vidéos à télécharger
    verify_video_to_download()

    # Suppression des doublons potentiels
    folder_and_file_manager.delete_file(DOWNLOAD_FOLDER)

    logger.info("Fin de la routine principale.")


def verify_video_to_download():
    """Vérifie et télécharge les nouvelles vidéos pour chaque chaîne."""
    try:
        # Lecture de l'heure de la dernière vérification

        if not verification_lock.acquire(blocking=False):
            logger.info("Une autre vérification est en cours. Ignorée.")
            return

        last_check = last_check_hour()
        if not last_check:
            logger.warning("Aucune date de dernière vérification disponible. Aucune comparaison possible.")
            return

        # Lecture de la liste des chaînes depuis le fichier
        channels = read_channel_list(CHANNELS_LIST_FILE)
        logger.info("Début de la vérification des vidéos à télécharger.")

        # Exécution multithread
        with ThreadPoolExecutor(max_workers=5) as executor:
            executor.map(process_channel, channels)

        logger.info("Vérification des vidéos terminée.")

    except Exception as e:
        logger.error(f"Erreur dans verify_video_to_download : {e}")

    finally:
        verification_lock.release()


def download_check_routine():
    """
    Planifie et exécute les routines principales de manière périodique.
    """
    logger.info("Planification des routines avec des intervalles dynamiques.")

    # Planifier la vérification des vidéos
    schedule.every(VIDEO_CHECK_INTERVAL).hours.do(routine_task)

    # Planifier la mise à jour de l'heure
    schedule.every(LAST_CHECK_UPDATE_INTERVAL).hours.do(update_last_check_hour)

    # Forcer la première exécution
    logger.info("Exécution immédiate de routine_task et update_last_check_hour.")
    routine_task()

    # Boucle pour exécuter les tâches planifiées
    try:
        while True:
            schedule.run_pending()
            time.sleep(1)  # Évite la surcharge CPU
    except KeyboardInterrupt:
        logger.info("Routine interrompue par l'utilisateur.")

def define_quality_title(video_quality):
    match video_quality: 
        case "bestvideo+bestaudio":
            return "[best_quality]"
        case "bestaudio":
            return "[audio]"
        case "bestvideo[height<=1080]+bestaudio/best[height<=1080]":
            return "[1080p]"
        case "bestvideo[height<=720]+bestaudio/best[height<=720]":
            return "[720p]"
        case "bestvideo[height<=480]+bestaudio/best[height<=480]":
            return "[480p]"
        case "bestvideo[height<=360]+bestaudio/best[height<=360]":
            return "[360p]"
        case "bestvideo[height<=144]+bestaudio/best[height<=144]":
            return "[140p]"