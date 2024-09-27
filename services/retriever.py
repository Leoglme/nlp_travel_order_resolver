import os
import requests
from language_detection import LanguageIdentification
from stats import Stats

document_stats = {}

lang = LanguageIdentification()
stats = Stats(document_stats)

def read_from_text_files(file_path):
    """
    Lecture texte à partir d'un fichier texte + vérification UTF-8
    """
    try: #récupération du contenu du fichier
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.readlines()
            lang_prediction(content, file_path)
    except UnicodeDecodeError:
        print(f"Erreur d'encodage lors de la lecture du fichier {file_path}.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de la lecture du fichier {file_path} : {e}")

# Appel pour la détection de langue
def lang_prediction(lines, file_name):
    if lines is not None:
        nb_fr = 0
        nb_non_fr = 0

        pourcentage_fr = 0
        pourcentage_non_fr = 0
        for i, line in enumerate(lines):
            line = line.replace("\n", "")
            language, confidence = lang.stat_print(line)
            # Vérification du résultat de la langue
            if "__label__fr" in language[0]:
                nb_fr += 1
                pourcentage_fr += round(confidence[0] * 100, 2)
            else:
                nb_non_fr += 1
                pourcentage_non_fr += round(confidence[0] * 100, 2)

        # Stocker les résultats dans le dictionnaire
        document_stats[file_name] = {'fr': nb_fr, 'non_fr': nb_non_fr, 'prct_fr': pourcentage_fr, 'prct_non_fr': pourcentage_non_fr}

def read_from_url(url):
    """
    Téléchargement du texte à partir d'une URL + vérification UTF-8
    """
    try:
        response = requests.get(url)
        response.encoding = 'utf-8'  # Assurer l'encodage UTF-8
        if response.status_code == 200:
            print(f"Contenu de l'URL {url} :\n")
            print(response.text)

            # Appeler la prédiction de la langue sur le texte de l'URL
            lang_predicted, confidence = lang.predict_lang(response.text)
            print(f"Langue prédite : {lang_predicted[0]} avec une confiance de {round(confidence[0] * 100, 2)}%")
        else:
            print(f"Erreur : Impossible de récupérer le contenu de l'URL. Statut : {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération de l'URL {url} : {e}")

def read_text(origin, path):
    """
    Lecture du texte depuis une source : fichier ou URL
    """
    if origin == "fichier" and path:
        read_from_text_files(path)
    elif origin == "url" and path:
        read_from_url(path)
    else:
        print("Type de source incorrect ou chemin non fourni. Utilisez 'fichier' ou 'url'.")

def get_all_texte():
    """
    Parcourir tous les fichiers dans le dossier 'assets' et analyser chaque fichier texte
    """
    file_path = "../assets/"
    for fichier in os.listdir(file_path):
        if fichier.endswith(".txt"):
            file_path_joined = os.path.join(file_path, fichier)
            read_text(origin="fichier", path=file_path_joined)

    # Appel à la fonction pour créer le graphique après avoir analysé tous les documents
    stats = Stats(document_stats)
    stats.plot_language_stats()
    stats.language_accuracy()

# Exemple d'utilisation : parcourir tous les fichiers texte dans 'assets'
get_all_texte()