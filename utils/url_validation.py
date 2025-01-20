import re
from urllib.parse import urlparse

def is_valid_url(url):
    """
    Vérifie si une URL est valide.
    Args:
        url (str): L'URL à vérifier.
    Returns:
        bool: True si l'URL est valide, False sinon.
    """
    regex = re.compile(
        r'^(?:http|https)://'  # schéma http ou https
        r'(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+$'
    )
    return re.match(regex, url) is not None and urlparse(url).netloc
