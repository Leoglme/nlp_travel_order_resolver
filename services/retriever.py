import os
import requests

def read_from_text_files(file_path):
    """
    Lecture texte à partir d'un fichier texte + vérification UTF-8
    """
    if not os.path.exists(file_path):
        print(f"Le fichier {file_path} n'existe pas.")
        return

    try:
        with open(file_path, "r", encoding="utf-8") as file:
            content = file.read()
            print(f"Contenu de {file_path} :\n")
            print(content)
    except UnicodeDecodeError:
        print(f"Erreur d'encodage lors de la lecture du fichier {file_path}.")
    except Exception as e:
        print(f"Une erreur s'est produite lors de la lecture du fichier {file_path} : {e}")


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
        else:
            print(f"Erreur : Impossible de récupérer le contenu de l'URL. Statut : {response.status_code}")
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la récupération de l'URL {url} : {e}")


def read_text(origin, path):
    """
    Lecture du texte
    """
    if origin == "fichier" and path:
        read_from_text_files(path)
    elif origin == "url" and path:
        read_from_url(path)
    else:
        print("Type de source incorrect ou chemin non fourni. Utilisez 'fichier' ou 'url'.")

def get_all_texte():
    # Parcourir tous les fichiers dans le dossier 'assets'
    file_path = "../assets/"
    for fichier in os.listdir(file_path):
        if fichier.endswith(".txt"):
            file_path = os.path.join(file_path, fichier)
            read_text(origin="fichier", path=file_path)

# Exemples d'utilisation individuelle :
read_text(origin="fichier", path="../assets/sample_nlp_input.txt")  # Fichier local
#read_text(origin="url", path="https://exemple.com/chemin/vers/texte")  # URL

get_all_texte()