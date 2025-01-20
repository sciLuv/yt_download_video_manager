#!/bin/bash

# Fonction pour vérifier Python (3.x déjà présent sur Debian 12)
verify_python() {
    echo "Vérification de Python..."
    if ! command -v python3 &>/dev/null; then
        echo "Python 3 n'est pas installé. Installation..."
        sudo apt update
        sudo apt install -y python3 python3-venv python3-distutils
    else
        echo "Python 3 est déjà installé."
    fi
}

# Fonction pour installer ffmpeg si nécessaire
install_ffmpeg() {
    echo "Vérification de ffmpeg..."
    if ! ffmpeg -version &>/dev/null; then
        echo "ffmpeg non trouvé. Installation..."
        sudo apt update
        sudo apt install -y ffmpeg
    else
        echo "ffmpeg est déjà installé."
    fi
}

# Installation des dépendances Python dans un venv
install_python_dependencies() {
    echo "Installation des dépendances Python..."
    if [ -f "requirements.txt" ]; then
        # On crée un venv Python 3.11 (ou 3.x) local
        python3 -m venv venv
        source venv/bin/activate
        pip install --upgrade pip
        # --break-system-packages pour contourner PEP 668 (à utiliser avec précaution !)
        pip install --break-system-packages -r requirements.txt
        deactivate
    else
        echo "Fichier requirements.txt introuvable !"
        exit 1
    fi
}

# Configuration de l'application
configure_app() {
    read -p "Entrez le port de l'application [5000 par défaut] : " app_port
    app_port=${app_port:-5000}

    read -p "Entrez l'IP de la machine [127.0.0.1 par défaut] : " app_ip
    app_ip=${app_ip:-127.0.0.1}

    echo "Configuration avec IP: $app_ip, Port: $app_port..."

    # Mise à jour des fichiers de configuration Python
    if [ -f "utils/env_config.py" ]; then
        sed -i "s/^PORT=\".*\"/PORT=\"$app_port\"/" utils/env_config.py
    else
        echo "Fichier utils/env_config.py introuvable !"
        exit 1
    fi

    # Mise à jour des fichiers de configuration Frontend
    if [ -f "front/script/env.js" ]; then
        sed -i "s/export const port = .*/export const port = \"$app_port\";/" front/script/env.js
        sed -i "s/export const ip = .*/export const ip = \"$app_ip\";/" front/script/env.js
    else
        echo "Fichier front/script/env.js introuvable !"
        exit 1
    fi

}

# Lancement du projet
start_project() {
    echo "Lancement du projet..."
    source venv/bin/activate
    python app.py
}

# Appel des fonctions
verify_python
install_ffmpeg
install_python_dependencies
configure_app
start_project
