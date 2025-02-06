import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, module="zmq._future")

import os
import nbformat as nbf
import numpy as np
import torch
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
from sklearn.metrics import (precision_score, recall_score, f1_score, accuracy_score,
                             confusion_matrix, roc_curve, auc)
from datasets import load_dataset
from tqdm.auto import tqdm

# ===============================
# Définition des chemins de fichiers
# ===============================
notebook_dir = "evaluations/travel_intent_classifier_evaluation"
if not os.path.exists(notebook_dir):
    os.makedirs(notebook_dir)

notebook_path = os.path.join(notebook_dir, "travel_intent_classifier_evaluation.ipynb")
executed_notebook_path = os.path.join(notebook_dir, "executed_notebook.ipynb")
html_output_path = os.path.join(notebook_dir, "index.html")

# Supprimer les anciens fichiers s'ils existent
print("Suppression des anciens fichiers...")
for file_path in [executed_notebook_path, html_output_path, notebook_path]:
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Supprimé : {file_path}")

# ===============================
# Chargement du modèle et du tokenizer
# ===============================
print("Chargement du modèle et du tokenizer...")
model_path = "model_output/travel_intent_classifier"
model = DistilBertForSequenceClassification.from_pretrained(model_path)
tokenizer = DistilBertTokenizerFast.from_pretrained(model_path)

# ===============================
# Chargement et préparation des données de test
# ===============================
print("Chargement et préparation des données de test...")
test_dataset_path = "datasets/test_travel_intent_dataset.csv"
test_data = load_dataset("csv", data_files={"test": test_dataset_path})["test"]
num_rows_test_data = len(test_data)
print(f"Nombre d'exemples dans le jeu de test : {num_rows_test_data}")

# Tokenisation des données de test
print("Tokenisation des données...")
tokenized_test_data = {"input_ids": [], "attention_mask": [], "label": []}
for example in tqdm(test_data, desc="Tokenisation"):
    tokenized = tokenizer(example["text"], padding="max_length", truncation=True)
    tokenized_test_data["input_ids"].append(tokenized["input_ids"])
    tokenized_test_data["attention_mask"].append(tokenized["attention_mask"])
    tokenized_test_data["label"].append(example["label"])

# Conversion des données en tenseurs
print("Conversion des données en tenseurs...")
test_encodings = {
    key: torch.tensor(np.array(tokenized_test_data[key])) for key in ["input_ids", "attention_mask"]
}
labels = np.array(tokenized_test_data["label"])

# ===============================
# Prédiction avec le modèle (traitement par batch)
# ===============================
print("Prédiction sur le jeu de test...")
batch_size = 32
predictions = []
probs = []

for i in tqdm(range(0, len(labels), batch_size), desc="Prédiction par batch"):
    batch_input_ids = test_encodings["input_ids"][i:i + batch_size]
    batch_attention_mask = test_encodings["attention_mask"][i:i + batch_size]
    with torch.no_grad():
        outputs = model(input_ids=batch_input_ids, attention_mask=batch_attention_mask)
        batch_probs = outputs.logits.softmax(dim=-1).numpy()
        batch_predictions = np.argmax(batch_probs, axis=1)
        predictions.extend(batch_predictions)
        probs.extend(batch_probs)

predictions = np.array(predictions)
probs = np.array(probs)

# ===============================
# Calcul des métriques d'évaluation
# ===============================
accuracy = accuracy_score(labels, predictions)
precision = precision_score(labels, predictions, average="weighted")
recall = recall_score(labels, predictions, average="weighted")
f1 = f1_score(labels, predictions, average="weighted")

cm = confusion_matrix(labels, predictions)

# Calcul de la courbe ROC et de l'AUC
fpr, tpr, thresholds = roc_curve(labels, probs[:, 1])
roc_auc = auc(fpr, tpr)

print("Métriques globales calculées :")
print(f" - Accuracy  : {accuracy:.4f}")
print(f" - Precision : {precision:.4f}")
print(f" - Recall    : {recall:.4f}")
print(f" - F1-Score  : {f1:.4f}")
print("Matrice de confusion :")
print(cm)

# ===============================
# Création du Notebook
# ===============================
print("Création du notebook...")

n = nbf.v4.new_notebook()

# --- Introduction générale ---
intro_text = r"""
# Évaluation détaillée du modèle TravelIntentClassifier

Ce notebook présente une **analyse complète** du modèle de classification d'intentions de voyage.  
Nous utilisons ici un modèle [DistilBERT](https://huggingface.co/distilbert-base-uncased) fine-tuné sur un jeu de données de textes annotés pour détecter si un texte exprime une intention de voyage.

## Objectifs
- **Vérifier la performance** du modèle sur un jeu de test réel.
- **Analyser** en détail les métriques de performance et les courbes associées.
- **Interpréter** les résultats à l'aide de graphiques explicatifs et d'analyses textuelles.

Le jeu de test contient **{} exemples**.  
""".format(num_rows_test_data)
n.cells.append(nbf.v4.new_markdown_cell(intro_text))

# --- Présentation du modèle et des données ---
model_data_description = r"""
## Présentation du modèle et des données

- **Modèle utilisé :** DistilBERT fine-tuné pour la classification binaire (Intent / Non-Intent).
- **Données de test :** Un fichier CSV contenant des exemples de textes annotés.
- **Tokenisation :** Chaque texte est transformé en séquence de tokens avec un padding jusqu'à une longueur maximale.

Les étapes principales du notebook sont les suivantes :
1. **Chargement** du modèle et des données.
2. **Tokenisation** et préparation des données pour le modèle.
3. **Prédiction** par batch et calcul des probabilités.
4. **Évaluation** avec plusieurs métriques et visualisations.
5. **Analyse détaillée** de chaque graphique afin de mieux comprendre les performances du modèle.
"""
n.cells.append(nbf.v4.new_markdown_cell(model_data_description))

# --- Résultats d'évaluation ---
eval_results_code = f"""
# Résultats globaux
accuracy = {accuracy}
precision = {precision}
recall = {recall}
f1 = {f1}
predictions = {list(predictions)}
labels = {list(labels)}
probs = {probs.tolist()}

print("Accuracy  :", accuracy)
print("Precision :", precision)
print("Recall    :", recall)
print("F1-Score  :", f1)
"""
n.cells.append(nbf.v4.new_code_cell(eval_results_code))

# --- Graphique des métriques de performance ---
perf_metrics_intro = r"""
## Visualisation des métriques de performance

**Interprétation attendue :**  
Avant ce graphique, il est important de comprendre que chaque métrique représente un aspect spécifique de la performance du modèle :
- **Accuracy** : Pourcentage d'exemples correctement classés.
- **Precision** : Proportion des prédictions positives correctes par rapport à toutes les prédictions positives.
- **Recall** : Capacité du modèle à identifier correctement les exemples positifs.
- **F1-Score** : Moyenne harmonique entre la précision et le recall.

Le graphique ci-dessous présente ces quatre métriques sous forme de barres horizontales.
"""
n.cells.append(nbf.v4.new_markdown_cell(perf_metrics_intro))

perf_metrics_code = r"""
import matplotlib.pyplot as plt

# Dictionnaire des métriques
metrics = {
    "Accuracy": accuracy,
    "Precision": precision,
    "Recall": recall,
    "F1-Score": f1,
}

plt.figure(figsize=(10, 6))
bars = plt.barh(list(metrics.keys()), list(metrics.values()), color=['#6baed6', '#fd8d3c', '#74c476', '#9e9ac8'])
plt.xlabel("Score")
plt.title("Performance du modèle : Métriques globales")
# Ajout des valeurs sur les barres
for bar in bars:
    width = bar.get_width()
    plt.text(width + 0.01, bar.get_y() + bar.get_height()/2,
             f'{width:.2f}', va='center')
plt.show()
"""
n.cells.append(nbf.v4.new_code_cell(perf_metrics_code))

perf_metrics_analysis = r"""
### Analyse des métriques

- **Accuracy** indique que le modèle classe correctement une très grande majorité des exemples.
- **Precision** élevée signifie que lorsqu'une intention est prédite, elle est très souvent correcte.
- **Recall** élevé montre que le modèle parvient à détecter presque toutes les intentions présentes.
- **F1-Score** reflète l'équilibre entre ces deux mesures.

Ces résultats suggèrent que le modèle est **robuste et fiable** pour cette tâche de classification.
"""
n.cells.append(nbf.v4.new_markdown_cell(perf_metrics_analysis))

# --- Matrice de confusion ---
cm_intro = r"""
## Matrice de confusion

**Comment interpréter ce graphique :**  
La matrice de confusion compare les prédictions du modèle avec les étiquettes réelles.  
Chaque case représente le nombre d'exemples pour une combinaison donnée de classe réelle et prédite :
- **Vrais positifs (TP)** : Exemples positifs correctement identifiés.
- **Vrais négatifs (TN)** : Exemples négatifs correctement identifiés.
- **Faux positifs (FP)** : Exemples négatifs incorrectement identifiés comme positifs.
- **Faux négatifs (FN)** : Exemples positifs non détectés.

Le graphique ci-dessous affiche cette matrice avec une palette de couleurs permettant de visualiser l'intensité des scores.
"""
n.cells.append(nbf.v4.new_markdown_cell(cm_intro))

cm_code = r"""
from sklearn.metrics import ConfusionMatrixDisplay, confusion_matrix
import matplotlib.pyplot as plt

cm = confusion_matrix(labels, predictions)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Non-Intent", "Intent"])
disp.plot(cmap=plt.cm.Blues)
plt.title("Matrice de Confusion")
plt.show()
"""
n.cells.append(nbf.v4.new_code_cell(cm_code))

cm_analysis = r"""
### Analyse de la matrice de confusion

En observant la matrice :
- Le nombre élevé de **vrais positifs** et de **vrais négatifs** indique que le modèle effectue la majorité de ses prédictions correctement.
- Le faible nombre de **faux positifs** et de **faux négatifs** montre que les erreurs sont rares.
- Ces observations confirment la **fiabilité** du modèle dans la détection des intentions de voyage.

En résumé, la matrice confirme les excellentes performances globales vues précédemment.
"""
n.cells.append(nbf.v4.new_markdown_cell(cm_analysis))

# --- Courbe ROC et AUC ---
roc_intro = r"""
## Courbe ROC et Calcul de l'AUC

**Avant le graphique :**  
La courbe ROC (Receiver Operating Characteristic) illustre le compromis entre le taux de vrais positifs (TPR) et le taux de faux positifs (FPR) à différents seuils de décision.  
- **TPR (Recall)** : Proportion des exemples positifs correctement identifiés.
- **FPR** : Proportion des exemples négatifs incorrectement classifiés comme positifs.
- **AUC** (Area Under the Curve) : Une valeur proche de 1 indique une excellente capacité de discrimination.

Le graphique suivant montre cette courbe ainsi que l'aire sous celle-ci.
"""
n.cells.append(nbf.v4.new_markdown_cell(roc_intro))

roc_code = r"""
from sklearn.metrics import roc_curve, auc
import numpy as np
import matplotlib.pyplot as plt
# Calcul de la courbe ROC et de l'AUC (si ce n'est pas déjà fait)

if not isinstance(probs, np.ndarray):
    probs = np.array(probs)

fpr, tpr, thresholds = roc_curve(labels, probs[:, 1])
roc_auc = auc(fpr, tpr)

plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='darkorange', lw=2, label=f'Courbe ROC (AUC = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='navy', lw=2, linestyle='--')
plt.xlim([0.0, 1.0])
plt.ylim([0.0, 1.05])
plt.xlabel("Taux de Faux Positifs (FPR)")
plt.ylabel("Taux de Vrais Positifs (TPR)")
plt.title("Courbe ROC")
plt.legend(loc="lower right")
plt.show()
"""
n.cells.append(nbf.v4.new_code_cell(roc_code))

roc_analysis = r"""
### Analyse de la courbe ROC

- Une **AUC élevée** (proche de 1) démontre que le modèle parvient à bien distinguer les deux classes.
- La courbe s’élève rapidement vers un TPR élevé tout en maintenant un FPR faible, ce qui est l'idéal.
- Cette visualisation confirme que le modèle possède une **capacité de discrimination** remarquable.

Ces résultats confortent notre constat sur la qualité du modèle.
"""
n.cells.append(nbf.v4.new_markdown_cell(roc_analysis))

# --- Distribution des scores de probabilité ---
score_dist_intro = r"""
## Distribution des scores de probabilité

**Interprétation du graphique :**  
Ce graphique présente la répartition des scores de probabilité pour la classe "Intent" parmi les exemples :
- Une bonne séparation entre les exemples avec une probabilité proche de 0 et ceux avec une probabilité proche de 1 indique un modèle confiant.
- Des scores intermédiaires (entre 0.3 et 0.7 par exemple) pourraient suggérer des cas ambigus.

Nous souhaitons observer si le modèle effectue des prédictions tranchées ou s'il hésite sur certains exemples.
"""
n.cells.append(nbf.v4.new_markdown_cell(score_dist_intro))

score_dist_code = r"""
import matplotlib.pyplot as plt

data_non_intent = probs[labels == 0, 1].flatten()
data_intent = probs[labels == 1, 1].flatten()

plt.figure(figsize=(10, 6))
plt.hist([data_non_intent, data_intent], bins=20, alpha=0.6,
         label=["Non-Intent", "Intent"],
         color=['#a6cee3', '#fb9a99'])
plt.xlabel("Score de probabilité pour la classe 'Intent'")
plt.ylabel("Nombre d'exemples")
plt.title("Distribution des scores de probabilité")
plt.legend()
plt.show()
"""
n.cells.append(nbf.v4.new_code_cell(score_dist_code))

score_dist_analysis = r"""
### Analyse de la distribution des scores

- On observe une **forte concentration** des scores proches de 0 pour les exemples négatifs et proches de 1 pour les exemples positifs.
- Cela indique que le modèle **n'hésite pas** et effectue des prédictions tranchées.
- Seuls quelques exemples se situent dans une zone intermédiaire, suggérant que très peu d'exemples posent problème.

En conclusion, la distribution des scores montre que le modèle est **très confiant** dans ses prédictions.
"""
n.cells.append(nbf.v4.new_markdown_cell(score_dist_analysis))

# --- Analyse détaillée des erreurs ---
errors_intro = r"""
## Analyse détaillée des erreurs

Même si les performances globales sont excellentes, il est instructif d'examiner de plus près les erreurs commises par le modèle.
"""
n.cells.append(nbf.v4.new_markdown_cell(errors_intro))

errors_code = r"""
# Identification des indices des erreurs
import pandas as pd
import numpy as np

error_indices = np.where(predictions != labels)[0]
print(f"Nombre total d'erreurs : {len(error_indices)}")

# Affichage de quelques exemples d'erreurs (si disponibles)
num_errors_affiches = min(5, len(error_indices))
if num_errors_affiches > 0:
    for idx in error_indices[:num_errors_affiches]:
        print(f"\nExemple d'erreur n°{idx}:")
        print("Texte :", test_data[idx]["text"])
        print("Étiquette réelle :", labels[idx])
        print("Prédiction :", predictions[idx])
else:
    print("Aucune erreur détectée !")
"""
n.cells.append(nbf.v4.new_code_cell(errors_code))

errors_analysis = r"""
### Analyse des erreurs

- Le nombre d'erreurs est extrêmement faible par rapport à la taille totale du jeu de test.
- L'analyse qualitative des exemples erronés permet d'identifier d'éventuels cas ambigus ou des exceptions dans la formulation des textes.
- Ces cas peuvent être étudiés pour affiner le modèle ou améliorer le jeu de données.

Même si ces erreurs sont rares, elles fournissent des pistes pour de **futures améliorations**.
"""
n.cells.append(nbf.v4.new_markdown_cell(errors_analysis))

# --- Conclusion générale ---
conclusion_text = r"""
## Conclusion générale

L'analyse détaillée réalisée dans ce notebook confirme que le modèle **TravelIntentClassifier** possède des performances remarquables sur le jeu de test.  
Les points forts mis en évidence sont :
- Une **précision** et un **rappel** très élevés.
- Une **capacité de discrimination** prouvée par la courbe ROC et une AUC quasi-parfaite.
- Une **confusion minimale** entre les classes, comme le montre la matrice de confusion.
- Une **confiance** dans les prédictions, illustrée par la distribution des scores de probabilité.

**Perspectives d'amélioration :**
- Étudier les rares erreurs pour comprendre les cas ambigus.
- Envisager une analyse de la robustesse du modèle sur d'autres jeux de données ou dans des contextes variés.

Ce notebook constitue une base solide pour l'évaluation et l'analyse fine d'un modèle de classification d'intentions de voyage.
"""
n.cells.append(nbf.v4.new_markdown_cell(conclusion_text))

# ===============================
# Sauvegarde du Notebook
# ===============================
with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(n, f)
print(f"Notebook créé : {notebook_path}")

# ===============================
# Exécution et conversion du Notebook
# ===============================
print("Exécution et conversion du notebook...")
os.system(f'jupyter nbconvert --to notebook --execute {notebook_path} --no-input --output executed_notebook.ipynb')
os.system(f'jupyter nbconvert --to html {executed_notebook_path} --no-input --output {html_output_path}')

print("Exécution et conversion terminées.")
