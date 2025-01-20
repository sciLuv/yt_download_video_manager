import os
from utils import web_utils
from utils import follow_yt_channel_management as yt_follow_manage
from utils import download_yt_video_management as yt_download_manage
from utils import folder_and_file_manager 
from utils import env_config as config
from utils.logging_config import logger


def download_all_video_from_channel(url, channel_quality):
    try:
        # Obtenir le contenu HTML de la chaîne
        soup_yt_channel = web_utils.soup_html(url)
        if not soup_yt_channel:
            logger.error("Impossible de récupérer le contenu de la chaîne.")
            return {"status": "error", "message": "Échec de la récupération du contenu de la chaîne."}

        # Trouver le titre de la chaîne
        yt_channel_title = yt_follow_manage.find_channel_title(soup_yt_channel)
        if not yt_channel_title:
            logger.error("Titre de la chaîne introuvable.")
            return {"status": "error", "message": "Impossible de trouver le titre de la chaîne."}

        # Obtenir et vérifier le dossier de téléchargement
        video_folder = config.DEFAULT_DOWNLOAD_FOLDER
        channel_folder = os.path.join(video_folder, yt_channel_title.replace(" ", "_"))
        folder_created = folder_and_file_manager.verify_and_create_folder(channel_folder)
        if not folder_created:
            logger.error(f"Échec de la création du dossier pour la chaîne : {channel_folder}")
            return {"status": "error", "message": "Impossible de créer le dossier de téléchargement."}

        # Construire la commande yt-dlp
        command = (
            f'./yt-dlp -f "{channel_quality}" --match-filter "!is_live" '
            f'-o "{channel_folder}/[%(upload_date)s]%(title)s{yt_download_manage.define_quality_title(channel_quality)}" '
            f'{url}'
        )

        logger.info(f"Lancement de la commande : {command}")
        exit_code = os.system(command)

        # Vérifier le code de sortie pour déterminer le résultat
        if exit_code == 0:
            logger.info(f"Téléchargement réussi pour la chaîne : {yt_channel_title}")
            return {"status": "success", "message": f"Téléchargement terminé pour {yt_channel_title}."}
        else:
            logger.error(f"Échec du téléchargement pour la chaîne : {yt_channel_title}. Code de sortie : {exit_code}")
            return {"status": "error", "message": f"Erreur lors du téléchargement pour {yt_channel_title}."}

    except Exception as e:
        logger.error(f"Une erreur s'est produite : {e}")
        return {"status": "error", "message": f"Exception : {str(e)}"}

def download_all_videos_from_playlist(playlist_url, playlist_quality, folder_name):
    try:
        # Obtenir le dossier de téléchargement
        video_folder = config.DEFAULT_DOWNLOAD_FOLDER
        
        # Ajouter un sous-dossier "playlist"
        playlist_base_folder = os.path.join(video_folder, "playlist")
        folder_and_file_manager.verify_and_create_folder(playlist_base_folder)

        # Créer le dossier spécifique pour la playlist dans le dossier "playlist"
        playlist_folder = os.path.join(playlist_base_folder, folder_name.replace(" ", "_"))
        folder_created = folder_and_file_manager.verify_and_create_folder(playlist_folder)
        if not folder_created:
            logger.error(f"Échec de la création du dossier : {playlist_folder}")
            return {"status": "error", "message": "Impossible de créer le dossier de téléchargement."}

        # Construire la commande yt-dlp
        command = (
            f'./yt-dlp -f "{playlist_quality}" --yes-playlist --match-filter "!is_live" '
            f'-o "{playlist_folder}/[%(upload_date)s]%(title)s{yt_download_manage.define_quality_title(playlist_quality)}" {playlist_url}'
        )

        logger.info(f"Lancement de la commande : {command}")
        exit_code = os.system(command)

        if exit_code == 0:
            logger.info(f"Téléchargement réussi pour la playlist : {folder_name}")
            return {"status": "success", "message": f"Téléchargement terminé pour {folder_name}."}
        else:
            logger.error(f"Échec du téléchargement pour la playlist : {folder_name}. Code de sortie : {exit_code}")
            return {"status": "error", "message": f"Erreur lors du téléchargement pour {folder_name}."}

    except Exception as e:
        logger.error(f"Une erreur s'est produite : {e}")
        return {"status": "error", "message": f"Exception : {str(e)}"}


def download_single_video(video_url, video_quality):
    """
    Télécharge une seule vidéo et renvoie le nom de la chaîne associée.

    Args:
        video_url (str): L'URL de la vidéo YouTube.
        video_quality (str): La qualité de la vidéo demandée.

    Returns:
        dict: Contient le statut, un message, et éventuellement le nom de la chaîne.
    """
    try:
        # Obtenir le nom de la chaîne via yt-dlp
        command = f'./yt-dlp --print "%(uploader)s" {video_url}'
        channel_name = os.popen(command).read().strip()

        if not channel_name:
            channel_name = "Unknown_Channel"

        # Remplacer les espaces par des underscores dans le nom de la chaîne
        sanitized_channel_name = channel_name.replace(" ", "_")

        # Créer le dossier pour la chaîne
        video_folder = config.DEFAULT_DOWNLOAD_FOLDER
        channel_folder = os.path.join(video_folder, sanitized_channel_name)
        folder_and_file_manager.verify_and_create_folder(channel_folder)

        # Télécharger la vidéo
        download_command = (
            f'./yt-dlp -f "{video_quality}" --match-filter "!is_live" '
            f'-o "{channel_folder}/[%(upload_date)s]%(title)s{yt_download_manage.define_quality_title(video_quality)}" {video_url}'
        )
        exit_code = os.system(download_command)

        if exit_code == 0:
            return {
                "status": "success",
                "message": f"Vidéo téléchargée avec succès dans le dossier : {sanitized_channel_name}.",
                "channel_name": sanitized_channel_name,
            }
        else:
            return {"status": "error", "message": "Erreur lors du téléchargement."}

    except Exception as e:
        logger.error(f"Erreur lors du téléchargement de la vidéo : {e}")
        return {"status": "error", "message": f"Exception : {str(e)}"}
