<template></template>



<script lang="ts" setup>
// Fonction pour ajouter les boutons de copie après le rendu
const addCopyButtons = () => {
  setTimeout(() => {
    document.querySelectorAll("pre code, .highlight pre").forEach((block) => {
      // Vérifier si un bouton est déjà ajouté
      if (block.parentElement?.querySelector(".copy-button")) return;

      const button = document.createElement("button");
      button.className = "copy-button absolute top-2 right-2 bg-gray-800 text-white px-2 py-1 text-xs rounded";
      button.textContent = "Copier";

      button.onclick = () => {
        navigator.clipboard.writeText(block.textContent || "").then(() => {
          button.textContent = "Copié !";
          setTimeout(() => (button.textContent = "Copier"), 2000);
        });
      };

      const pre = block.parentElement;
      if (pre) {
        pre.style.position = "relative";
        pre.appendChild(button);
      }
    });
  }, 100); // Attendre un peu après l'affichage du Markdown
};

onMounted(() => {
  addCopyButtons();
});
</script>


<style>
.copy-button {
  position: absolute;
  top: 8px;
  right: 8px;
  background-color: rgba(0, 0, 0, 0.7);
  color: white;
  padding: 4px 8px;
  border-radius: 4px;
  cursor: pointer;
  font-size: 12px;
  border: none;
}

.copy-button:hover {
  background-color: rgba(0, 0, 0, 0.9);
}

.highlight pre {
  color: rgb(229, 231, 235) !important;
  background-color: rgb(31, 41, 55) !important;
  overflow-x: auto;
  font-weight: 400;
  font-size: 0.875em !important;
  line-height: 1.7142857 !important;
  margin-top: 1.7142857em !important;
  margin-bottom: 1.7142857em !important;
  border-radius: 0.375rem;
  padding-top: 0.8571429em !important;
  padding-inline-end: 1.1428571em !important;
  padding-bottom: 0.8571429em !important;
  padding-inline-start: 1.1428571em !important;
}
</style>
