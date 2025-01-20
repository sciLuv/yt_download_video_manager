export function initToggleSections() {
  const sections = [
      { buttonId: "open-channel-container", containerId: "channel-list" },
      { buttonId: "open-directory-container", containerId: "video-browser" },
      { buttonId: "open-download-container", containerId: "video-dowload-container" },
  ];

  sections.forEach(({ buttonId, containerId }) => {
      const button = document.getElementById(buttonId);
      const container = document.getElementById(containerId);

      button.addEventListener("click", () => {
          // Fermer toutes les sections
          sections.forEach(({ containerId: otherContainerId }) => {
              const otherContainer = document.getElementById(otherContainerId);
              if (otherContainer && otherContainer !== container) {
                  otherContainer.classList.add("hidden");
              }
          });

          // Basculer la section actuelle
          container.classList.toggle("hidden");
      });
  });
}


export function initToggleDownloadForms() {
    const forms = [
        { buttonId: "addChannelButton", formId: "url-form-add-channel" },
        { buttonId: "downloadChannelButton", formId: "downloadVideosForm" },
        { buttonId: "downloadPlaylistButton", formId: "downloadPlaylistForm" },
        { buttonId: "downloadSingleVideoButton", formId: "downloadSingleVideoForm" },
    ];

    forms.forEach(({ buttonId, formId }) => {
        const button = document.getElementById(buttonId);
        const form = document.getElementById(formId);

        button.addEventListener("click", () => {
            // Fermer tous les formulaires
            forms.forEach(({ formId: otherFormId }) => {
                const otherForm = document.getElementById(otherFormId);
                if (otherForm && otherForm !== form) {
                    otherForm.classList.add("hidden");
                }
            });

            // Basculer l'affichage du formulaire actuel
            form.classList.toggle("hidden");
        });
    });
}
