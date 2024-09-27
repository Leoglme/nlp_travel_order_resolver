import numpy as np
from matplotlib import pyplot as plt

class Stats:
    def __init__(self, document_stats):
        self.document_stats = document_stats

    def plot_language_stats(self):
        documents = list(self.document_stats.keys())
        nb_lignes_fr = np.asarray([self.document_stats[doc]['fr'] for doc in documents])  # Conversion en tableau NumPy
        nb_lignes_non_fr = np.asarray([self.document_stats[doc]['non_fr'] for doc in documents])

        ind = np.arange(len(documents))  # Position des documents sur l'axe x

        plt.figure(figsize=(10, 6))
        plt.bar(ind, nb_lignes_fr, width=0.4, label='Français', color='blue')
        plt.bar(ind, nb_lignes_non_fr, width=0.4, label='Langue différente', color='red', bottom=nb_lignes_fr)

        plt.xlabel('Documents')
        plt.ylabel('Nombre de lignes')
        plt.title('Nombre de lignes par document et détection de la langue')
        plt.xticks(ind, documents, rotation=45, ha="right")
        plt.legend()
        plt.tight_layout()
        plt.show()

    def language_accuracy(self):
        documents = list(self.document_stats.keys())
        nb_lignes_fr = np.asarray([self.document_stats[doc]['fr'] for doc in documents])
        nb_lignes_non_fr = np.asarray([self.document_stats[doc]['non_fr'] for doc in documents])
        prct_fr = np.asarray([self.document_stats[doc]['prct_fr'] for doc in documents])
        prct_non_fr = np.asarray([self.document_stats[doc]['prct_non_fr'] for doc in documents])

        certitude_fr = [(prct / nb_fr * 100) if nb_fr != 0 else 0 for prct, nb_fr in zip(prct_fr, nb_lignes_fr)]
        certitude_non_fr = [(prct / nb_non_fr * 100) if nb_non_fr != 0 else 0 for prct, nb_non_fr in
                            zip(prct_non_fr, nb_lignes_non_fr)]

        ind = np.arange(len(documents))

        plt.figure(figsize=(10, 6))
        plt.bar(ind - 0.2, certitude_fr, width=0.4, label='Certitude Français', color='blue')
        plt.bar(ind + 0.2, certitude_non_fr, width=0.4, label='Certitude Non-Français', color='red')

        plt.xlabel('Documents')
        plt.ylabel('Pourcentage de certitude (%)')
        plt.title('Pourcentage de certitude des prédictions pour les lignes françaises et non françaises')
        plt.xticks(ind, documents, rotation=45, ha="right")
        plt.legend()
        plt.tight_layout()
        plt.show()
