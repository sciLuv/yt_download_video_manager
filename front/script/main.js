import { initForm } from './controller.js';
import { initToggleSections, initToggleDownloadForms } from './basic.js';
import { port, ip } from './env.js'


document.addEventListener("DOMContentLoaded", () => {
  initForm();
  initToggleSections(); 
  initToggleDownloadForms();
});


async function loadDirectory(subpath = "") {
    const url = `http://${ip}:${port}/browse/${subpath}`;
    const videoBrowser = document.getElementById("video-browser");
    const videoPlayer = document.getElementById("video-player");

    try {
        
        const response = await fetch(url);
        if (!response.ok) {
            throw new Error(`Erreur : ${response.status}`);
        }

        const data = await response.json();

        // Vider le contenu précédent du navigateur de vidéos
        videoBrowser.innerHTML = "";

        // Conteneur de la première ligne (chemin et bouton retour)
        const firstLineContainer = document.createElement("div");
        firstLineContainer.classList.add("directory-first-line");
        firstLineContainer.style.display = "flex";
        firstLineContainer.style.alignItems = "center";

        const titleDirectory = document.createElement("h3");
        titleDirectory.textContent = `${data.path || '/'}`;

        // Ajouter un bouton pour revenir au dossier parent
        if (data.path) {
            const parentPath = data.path.substring(0, data.path.lastIndexOf('/'));
            const backButton = document.createElement("button");
            backButton.textContent = "<";
            backButton.addEventListener("click", () => {
                loadDirectory(parentPath || "");
            });
            firstLineContainer.appendChild(backButton);
        }

        firstLineContainer.appendChild(titleDirectory);
        videoBrowser.appendChild(firstLineContainer);

        // Ajouter les éléments du dossier
        data.items.forEach(item => {
            const itemElement = document.createElement("div");
            itemElement.classList.add("directory-part");
            itemElement.textContent = item.name;
            itemElement.style.cursor = "pointer";

            if (item.type === "folder") {
                itemElement.addEventListener("click", () => {
                    loadDirectory(`${item.name}`);
                });
            } else if (item.type === "file") {
                const fileExt = item.name.split('.').pop().toLowerCase();
                if (['mp4', 'webm', 'ogg'].includes(fileExt)) {
                    // Ajouter un événement pour jouer la vidéo lorsque l'utilisateur clique
                    itemElement.addEventListener("click", () => {
                        videoPlayer.src = `http://${ip}:${port}/browse/${data.path}/${item.name}`;
                        videoPlayer.style.display = "block";
                        videoPlayer.play(); // Lecture uniquement quand l'utilisateur clique
                    });
                } else {
                    alert("Type de fichier non supporté pour la lecture.");
                }
            }

            videoBrowser.appendChild(itemElement);
        });
    } catch (error) {
        console.error(error);
        videoBrowser.innerHTML = `<p>Erreur : Impossible de charger le contenu.</p>`;
    }
}



document.addEventListener("DOMContentLoaded", () => {
    loadDirectory();
});

document.addEventListener("DOMContentLoaded", () => {
    const downloadForm = document.getElementById("downloadVideosForm");
    const downloadResponse = document.getElementById("downloadResponse");

    downloadForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const channelUrl = document.getElementById("channelUrl").value;
        const channelQuality = document.getElementById("channelQuality").value;

        try {
            const response = await fetch(`http://${ip}:${port}/download-videos-from-one-channel`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    url: channelUrl,
                    quality: channelQuality,
                }),
            });

            if (!response.ok) throw new Error("Erreur du serveur.");

            const data = await response.json();
            downloadResponse.textContent = data.message;

            if (data.status === "success") {
                downloadResponse.style.color = "green";
            } else {
                downloadResponse.style.color = "red";
            }
        } catch (error) {
            console.error(error);
            downloadResponse.textContent = "Erreur lors du téléchargement.";
            downloadResponse.style.color = "red";
        }
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const downloadPlaylistForm = document.getElementById("downloadPlaylistForm");
    const playlistDownloadResponse = document.getElementById("playlistDownloadResponse");

    downloadPlaylistForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const playlistUrl = document.getElementById("playlistUrl").value;
        const playlistQuality = document.getElementById("playlistQuality").value;
        const folderName = document.getElementById("folderName").value;

        try {
            const response = await fetch(`http://${ip}:${port}/download-videos-from-playlist`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    url: playlistUrl,
                    quality: playlistQuality,
                    folder_name: folderName,
                }),
            });

            const data = await response.json();
            playlistDownloadResponse.textContent = data.message;

            if (data.status === "success") {
                playlistDownloadResponse.style.color = "green";
            } else {
                playlistDownloadResponse.style.color = "red";
            }
        } catch (error) {
            console.error(error);
            playlistDownloadResponse.textContent = "Erreur lors du téléchargement.";
            playlistDownloadResponse.style.color = "red";
        }
    });
});

document.addEventListener("DOMContentLoaded", () => {
    const downloadSingleVideoForm = document.getElementById("downloadSingleVideoForm");
    const singleVideoDownloadResponse = document.getElementById("singleVideoDownloadResponse");

    downloadSingleVideoForm.addEventListener("submit", async (event) => {
        event.preventDefault();

        const videoUrl = document.getElementById("videoUrl").value;
        const videoQuality = document.getElementById("videoQuality").value;

        try {
            const response = await fetch(`http://${ip}:${port}/download-single-video`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    url: videoUrl,
                    quality: videoQuality,
                }),
            });

            const data = await response.json();
            singleVideoDownloadResponse.textContent = data.message;

            if (data.status === "success") {
                singleVideoDownloadResponse.style.color = "green";
            } else {
                singleVideoDownloadResponse.style.color = "red";
            }
        } catch (error) {
            console.error(error);
            singleVideoDownloadResponse.textContent = "Erreur lors du téléchargement.";
            singleVideoDownloadResponse.style.color = "red";
        }
    });
});
