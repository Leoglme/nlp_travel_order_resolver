import os
import sys
import json
import numpy as np
from tqdm.auto import tqdm
import torch
from transformers import CamembertTokenizerFast, CamembertForTokenClassification
from datasets import load_dataset
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, classification_report
import nbformat as nbf
import asyncio

# Ajouter le projet à Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))
from models.camembert_ner_model import CamembertNERModel

# Gestion des boucles asynchrones sous Windows
if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Définition des chemins
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
notebook_dir = "evaluations/camembert_ner_evaluation"
notebook_path = os.path.join(notebook_dir, "camembert_ner_evaluation.ipynb")
executed_notebook_path = os.path.join(notebook_dir, "executed_notebook.ipynb")
html_output_path = os.path.join(notebook_dir, "index.html")
test_dataset_path = os.path.join(project_root, "datasets/camembert_ner_dataset.csv")
model_path = "model_output/camembert_ner"

# Assure la création du répertoire des notebooks
if not os.path.exists(notebook_dir):
    os.makedirs(notebook_dir)

# Définir les étiquettes du modèle
label_list = ["O", "B-DEP", "B-ARR", "I-DEP", "I-ARR"]

# Nettoyage des fichiers précédents
print("Nettoyage des anciens fichiers...")
for file_path in [notebook_path, executed_notebook_path, html_output_path]:
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Supprimé : {file_path}")

# Charger le modèle et le tokenizer
print("Chargement du modèle et du tokenizer...")
tokenizer = CamembertTokenizerFast.from_pretrained(model_path)
model = CamembertForTokenClassification.from_pretrained(model_path)

# Charger le dataset de test
print("Chargement des données de test...")
if not os.path.exists(test_dataset_path):
    raise FileNotFoundError(f"Fichier de dataset introuvable : {test_dataset_path}")

dataset = load_dataset("csv", data_files={"test": test_dataset_path})["test"]
camembert_ner_model = CamembertNERModel()

# Tokenisation et alignement des labels
tokenized_dataset = dataset.map(camembert_ner_model.tokenize_and_align_labels, batched=True)
test_texts = dataset["text"]
test_labels = tokenized_dataset["labels"]
num_rows_test_data = len(dataset)

# Prédictions
print("Prédictions...")
results, all_true_labels, all_predicted_labels = [], [], []
for i, text in enumerate(tqdm(test_texts, desc="Prédictions")):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        logits = model(**inputs).logits
    predictions = np.argmax(logits.numpy(), axis=2)[0]
    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0].numpy())

    valid_indices = [i for i, token in enumerate(tokens) if not token.startswith("<") and token != "[PAD]"]
    filtered_predictions = [int(predictions[i]) for i in valid_indices]
    filtered_tokens = [tokens[i] for i in valid_indices]
    filtered_true_labels = [int(test_labels[i][j]) for j in valid_indices]

    all_true_labels.extend(filtered_true_labels)
    all_predicted_labels.extend(filtered_predictions)

    results.append({
        "text": text,
        "tokens": filtered_tokens,
        "predictions": filtered_predictions,
        "true_labels": filtered_true_labels,
    })

# Validation
if len(all_true_labels) != len(all_predicted_labels):
    raise ValueError("Longueur incohérente entre étiquettes réelles et prédites!")

# Calcul des métriques
metrics = {
    "Accuracy": accuracy_score(all_true_labels, all_predicted_labels),
    "Precision": precision_score(all_true_labels, all_predicted_labels, average="weighted", zero_division=0),
    "Recall": recall_score(all_true_labels, all_predicted_labels, average="weighted", zero_division=0),
    "F1-Score": f1_score(all_true_labels, all_predicted_labels, average="weighted", zero_division=0),
}
classification_rep = classification_report(all_true_labels, all_predicted_labels, target_names=label_list,
                                           zero_division=0)

# Création du notebook
n = nbf.v4.new_notebook()

# 1. Introduction
n.cells.append(nbf.v4.new_markdown_cell(f"# Évaluation du modèle `Camembert NER`"))
n.cells.append(nbf.v4.new_markdown_cell(f"### Ce notebook évalue les performances d'un modèle fine-tuné pour extraire les villes de départ et d'arrivée dans des textes."
                                        "Il est basé sur un modèle Camembert fine-tuné sur un ensemble de données de "
                                        "textes annotés pour l'extraction des entités nommées. "
                                        f"Le modèle est évalué sur un dataset de test de {num_rows_test_data} lignes."))

# 2. Exploration des données
n.cells.append(nbf.v4.new_markdown_cell("## Exploration des Données"))
n.cells.append(nbf.v4.new_markdown_cell("""
Le tableau suivant montre un aperçu des données utilisées pour l'évaluation du modèle.
Chaque ligne correspond à une phrase annotée avec des villes de départ (B-DEP, I-DEP) et des villes d'arrivée (B-ARR, I-ARR).
"""))
n.cells.append(nbf.v4.new_code_cell(f"""
import pandas as pd
pd.set_option('display.max_colwidth', None)
dataset = pd.read_csv(r"{test_dataset_path}")
dataset.head(10)
"""))

# 3. Statistiques sur les données
n.cells.append(nbf.v4.new_markdown_cell("## Statistiques sur le Dataset"))
n.cells.append(nbf.v4.new_markdown_cell("""
Ce graphique montre la fréquence des étiquettes (par exemple, "O", "B-DEP", "B-ARR") dans le dataset. 
Cela permet d'identifier les déséquilibres éventuels entre les classes.
"""))
n.cells.append(nbf.v4.new_code_cell(f"""
from collections import Counter
import matplotlib.pyplot as plt

# Comptage des étiquettes
label_counts = Counter([label for labels in {json.dumps(test_labels)} for label in labels if label != -100])

plt.figure(figsize=(10, 6))
plt.bar({json.dumps(label_list)}, [label_counts.get(i, 0) for i in range(len({json.dumps(label_list)}))], color='skyblue')
plt.title("Répartition des classes dans le dataset")
plt.xlabel("Classes")
plt.ylabel("Nombre d'occurrences")
plt.grid(axis='y')
plt.show()
"""))

# 4. Visualisation des métriques
n.cells.append(nbf.v4.new_markdown_cell("## Visualisation des métriques de performance"))

n.cells.append(nbf.v4.new_markdown_cell("""
Ce graphique en barres montre les métriques de performance du modèle :
- **Précision (Accuracy)** : La proportion des prédictions correctes parmi toutes les prédictions.
- **Précision (Precision)** : Proportion de prédictions correctes parmi les cas réels.
- **Rappel (Recall)** : Moyenne harmonique de la précision et du rappel.
- **Score F1** : Proportion globale de prédictions correctes.
"""))

n.cells.append(nbf.v4.new_code_cell(f"""
plt.figure(figsize=(8, 5))
plt.barh(list({metrics}.keys()), list({metrics}.values()), color=['skyblue', 'orange', 'green', 'purple'])
plt.xlabel("Score")
plt.title("Model Performance Metrics")
for i, value in enumerate({metrics}.values()):
    plt.text(value, i, {{value}}:.2f)
plt.show()
"""))

# 5. Matrice de confusion
n.cells.append(nbf.v4.new_markdown_cell("## Matrice de Confusion"))
n.cells.append(nbf.v4.new_markdown_cell("""
La matrice de confusion ci-dessous indique comment le modèle a prédit les étiquettes pour les tokens. 
Chaque cellule montre le nombre de fois où une étiquette réelle a été prédite comme une autre.
- **Lignes** : étiquettes réelles.
- **Colonnes** : étiquettes prédites.
"""))
n.cells.append(nbf.v4.new_code_cell(f"""
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

# Calcul et affichage
cm = confusion_matrix({all_true_labels}, {all_predicted_labels})
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels={label_list})

plt.figure(figsize=(10, 8))
disp.plot(cmap=plt.cm.Blues, xticks_rotation=45)
plt.title("Matrice de confusion")
plt.xlabel("Étiquette Prédite")
plt.ylabel("Étiquette Réelle")
plt.grid(False)
plt.show()
"""))

# # 6. Interface interactive
# n.cells.append(nbf.v4.new_markdown_cell("## Interface Interactive"))
# n.cells.append(nbf.v4.new_markdown_cell("""
# Cette interface permet de tester le modèle en entrant une phrase et en obtenant les prédictions token par token.
# """))
# n.cells.append(nbf.v4.new_code_cell(f"""
# from transformers import CamembertTokenizerFast, CamembertForTokenClassification
# import torch
# from ipywidgets import interact
# import os
#
# # Définition des étiquettes du modèle
# label_list = {json.dumps(label_list)}
#
# # Chemin vers le modèle
# model_path = r"{model_path}"
#
# # Vérification du contenu du chemin
# if not os.path.exists(model_path):
#     raise FileNotFoundError(f"Le chemin spécifié pour le modèle ({model_path}) n'existe pas.")
#
# print(f"Contenu du dossier {model_path} :", os.listdir(model_path))
#
# # Chargement du tokenizer et du modèle
# try:
#     tokenizer = CamembertTokenizerFast.from_pretrained(model_path, local_files_only=True)
#     model = CamembertForTokenClassification.from_pretrained(model_path, local_files_only=True)
# except OSError as e:
#     print(f"Erreur : Impossible de charger les fichiers nécessaires depuis {model_path}.")
#     print("Vérifiez que le dossier contient tous les fichiers nécessaires : tokenizer.json, config.json, etc.")
#     raise e
#
# def test_model(sentence):
#     \"\"\"Teste le modèle sur une phrase entrée par l'utilisateur.\"\"\"
#     try:
#         # Prétraitement de la phrase
#         inputs = tokenizer(sentence, return_tensors="pt", padding=True, truncation=True)
#         with torch.no_grad():
#             logits = model(**inputs).logits
#         # Prédictions
#         predictions = torch.argmax(logits, dim=2).numpy()[0]
#         tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0])
#         # Retourne les prédictions pour chaque token
#         return dict(zip(tokens, [label_list[p] for p in predictions]))
#     except Exception as e:
#         print(f"Erreur lors de la prédiction")
#         raise e
#
# # Interface interactive
# interact(test_model, sentence="Je veux aller de Paris à Marseille")
# """))

# Sauvegarde du notebook généré
if not os.path.exists(notebook_dir):
    os.makedirs(notebook_dir)

with open(notebook_path, "w", encoding="utf-8") as f:
    nbf.write(n, f)

print(f"Notebook created: {notebook_path}")
os.system(f'jupyter nbconvert --to notebook --execute {notebook_path} --no-input --output executed_notebook.ipynb')
os.system(f'jupyter nbconvert --to html {executed_notebook_path} --no-input --output index.html')
print("Notebook execution and conversion to HTML completed.")
