import os
import subprocess
import threading
import time


def download_yt_dlp():
    # Dossier parent du fichier courant
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    yt_dlp_path = os.path.join(project_root, "yt-dlp")  # Chemin cible dans le dossier parent
    
    if not os.path.exists(yt_dlp_path):
        print("Téléchargement de yt-dlp...")
        subprocess.run([
            "curl", "-L",
            "https://github.com/yt-dlp/yt-dlp/releases/latest/download/yt-dlp",
            "-o", yt_dlp_path
        ], check=True)
        subprocess.run(["chmod", "+x", yt_dlp_path], check=True)
        print(f"yt-dlp a été téléchargé et installé à : {yt_dlp_path}")
    else:
        print(f"yt-dlp est déjà installé à : {yt_dlp_path}")


def update_yt_dlp():
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    yt_dlp_path = os.path.join(project_root, "yt-dlp")
    
    if os.path.exists(yt_dlp_path):
        print("Mise à jour de yt-dlp...")
        subprocess.run([yt_dlp_path, "-U"], check=True)
        print(f"yt-dlp a été mis à jour avec succès à : {yt_dlp_path}")
    else:
        print("yt-dlp n'est pas installé, mise à jour impossible.")


def check_and_update_yt_dlp():
    """
    Vérifie et met à jour yt-dlp si nécessaire.
    """
    project_root = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    yt_dlp_path = os.path.join(project_root, "yt-dlp")
    
    if os.path.exists(yt_dlp_path):
        print("Vérification des mises à jour pour yt-dlp...")
        try:
            subprocess.run([yt_dlp_path, "-U"], check=True)
            print(f"yt-dlp a été mis à jour avec succès à : {yt_dlp_path}")
        except subprocess.CalledProcessError as e:
            print(f"Erreur lors de la mise à jour de yt-dlp : {e}")
    else:
        print("yt-dlp n'est pas installé, mise à jour impossible.")

def periodic_update(interval_hours=2):
    """
    Fonction exécutant la vérification toutes les `interval_hours`.
    """
    interval_seconds = interval_hours * 3600
    while True:
        check_and_update_yt_dlp()
        print(f"Prochaine vérification dans {interval_hours} heures.")
        time.sleep(interval_seconds)






