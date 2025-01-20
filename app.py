from utils import follow_yt_channel_management as yt_follow_manage
from utils import download_yt_video_management as yt_download_manage
from utils import other_download_type
from utils import folder_and_file_manager
from utils import env_config as config
from utils import yt_dlp_update as yd_update
from utils.logging_config import logger
from flask import Flask, request, jsonify, send_file, send_from_directory
from flask_cors import CORS
import threading
import os
from datetime import datetime
from utils.url_validation import is_valid_url
from bs4 import BeautifulSoup

app = Flask(__name__)
CORS(app, resources={r"/*": {"origins": "*"}})

CHANNELS_LIST_FILE = config.CHANNELS_LIST_PATH

# Route pour servir le fichier HTML principal
@app.route('/')
def home():
    return send_from_directory('front', 'index.html')

# Route pour servir les fichiers statiques (CSS et JS)
@app.route('/<path:filename>')
def serve_static(filename):
    return send_from_directory('front', filename)

@app.route('/download-single-video', methods=['POST'])
def download_single_video():
    """
    Télécharge une seule vidéo YouTube et obtient le nom de la chaîne.
    """
    try:
        data = request.get_json()
        video_url = data.get('url')
        video_quality = data.get('quality', 'bestvideo+bestaudio')

        if not video_url:
            return jsonify({"status": "error", "message": "URL non fournie."}), 400

        # Appeler la fonction dans other_download_type
        result = other_download_type.download_single_video(video_url, video_quality)

        status_code = 200 if result['status'] == "success" else 500
        return jsonify(result), status_code

    except Exception as e:
        logger.error(f"Erreur dans /download-single-video : {e}")
        return jsonify({"status": "error", "message": f"Erreur serveur : {str(e)}"}), 500



@app.route('/download-videos-from-playlist', methods=['POST'])
def download_videos_from_playlist():
    """
    Télécharge toutes les vidéos d'une playlist YouTube.
    """
    try:
        data = request.get_json()
        playlist_url = data.get('url', '')
        playlist_quality = data.get('quality', 'bestvideo+bestaudio')
        folder_name = data.get('folder_name', 'Playlist')

        if not playlist_url:
            return jsonify({"status": "error", "message": "URL non fournie."}), 400

        result = other_download_type.download_all_videos_from_playlist(
            playlist_url, playlist_quality, folder_name
        )

        return jsonify(result), 200 if result['status'] == "success" else 500

    except Exception as e:
        logger.error(f"Erreur dans /download-videos-from-playlist : {e}")
        return jsonify({"status": "error", "message": f"Erreur serveur : {str(e)}"}), 500


@app.route('/download-videos-from-one-channel', methods=['POST'])
def download_videos_from_one_channel():
    """
    Télécharge toutes les vidéos d'une chaîne YouTube spécifiée.
    """
    try:
        # Récupérer les données envoyées
        data = request.get_json()
        url = data.get('url', '')
        quality = data.get('quality', 'bestvideo+bestaudio')

        if not url:
            return jsonify({"status": "error", "message": "URL non fournie."}), 400

        # Appeler la fonction pour télécharger toutes les vidéos
        result = other_download_type.download_all_video_from_channel(url, quality)

        # Retourner le résultat
        return jsonify(result), 200 if result['status'] == "success" else 500

    except Exception as e:
        logger.error(f"Erreur dans la fonction /download-videos-from-one-channel : {e}")
        return jsonify({"status": "error", "message": f"Erreur serveur : {str(e)}"}), 500


@app.route('/get-channels', methods=['GET'])
def get_channels_with_last_download():
    """Renvoie la liste des chaînes avec la dernière date de vidéo téléchargée."""
    channels = yt_download_manage.read_channel_list(CHANNELS_LIST_FILE)

    for channel in channels:
        channel['last_downloaded'] = None

        # Vérifier si le dossier de la chaîne existe
        if folder_and_file_manager.channel_folder_exists(channel['title']):
            videos = yt_download_manage.search_last_video_upload(channel['url'])
            for video in videos:
                video_date = datetime.fromisoformat(video['published_date'])
                if channel['last_downloaded'] is None or video_date > channel['last_downloaded']:
                    channel['last_downloaded'] = video_date

    # Formatage des dates pour JSON (ISO 8601)
    for channel in channels:
        if channel['last_downloaded']:
            channel['last_downloaded'] = channel['last_downloaded'].strftime("%Y-%m-%dT%H:%M:%S%z")

    return jsonify(channels)


@app.route('/submit-new-channel', methods=['POST'])
def submit():
    data = request.get_json()  # Récupère les données JSON envoyées par le frontend
    url = data.get('url', '')  # Extrait l'URL
    if not is_valid_url(url):
        return jsonify({"message": "URL invalide, veuillez vérifier et réessayer."}), 400
    
    quality = data.get('quality', 'bestvideo+bestaudio')  # Extrait la qualité ou utilise une valeur par défaut

    response = yt_follow_manage.add_channel_to_the_list(url, quality=quality)

    if url:
        # Relance immédiate de la vérification des vidéos dans un thread
        threading.Thread(target=yt_download_manage.verify_video_to_download).start()
        return jsonify({"message": response})  
    return jsonify({"message": "Aucune URL fournie."}), 400  # Erreur si aucune URL n'est donnée

@app.route('/send_followed_channels', methods=['GET'])
def send_channel_list():
    return yt_download_manage.read_channel_list(CHANNELS_LIST_FILE)

@app.route('/unfollow-channel', methods=['POST'])
def unfollow_channel():
    print("test")
    data = request.get_json()
    print(data)
    channel_name = data.get('channel_name', '')

    if not channel_name:
        return jsonify({"message": "Nom de chaîne non fourni."}), 400

    try:
        with open(CHANNELS_LIST_FILE, 'r') as file:
            lines = file.readlines()

        updated_lines = [line for line in lines if not line.startswith(channel_name + "|-|")]

        with open(CHANNELS_LIST_FILE, 'w') as file:
            file.writelines(updated_lines)

        return jsonify({"message": f"'{channel_name}' a été supprimé."}), 200
    except Exception as e:
        return jsonify({"message": f"Erreur lors de la suppression : {str(e)}"}), 500

@app.route('/update-channel-quality', methods=['POST'])
def update_quality():
    data = request.get_json()
    channel_name = data.get('channel_name', '')
    new_quality = data.get('quality', 'bestvideo+bestaudio')

    with open(CHANNELS_LIST_FILE, 'r') as file:
        lines = file.readlines()

    updated = False
    with open(CHANNELS_LIST_FILE, 'w') as file:
        for line in lines:
            if line.startswith(channel_name + "|-|"):
                parts = line.strip().split('|-|')
                if len(parts) == 3:
                    file.write(f"{parts[0]}|-|{parts[1]}|-|{new_quality}\n")
                    updated = True
                else:
                    file.write(line)
            else:
                file.write(line)

    if updated:
        return jsonify({"message": f"Qualité mise à jour pour la chaîne '{channel_name}'."})
    else:
        return jsonify({"message": "Chaîne non trouvée."}), 404
    
@app.route('/browse/<path:subpath>', methods=['GET'])
@app.route('/browse/', defaults={'subpath': ''}, methods=['GET'])
def browse_videos(subpath):
    """Naviguer dans le dossier de téléchargement ou servir un fichier vidéo."""
    base_path = os.path.join(config.DEFAULT_DOWNLOAD_FOLDER, subpath)

    # Vérifiez si le chemin existe
    if not os.path.exists(base_path):
        return jsonify({"error": "Chemin introuvable"}), 404

    # Si c'est un fichier, vérifiez s'il est lisible comme une vidéo
    if os.path.isfile(base_path):
        ext = os.path.splitext(base_path)[1].lower()
        if ext in ['.mp4', '.webm', '.ogg']:
            # Servir le fichier vidéo
            return send_file(base_path, mimetype=f"video/{ext[1:]}")  # Enlève le point dans l'extension

        return jsonify({"error": "Type de fichier non supporté"}), 400

    # Sinon, naviguez dans les dossiers
    items = []
    for item in os.listdir(base_path):
        item_path = os.path.join(base_path, item)
        if os.path.isdir(item_path):
            items.append({"name": item, "type": "folder"})
        else:
            items.append({"name": item, "type": "file"})

    return jsonify({"path": subpath, "items": items})

    
if __name__ == '__main__':
    yd_update.download_yt_dlp()
    # Assurez-vous que le dossier de logs existe
    os.makedirs(config.LOGS_FOLDER_PATH, exist_ok=True)

    # Démarrer la routine dans un thread
    try:
        thread = threading.Thread(target=yt_download_manage.download_check_routine)
        update_thread = threading.Thread(target=yd_update.periodic_update, args=(2,), daemon=True)
        thread.daemon = True  # Permet au thread de se terminer avec le programme principal
        thread.start()
        update_thread.start()
    except KeyboardInterrupt:
        logger.info("Programme interrompu par l'utilisateur.")
        thread.join()
        update_thread.join()

    # Lancer le serveur Flask
    app.run(host="0.0.0.0", port=config.PORT, debug=True)


