import requests
from requests.exceptions import RequestException, Timeout, HTTPError
from bs4 import BeautifulSoup
from utils.logging_config import logger

def fetch_soup(url, parser="html.parser", retries=3, timeout=10):
    """
    Tente de récupérer une page web et de la convertir en soup.
    
    Args:
        url (str): URL de la page web.
        parser (str): Parser BeautifulSoup à utiliser (html.parser ou xml).
        retries (int): Nombre de tentatives avant d'abandonner.
        timeout (int): Temps limite pour chaque tentative en secondes.
    
    Returns:
        BeautifulSoup | None: L'objet soup ou None en cas d'échec.
    """
    for attempt in range(retries):
        try:
            response = requests.get(url, timeout=timeout)
            response.raise_for_status()  # Génère une HTTPError pour les codes >= 400
            logger.info(f"Requête réussie vers {url} (tentative {attempt + 1})")
            return BeautifulSoup(response.text, parser)
        except Timeout:
            logger.warning(f"Timeout pour {url} (tentative {attempt + 1})")
        except HTTPError as http_err:
            logger.error(f"Erreur HTTP pour {url} : {http_err} (tentative {attempt + 1})")
        except RequestException as req_err:
            logger.error(f"Erreur réseau pour {url} : {req_err} (tentative {attempt + 1})")
        except Exception as e:
            logger.error(f"Erreur inattendue pour {url} : {e} (tentative {attempt + 1})")

    logger.error(f"Impossible de récupérer les données depuis {url} après {retries} tentatives.")
    return None

def soup_html(url, retries=3, timeout=10):
    return fetch_soup(url, parser="html.parser", retries=retries, timeout=timeout)

def soup_xml(url, retries=3, timeout=10):
    return fetch_soup(url, parser="xml", retries=retries, timeout=timeout)
