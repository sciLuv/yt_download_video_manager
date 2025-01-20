import { port, ip } from './env.js'

export function initForm() {
    const form = document.getElementById("url-form-add-channel");
    const responseContainer = document.getElementById("response");
    const modal = document.getElementById("modal");
    const closeModalButton = document.getElementById("close-modal");
    const modalChannelName = document.getElementById("modal-channel-name");
    const modalQualitySelector = document.getElementById("modal-quality");
    const updateChannelButton = document.getElementById("update-channel");
    const deleteChannelButton = document.getElementById("delete-channel");
    const returnButton = document.getElementById("return-button");

    let selectedChannelName = "";

    function openModal(channelName, currentQuality) {
        modalChannelName.textContent = `Chaîne : ${channelName}`;
        selectedChannelName = channelName;

        Array.from(modalQualitySelector.options).forEach(option => {
            option.selected = option.value === currentQuality;
        });

        modal.classList.remove("hidden");
    }

    function closeModal() {
        modal.classList.add("hidden");
        selectedChannelName = "";
    }

    closeModalButton.addEventListener("click", closeModal);
    returnButton.addEventListener("click", closeModal);

    form.addEventListener("submit", async function (event) {
        event.preventDefault();

        const urlInput = document.getElementById("url").value;
        const qualityInput = document.getElementById("quality").value;

        try {
            const response = await fetch(`http://${ip}:${port}/submit-new-channel`, {
                method: "POST",
                headers: {
                    "Content-Type": "application/json",
                },
                body: JSON.stringify({
                    url: urlInput,
                    quality: qualityInput,
                }),
            });

            if (!response.ok) throw new Error("Erreur du serveur");

            const data = await response.json();
            responseContainer.textContent = data.message;

            // Mise à jour de l'interface pour refléter les changements
            await fetchFollowedChannels();
        } catch (error) {
            console.error(error);
            responseContainer.textContent = "Erreur lors de l'envoi des données.";
        }
    });

    async function fetchFollowedChannels() {
        const url = `http://${ip}:${port}/get-channels`;
        const channelContainer = document.getElementById("channel-list");
    
        try {
            const response = await fetch(url, {
                method: "GET",
                headers: {
                    "Content-Type": "application/json",
                },
            });
    
            if (!response.ok) {
                throw new Error(`Erreur HTTP : ${response.status}`);
            }
    
            const channelList = await response.json();
            channelContainer.innerHTML = "";
    
            channelList.forEach(channel => {
                const channelItem = document.createElement("div");
                channelItem.className = "channel-item";
    
                const title = document.createElement("h5");
                title.textContent = channel.title;
    
                const manageButton = document.createElement("button");
                manageButton.textContent = "Gérer";
                manageButton.className = "primary-button";
                manageButton.addEventListener("click", () => {
                    openModal(channel.title, channel.quality);
                });
    
                channelItem.appendChild(title);
                channelItem.appendChild(manageButton);
                channelContainer.appendChild(channelItem);
            });
        } catch (error) {
            console.error("Erreur lors de la récupération des chaînes :", error);
        }
    }
    

    

    updateChannelButton.addEventListener("click", async () => {
        try {
            const newQuality = modalQualitySelector.value;

            const response = await fetch(`http://${ip}:${port}/update-channel-quality`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    channel_name: selectedChannelName,
                    quality: newQuality,
                }),
            });

            if (!response.ok) throw new Error("Erreur serveur");

            const data = await response.json();
            alert(data.message);
            closeModal();
            fetchFollowedChannels();
        } catch (error) {
            console.error(error);
            alert("Erreur lors de la mise à jour de la qualité.");
        }
    });

    deleteChannelButton.addEventListener("click", async () => {
        try {
            const response = await fetch(`http://${ip}:${port}/unfollow-channel`, {
                method: "POST",
                headers: { "Content-Type": "application/json" },
                body: JSON.stringify({
                    channel_name: selectedChannelName,
                }),
            });

            if (!response.ok) throw new Error("Erreur serveur");

            const data = await response.json();
            alert(data.message);
            closeModal();
            fetchFollowedChannels();
        } catch (error) {
            console.error(error);
            alert("Erreur lors de la suppression de la chaîne.");
        }
    });

    fetchFollowedChannels();
}
