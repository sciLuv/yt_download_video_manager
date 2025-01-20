import os
from utils import folder_and_file_manager
from utils import env_config as config
from utils import web_utils
from utils.logging_config import logger
from utils.url_validation import is_valid_url


channels_list_file = config.CHANNELS_LIST_PATH
config_folder_path = config.CONFIG_FOLDER_PATH




# from channel home page from youtube, find the associate rss page 
def find_channel_rss(soup):
    return soup.find("link", {"type": "application/rss+xml"}).get("href")


# from channel home page url from youtube, find the channel's name
def find_channel_title(soup):
    return soup.find("title").text.split(" -")[0]

# adding new channel to the list
def add_channel_to_the_list(url, quality='bestvideo+bestaudio'):
    if not is_valid_url(url):
        logger.error(f"L'URL fournie n'est pas valide : {url}")
        return "URL invalide, veuillez vérifier et réessayer."
    
    #vérifie si un dossier config exist ou non, si il n'existe pas le créer
    folder_and_file_manager.verify_and_create_folder(config_folder_path)
    #vérifie si un fichier channels_list exist ou non, si il n'existe pas le créer
    folder_and_file_manager.verify_file_existence(channels_list_file)

    soup = web_utils.soup_html(url)

    if soup:
        channel_title = find_channel_title(soup)
        channel_rss = find_channel_rss(soup)

        new_channel_line = f"{channel_title}|-|{channel_rss}|-|{quality}\n"

        with open(channels_list_file, 'r') as file:
            lines = file.readlines()

        if new_channel_line in lines:
            logger.info(f"'{channel_title}' est déjà dans la liste.")
            return f"'{channel_title}' est déjà dans la liste."
        else:
            with open(channels_list_file, 'a') as file:
                file.write(new_channel_line)
            logger.info(f"Chaîne ajoutée : '{channel_title}' avec qualité '{quality}' et flux RSS '{channel_rss}'.")
            return f"'{channel_title}' a été ajouté à la liste."
    else:
        logger.error("Le HTML n'a pas pu être récupéré.")
        return "Il y a un probleme avec le texte envoyé"

def remove_channel_from_list(channel_name):

    if not os.path.exists(channels_list_file):
        logger.error(f"Le fichier {channels_list_file} n'existe pas.")
        return False

    try:
        with open(channels_list_file, 'r', encoding='utf-8') as file:
            lines = file.readlines()

        updated_lines = []
        channel_found = False
        for line in lines:
            if line.startswith(channel_name + "|-|"):
                logger.info(f"Chaîne trouvée et supprimée : {line.strip()}")
                channel_found = True
            else:
                updated_lines.append(line)

        if not channel_found:
            logger.warning(f"Chaîne '{channel_name}' introuvable dans la liste.")
            return False

        with open(channels_list_file, 'w', encoding='utf-8') as file:
            file.writelines(updated_lines)

        return True
    except Exception as e:
        logger.error(f"Erreur lors de la suppression de la chaîne '{channel_name}': {e}")
        return False
    




