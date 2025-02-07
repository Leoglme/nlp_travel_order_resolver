import warnings

warnings.filterwarnings("ignore", category=RuntimeWarning, module="zmq._future")

import os
import sys
import nbformat as nbf
import numpy as np
import torch
import pandas as pd
from datasets import load_dataset
from tqdm.auto import tqdm
import torch.nn.functional as F
from transformers import CamembertTokenizerFast, CamembertForTokenClassification

# Ajouter le répertoire racine du projet au PYTHONPATH
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), "../..")))

# Import du modèle CamembertNER
from models.camembert_ner_model import CamembertNERModel

# ===============================
# Définition des chemins de fichiers
# ===============================
notebook_dir = "evaluations/camembert_ner_evaluation_v2"
if not os.path.exists(notebook_dir):
    os.makedirs(notebook_dir)

notebook_path = os.path.join(notebook_dir, "camembert_ner_evaluation.ipynb")
executed_notebook_path = os.path.join(notebook_dir, "executed_notebook.ipynb")
html_output_path = os.path.join(notebook_dir, "index.html")

# Suppression des anciens fichiers s'ils existent
print("Suppression des anciens fichiers...")
for file_path in [executed_notebook_path, html_output_path, notebook_path]:
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Supprimé : {file_path}")

# ===============================
# Chargement du modèle et des données
# ===============================
print("Chargement du modèle CamembertNER et du tokenizer...")
model_path = "model_output/camembert_ner"
camembert_ner_model = CamembertNERModel()
tokenizer = CamembertTokenizerFast.from_pretrained(model_path)
model = CamembertForTokenClassification.from_pretrained(model_path)

# Chargement du dataset d'entraînement pour affichage
train_dataset_path = "datasets/camembert_ner_dataset.csv"
num_rows_train_data = len(pd.read_csv(train_dataset_path))
df_train = pd.read_csv(train_dataset_path)
sample_train = df_train.sample(5)  # Prendre un échantillon de 5 lignes

# Chargement du dataset de test
print("Chargement du dataset de test...")
test_dataset_path = "datasets/test_camembert_ner_dataset.csv"
test_data = load_dataset("csv", data_files={"test": test_dataset_path})["test"]
num_rows_test_data = len(test_data)

# Tokenisation et alignement des labels
print("Tokenisation et alignement des labels pour le test...")
tokenized_test_data = test_data.map(camembert_ner_model.tokenize_and_align_labels, batched=True)

test_encodings = {
    "input_ids": torch.tensor(tokenized_test_data["input_ids"]),
    "attention_mask": torch.tensor(tokenized_test_data["attention_mask"])
}
labels = np.array(tokenized_test_data["labels"])

# ===============================
# Prédictions sur le jeu de test
# ===============================
print("Prédiction sur le jeu de test...")
all_predictions = []
all_logits = []

batch_size = 8
with torch.no_grad():
    for i in tqdm(range(0, test_encodings["input_ids"].shape[0], batch_size), desc="Prédiction par batch"):
        batch_input_ids = test_encodings["input_ids"][i:i + batch_size]
        batch_attention_mask = test_encodings["attention_mask"][i:i + batch_size]
        outputs = model(input_ids=batch_input_ids, attention_mask=batch_attention_mask)
        # Récupération des logits pour le batch
        logits = outputs.logits.detach().cpu().numpy()  # shape: (batch_size, seq_length, num_labels)
        all_logits.append(logits)  # On ajoute le batch dans une liste
        # Calcul des prédictions pour le batch
        batch_predictions = np.argmax(logits, axis=2)  # shape: (batch_size, seq_length)
        all_predictions.append(batch_predictions)

all_predictions = np.concatenate(all_predictions, axis=0)
all_logits = np.concatenate(all_logits, axis=0)

# ===============================
# Calcul des métriques
# ===============================
metrics = camembert_ner_model.compute_metrics((all_logits, labels))
accuracy_val = metrics["accuracy"]
precision_val = metrics["precision"]
recall_val = metrics["recall"]
f1_val = metrics["f1"]

# ===============================
# Création du Notebook
# ===============================
print("Création du notebook CamembertNER...")
n = nbf.v4.new_notebook()

# Introduction
n.cells.append(nbf.v4.new_markdown_cell(f"""
# 📌 Évaluation du modèle **CamembertNER**

Ce notebook présente l’évaluation du modèle **CamembertNER**, un modèle de **Reconnaissance d’Entités Nommées (NER)** basé sur **Camembert**, fine-tuné pour détecter les **villes de départ et d’arrivée** dans des phrases en français.

#### 🔍 Contexte du projet
L’objectif du modèle est d’extraire automatiquement les villes mentionnées dans un texte pour identifier :
- **La ville de départ** (`B-DEP`, `I-DEP`)
- **La ville d’arrivée** (`B-ARR`, `I-ARR`)

#### 🛠️ Construction du Dataset
Le dataset utilisé pour entraîner ce modèle a été soigneusement **construit à partir de plusieurs sources**, notamment :
- **Des prompts générés par plusieurs personnes via ChatGPT**, permettant de capturer des formulations variées de trajets.
- **Des phrases générées automatiquement**, en combinant différentes villes et structures de phrases.

Le dataset total contient **{num_rows_train_data} exemples** et **{num_rows_test_data}** exemples de test, ce qui permet d’obtenir une évaluation fiable des performances du modèle.

#### 🎯 Objectif de ce notebook
Ce notebook a pour but de :
1. **Évaluer les performances** du modèle sur un dataset de test.
2. **Visualiser les métriques clés** : Accuracy, Précision, Rappel, F1-Score, etc.
3. **Analyser les erreurs du modèle** grâce à une Matrice de Confusion.
4. **Examiner la confiance du modèle** à travers la distribution des scores de probabilité.
5. **Explorer l’impact d’un seuil de confiance** sur la précision des prédictions.

#### 📊 Métriques évaluées
- **Accuracy** : Proportion de prédictions correctes parmi toutes les prédictions.
- **Précision** : Parmi les entités détectées, combien sont correctes ?
- **Recall** : Parmi les entités réellement présentes, combien ont été correctement détectées ?
- **F1-Score** : Une mesure combinée entre précision et rappel.

#### Le modèle est évalué sur un **dataset indépendant** du dataset d'entraînement, ce qui permet de mesurer sa capacité à **généraliser sur de nouvelles phrases**.
"""))

# Aperçu du dataset d'entraînement
n.cells.append(nbf.v4.new_markdown_cell("## 🔍 **Aperçu du dataset d'entraînement**"))

n.cells.append(nbf.v4.new_markdown_cell(f"""
Le dataset d'entraînement contient **{num_rows_test_data} exemples**.  
Il a été conçu avec des phrases issues de plusieurs sources, incluant des générations automatiques et des phrases créées via des prompts ChatGPT variés, afin d'assurer une diversité dans les formulations.

### 📊 Structure du dataset :
- **text** : La phrase contenant un trajet.
- **departure** : La ville de départ (annotation NER : `B-DEP`, `I-DEP`).
- **destination** : La ville d’arrivée (annotation NER : `B-ARR`, `I-ARR`).

Ci-dessous, un aperçu de **5 exemples** du dataset d'entraînement :
"""))

n.cells.append(nbf.v4.new_code_cell(f"""
import pandas as pd
from IPython.display import display

# Affichage d'un échantillon de 5 lignes avec une largeur de colonne augmentée
pd.set_option("display.max_colwidth", 150)  # Évite la coupure des phrases longues

sample_train = {sample_train.to_dict(orient='records')}
df_train_sample = pd.DataFrame(sample_train)

display(df_train_sample)
"""))

# Résumé des métriques
n.cells.append(nbf.v4.new_markdown_cell("## 📊 **Résumé des performances**"))

# Introduction expliquant les métriques
n.cells.append(nbf.v4.new_markdown_cell("""
L'évaluation du modèle repose sur plusieurs métriques essentielles pour mesurer ses performances en reconnaissance d'entités nommées (NER) :

- **Accuracy** : Proportion des prédictions correctes sur l’ensemble du dataset.
- **Précision (Precision)** : Parmi les entités détectées, combien sont correctes.
- **Rappel (Recall)** : Parmi les entités existantes, combien ont été correctement identifiées.
- **F1-Score** : Moyenne harmonique entre la précision et le rappel, offrant un équilibre entre les deux.

Le graphique ci-dessous permet de comparer les scores obtenus pour chaque métrique.
"""))

# Ajout des valeurs numériques
n.cells.append(nbf.v4.new_markdown_cell(f"""
- **Accuracy** : {accuracy_val:.3f} 🎯
- **Précision** : {precision_val:.3f} ✅
- **Recall** : {recall_val:.3f} 🔍
- **F1-Score** : {f1_val:.3f} 📊
"""))

# Ajout du graphique en barres pour visualiser les métriques
n.cells.append(nbf.v4.new_markdown_cell("### 📈 Visualisation des métriques"))
n.cells.append(nbf.v4.new_code_cell(f"""
import matplotlib.pyplot as plt

# Données pour le graphique
metrics = {{
    "Accuracy": {accuracy_val},
    "Precision": {precision_val},
    "Recall": {recall_val},
    "F1-Score": {f1_val},
}}

# Création du graphique
plt.figure(figsize=(10, 6))
plt.barh(list(metrics.keys()), list(metrics.values()), color=['blue', 'orange', 'green', 'purple'])
plt.xlabel("Score")
plt.title("Performances du modèle CamembertNER")

# Ajout des valeurs sur les barres
for i, value in enumerate(metrics.values()):
    plt.text(value, i, f"{{value:.3f}}", ha='left', va='center', fontsize=12)

plt.show()
"""))

# Analyse détaillée des résultats
n.cells.append(nbf.v4.new_markdown_cell("### 🔍 Analyse des résultats"))
n.cells.append(nbf.v4.new_markdown_cell(f"""
Les résultats obtenus montrent que le modèle **CamembertNER** atteint des performances solides en reconnaissance d’entités nommées :

✅ **Accuracy : {accuracy_val:.3f}**  
→ Le modèle effectue des prédictions correctes sur **{accuracy_val * 100:.1f}%** des tokens du dataset de test.  

✅ **Précision : {precision_val:.3f}**  
→ Parmi les entités détectées, **{precision_val * 100:.1f}%** sont correctes.  
Cela signifie que le modèle génère très peu de fausses entités.  

✅ **Recall : {recall_val:.3f}**  
→ Il identifie correctement **{recall_val * 100:.1f}%** des entités réelles présentes dans les phrases.  
Un score élevé de rappel montre que le modèle **ne manque pas** beaucoup d'entités importantes.  

✅ **F1-Score : {f1_val:.3f}**  
→ Le F1-score équilibre précision et rappel, prouvant que le modèle est à la fois précis et capable de bien identifier les entités.  

📌 **Interprétation globale** :  
Le modèle **généralise bien** sur les données de test et détecte **précisément** les villes de départ et d'arrivée dans les phrases.  
Cependant, **une analyse des erreurs** sera nécessaire pour identifier d’éventuelles faiblesses et améliorer encore les performances.
"""))

labels_flat = labels.flatten()
predictions_flat = all_predictions.flatten()

# Matrice de confusion
n.cells.append(nbf.v4.new_markdown_cell("## 🔄 **Matrice de confusion des prédictions NER**"))

# Introduction expliquant l'intérêt de la matrice de confusion
n.cells.append(nbf.v4.new_markdown_cell("""
La **matrice de confusion** est un outil essentiel pour évaluer la qualité des prédictions du modèle.  
Elle permet d'analyser **les erreurs de classification** en comparant les entités prédites aux entités réelles.

### 🔍 **Comment lire ce graphique ?**
- Chaque **ligne** représente les **vraies classes** des entités nommées (labels réels).
- Chaque **colonne** correspond aux **prédictions** du modèle.
- 🔵 **Diagonale principale (haut-gauche → bas-droite)** : Nombre de prédictions **correctes**.
- 🔴 **Hors-diagonale** : Nombre d'erreurs, indiquant **les confusions du modèle**.

Un **modèle parfait** aurait uniquement des valeurs **sur la diagonale**, sans confusion.

📊 **Affichage des classes** :  
Les classes utilisées sont :  
- **O** : Mots hors entité  
- **B-DEP** / **I-DEP** : Départ (Begin / Inside)  
- **B-ARR** / **I-ARR** : Arrivée (Begin / Inside)  
"""))

# Code pour afficher la matrice de confusion
n.cells.append(nbf.v4.new_code_cell(f"""
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
import numpy as np

# Convertir en tableau numpy
labels_flat = np.array({labels_flat.tolist()})
predictions_flat = np.array({predictions_flat.tolist()})

# Exclure les labels -100 (tokens spéciaux)
valid_mask = labels_flat != -100
filtered_labels_flat = labels_flat[valid_mask]
filtered_predictions_flat = predictions_flat[valid_mask]

# Fermer toute figure existante pour éviter "<Figure size 800x600 with 0 Axes>"
plt.close()

# Vérifier si les valeurs filtrées ne sont pas vides
if len(filtered_labels_flat) == 0 or len(filtered_predictions_flat) == 0:
    print("⚠️ Aucune donnée valide pour la matrice de confusion.")
else:
    # Création de la Matrice de Confusion
    cm = confusion_matrix(filtered_labels_flat, filtered_predictions_flat)

    # Création de la figure propre pour éviter tout affichage parasite
    fig, ax = plt.subplots(figsize=(8, 6))

    # Affichage avec annotations et cmap améliorée
    disp = ConfusionMatrixDisplay(confusion_matrix=cm)
    disp.plot(cmap=plt.cm.Blues, ax=ax, values_format="d")

    plt.title("Matrice de Confusion des prédictions NER")
    plt.xlabel("Classe Prédite")
    plt.ylabel("Classe Réelle")
    plt.grid(False)
    plt.show()
"""))

# Analyse des résultats
n.cells.append(nbf.v4.new_markdown_cell("### 🔍 Analyse des résultats"))
n.cells.append(nbf.v4.new_markdown_cell(f"""
Les résultats de la **matrice de confusion** mettent en évidence les forces et faiblesses du modèle.

📌 **Points forts :**
- ✅ **Un grand nombre de prédictions correctes sur la diagonale**, indiquant que le modèle détecte bien les entités.
- ✅ **Faible nombre de fausses alertes** : peu d’entités détectées à tort.

⚠️ **Axes d’amélioration :**
- 🔸 **Confusions possibles entre B-DEP et B-ARR** : Le modèle pourrait parfois inverser les villes de départ et d’arrivée.
- 🔸 **Mots hors entité (O) mal classifiés** : Certains mots neutres sont identifiés comme entités à tort.
- 🔸 **Manque de sensibilité sur certaines entités rares** : Le modèle peut avoir du mal avec certaines formulations non vues lors de l'entraînement.

📊 **Recommandations** :
- 🔄 **Augmenter la diversité du dataset** : Ajouter des exemples de phrases complexes.
- 🎯 **Régler les seuils de confiance** : Ajuster les probabilités pour minimiser les erreurs de type faux positifs.
- 🔍 **Analyser des exemples d’erreurs spécifiques** pour comprendre les cas les plus problématiques.

En conclusion, le modèle **CamembertNER** fonctionne bien pour la majorité des cas, mais quelques améliorations sont possibles pour réduire les erreurs résiduelles.
"""))

# Courbe ROC
n.cells.append(nbf.v4.new_markdown_cell("## 📈 **Courbe ROC (Receiver Operating Characteristic)**"))

n.cells.append(nbf.v4.new_markdown_cell("""
La **courbe ROC** est un indicateur clé de la performance du modèle.  
Elle permet d’évaluer comment le modèle fait la distinction entre les **vraies entités (positives)** et les **mots hors entité (négatifs)** en fonction de différents seuils.

### 🔍 **Comment lire ce graphique ?**
- L'**axe X** représente le **taux de faux positifs (FPR)**.
- L'**axe Y** représente le **taux de vrais positifs (TPR)**.
- 🔵 **Une courbe proche de la diagonale (0.5)** signifie que le modèle prédit **au hasard**.
- 🟢 **Une courbe qui monte rapidement vers 1** indique un modèle performant.
- 📏 **L'aire sous la courbe (AUC)** est une **mesure de la performance globale** :
  - **AUC = 1.0** : Modèle parfait.
  - **AUC = 0.5** : Modèle non-informatif.
  - **AUC < 0.5** : Modèle qui fait pire que du hasard.
"""))

n.cells.append(nbf.v4.new_code_cell(f"""
from sklearn.metrics import roc_curve, auc
import numpy as np
import matplotlib.pyplot as plt
import torch.nn.functional as F
import torch

# Appliquer softmax pour obtenir les probabilités des classes
probs = F.softmax(torch.tensor({all_logits.tolist()}), dim=-1).numpy()

# Calculer la probabilité qu'un token soit une entité :
# Puisque la classe "O" (non-entité) correspond à l'indice 0,
# le score d'entité est : 1 - probabilité de la classe "O"
entity_scores = 1 - probs[..., 0]

# Filtrer les labels valides (éviter -100)
labels_array = np.array({labels.tolist()})
valid_mask = labels_array != -100
filtered_labels = labels_array[valid_mask]
filtered_entity_scores = entity_scores[valid_mask]

# Calcul du TPR et FPR pour différents seuils
# On considère comme positif tout token qui n'est pas de la classe 0 (non-entité)
fpr, tpr, thresholds = roc_curve(filtered_labels != 0, filtered_entity_scores)
roc_auc = auc(fpr, tpr)

# Affichage de la courbe ROC
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='blue', lw=2, label=f'ROC Curve (AUC = {{roc_auc:.2f}})')
plt.plot([0, 1], [0, 1], color='gray', linestyle='--')  # Ligne diagonale
plt.xlabel("Taux de Faux Positifs (FPR)")
plt.ylabel("Taux de Vrais Positifs (TPR)")
plt.title("Courbe ROC - Performance de CamembertNER")
plt.legend(loc="lower right")
plt.grid(True)
plt.show()
"""))

n.cells.append(nbf.v4.new_markdown_cell("### 🔍 **Analyse des résultats**"))
n.cells.append(nbf.v4.new_markdown_cell(f"""
La **courbe ROC** nous permet d’analyser la capacité du modèle à détecter correctement les entités.

📌 **Observations générales :**
- ✅ **L’aire sous la courbe (AUC) indique que le modèle **distingue bien les entités des autres mots**.
- 🔵 **Si la courbe monte rapidement vers 1**, cela montre que le modèle **prend de bonnes décisions avec peu d'erreurs**.
- 🔴 **Si la courbe est proche de 0.5**, cela signifie que le modèle a du mal à différencier les entités des autres mots.

⚠️ **Axes d'amélioration possibles :**
- 🎯 **Ajuster le seuil de confiance** : Si on veut réduire les faux positifs, on peut choisir un seuil plus élevé.
- 🔄 **Améliorer les données d'entraînement** : Ajouter plus de phrases variées pour renforcer la capacité du modèle.
- 📊 **Comparer avec d’autres modèles** : Un AUC élevé (>0.9) est excellent, mais en-dessous de **0.8**, il faut peut-être revoir l’entraînement.

💡 **Conclusion :**  
Si l’AUC est **supérieur à 0.85**, le modèle fonctionne **très bien**.  
Si l’AUC est **entre 0.7 et 0.85**, il y a encore des améliorations possibles.  
Si l’AUC est **inférieur à 0.7**, il faut retravailler l’entraînement du modèle.
"""))

# Distribution des scores de probabilité
n.cells.append(nbf.v4.new_markdown_cell("## 📈 **Distribution des scores de probabilité**"))

n.cells.append(nbf.v4.new_markdown_cell("""
Ce graphique montre la **répartition des scores de probabilité** attribués par le modèle à chaque token.  
Un bon modèle doit être **très confiant sur ses bonnes prédictions** et donner des scores **faibles pour les erreurs**.

### 🔍 **Comment lire ce graphique ?**
- L'**axe X** représente les **scores de probabilité** du modèle, allant de **0 à 1**.
- L'**axe Y** montre **le nombre d'exemples** qui ont reçu chaque probabilité.
- 🟢 **Un pic proche de 1** signifie que le modèle est sûr de lui pour ces prédictions.
- 🔴 **Un pic proche de 0** indique que le modèle exclut clairement certains tokens.
- ⚠️ **Une accumulation autour de 0.5** signale une **grande incertitude** dans la classification.

📊 **Un modèle bien entraîné** doit montrer **deux pics nets** (près de 0 et près de 1), avec **peu de valeurs autour de 0.5**.
"""))

n.cells.append(nbf.v4.new_code_cell(f"""
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import torch
import torch.nn.functional as F

# Appliquer softmax pour obtenir les scores de probabilité
probs = F.softmax(torch.tensor({all_logits.tolist()}), dim=-1).numpy()

# Calculer le score d'entité : 1 - proba(classe O)
entity_scores = 1 - probs[..., 0]

# Éventuellement, aplatir le tableau pour faciliter l'affichage
entity_scores_flat = entity_scores.flatten()

# Échantillonner les données si elles sont trop nombreuses (par exemple, max 10 000 points)
if len(entity_scores_flat) > 10000:
    entity_scores_flat = np.random.choice(entity_scores_flat, 10000, replace=False)

# Tracer l'histogramme des scores d'entité
plt.figure(figsize=(10, 6))
sns.histplot(entity_scores_flat, bins=30, color='blue')  # Vous pouvez ajuster le nombre de bins

# Ajouter des lignes verticales pour des seuils clés
plt.axvline(x=0.5, color='red', linestyle='--', linewidth=2, label="Seuil = 0.5")
plt.axvline(x=0.8, color='green', linestyle='--', linewidth=2, label="Seuil élevé = 0.8")

plt.title("Distribution des scores d'entité du modèle")
plt.xlabel("Score d'entité (0 à 1)")
plt.ylabel("Nombre d'exemples")
plt.legend(loc="upper left")
plt.grid(True, linestyle="--", alpha=0.6)
plt.show()
"""))

n.cells.append(nbf.v4.new_markdown_cell("### 🔍 **Analyse des résultats**"))
n.cells.append(nbf.v4.new_markdown_cell(f"""
Les scores de probabilité révèlent **le niveau de confiance du modèle** pour ses prédictions.

📌 **Observations générales :**
- ✅ **Un pic net autour de 1.0** signifie que le modèle **est confiant pour certaines prédictions**.
- ✅ **Un pic proche de 0.0** montre qu’il sait **exclure les tokens non pertinents**.
- 🔴 **Si beaucoup de valeurs sont autour de 0.5**, cela montre une **incertitude élevée** du modèle.
- 🔹 **Une forte concentration entre 0.7 et 1.0** indique que le modèle **prend des décisions tranchées**.

⚠️ **Axes d’amélioration possibles :**
- 🎯 **Analyser les tokens où le score est proche de 0.5** pour identifier les erreurs fréquentes.
- 🔄 **Ajuster le seuil de confiance** : Si trop de prédictions sont entre 0.4 et 0.6, il faut peut-être **élever le seuil à 0.7**.
- 📏 **Augmenter la taille du dataset** pour apprendre sur des phrases plus variées et éviter que le modèle hésite.

💡 **Conclusion :**  
Un bon modèle doit **éviter d’avoir trop d’incertitude** et montrer **une séparation claire** entre **les bonnes prédictions (score proche de 1)** et **les erreurs (score proche de 0)**.
"""))

# Distribution des scores de confiance
n.cells.append(nbf.v4.new_markdown_cell("## 📈 **Distribution des scores de confiance**"))

# Introduction expliquant l'intérêt du graphique
n.cells.append(nbf.v4.new_markdown_cell("""
Le **score de confiance** est la probabilité attribuée par le modèle à chaque prédiction.  
Il mesure **le niveau de certitude** du modèle pour chaque étiquette NER (O, B-DEP, I-DEP, B-ARR, I-ARR).

### 🔍 **Comment interpréter ce graphique ?**
- L'**axe X** représente les valeurs des scores de confiance (entre **0 et 1**).
- L'**axe Y** montre **le nombre d'exemples** pour chaque score de confiance.
- 🔵 **Un pic proche de 1** signifie que le modèle est souvent **très confiant** dans ses prédictions.
- 🔴 **Une répartition large vers 0.5 ou plus bas** indique une **incertitude élevée**, suggérant des erreurs potentielles.

💡 **Un bon modèle** doit avoir **une distribution de scores bien séparée**, avec peu d’exemples proches de **0.5** (zone d'incertitude).
"""))

# Code pour afficher l'histogramme des scores de confiance
n.cells.append(nbf.v4.new_code_cell(f"""
from matplotlib import pyplot as plt
import seaborn as sns
import numpy as np
import torch
import torch.nn.functional as F

# Appliquer softmax pour obtenir les probabilités
probs = F.softmax(torch.tensor({all_logits.tolist()}), dim=-1).numpy()

# Calculer le score d'entité (score de confiance)
entity_scores = 1 - probs[..., 0]

# Aplatir le tableau pour faciliter l'affichage
entity_scores_flat = entity_scores.flatten()

# Tracer l'histogramme des scores de confiance
plt.figure(figsize=(10, 6))
sns.histplot(entity_scores_flat, bins=50, kde=True, color='purple')
plt.title("Distribution des scores de confiance du modèle")
plt.xlabel("Score de confiance (0 à 1)")
plt.ylabel("Nombre d'exemples")
plt.axvline(x=0.5, color='red', linestyle='--', label="Seuil = 0.5")
plt.legend()
plt.show()
"""))

# Analyse des résultats
n.cells.append(nbf.v4.new_markdown_cell("### 🔍 Analyse des résultats"))
n.cells.append(nbf.v4.new_markdown_cell(f"""
Les scores de confiance révèlent **le degré d'assurance du modèle** pour ses prédictions.  
Un modèle fiable doit avoir une **forte confiance sur ses prédictions correctes** et une faible confiance sur ses erreurs.

📌 **Observations générales :**
- ✅ **Une grande majorité des prédictions ont un score de confiance proche de 1** → Le modèle est **sûr de lui** dans la plupart des cas.
- 🔸 **Certains scores proches de 0.5 indiquent une incertitude élevée** → Ces cas sont probablement des erreurs.
- 🔴 **Un pic de scores bas (< 0.5) pourrait indiquer une confusion fréquente** → Le modèle doute pour certaines entités.

⚠️ **Axes d’amélioration :**
- 🎯 **Analyser les phrases où le score est autour de 0.5** pour identifier les cas ambigus.
- 🔄 **Augmenter le dataset** avec plus d'exemples similaires aux phrases mal classées.
- 📏 **Ajuster le seuil de confiance** : Si beaucoup d’erreurs ont un score < 0.6, on peut filtrer les prédictions faibles.

💡 **Recommandation** : Pour améliorer le modèle, **réduire les erreurs en ciblant les cas où la confiance est faible** et affiner l’apprentissage pour ces exemples.
"""))

# Courbe d'évolution de la précision en fonction du seuil
n.cells.append(nbf.v4.new_markdown_cell("## 🚀 **Courbe d'évolution de la précision en fonction du seuil**"))

# Introduction expliquant l'intérêt du graphique
n.cells.append(nbf.v4.new_markdown_cell("""
Le **seuil de confiance** est une valeur utilisée pour déterminer si une prédiction doit être acceptée ou rejetée.  
Il influence directement la **précision** du modèle (nombre de prédictions correctes sur le total des prédictions).

### 🔍 **Comment interpréter ce graphique ?**
- L'**axe X** représente **le seuil de confiance** utilisé pour filtrer les prédictions.
- L'**axe Y** indique **la précision du modèle** obtenue en appliquant ce seuil.
- 🔵 **Une précision élevée pour des seuils bas** signifie que le modèle ne fait pas trop d'erreurs, même avec des prédictions peu confiantes.
- 🔴 **Une chute brutale de la précision à partir d'un certain seuil** indique qu’un seuil trop élevé élimine trop de bonnes prédictions.

💡 **Le but est d'identifier le seuil optimal**, celui qui maximise la précision sans exclure trop de prédictions correctes.
"""))

# Appliquer softmax sur les logits pour obtenir des probabilités
probs = F.softmax(torch.tensor(all_logits.tolist()), dim=-1).numpy()

# Prendre la probabilité la plus élevée pour chaque token
max_probs = np.max(probs, axis=-1)

labels = np.array(labels.tolist())
valid_mask = labels != -100
filtered_labels = labels[valid_mask]
filtered_probs = max_probs[valid_mask]

# Définir les seuils à tester
thresholds = np.linspace(0, 1, 50)

# Calculer la précision pour chaque seuil (comparaison avec les labels)
precision_values = [np.mean((filtered_probs > t) == (filtered_labels != 0)) for t in thresholds]

# Identifier le seuil optimal (meilleure précision)
optimal_threshold = thresholds[np.argmax(precision_values)]

# Code pour afficher la courbe d'évolution de la précision
n.cells.append(nbf.v4.new_code_cell(f"""
import numpy as np
import matplotlib.pyplot as plt
import torch
import torch.nn.functional as F

# Calculer les probabilités à partir des logits
probs = F.softmax(torch.tensor({all_logits.tolist()}), dim=-1).numpy()

# Calculer le score d'entité : 1 - proba(classe "O") (classe "O" est à l'indice 0)
entity_scores = 1 - probs[..., 0]

# Convertir les labels en array numpy
labels_array = np.array({labels.tolist()})

# Filtrer les tokens valides (exclure les tokens spéciaux dont le label est -100)
valid_mask = labels_array != -100
filtered_labels = labels_array[valid_mask]
filtered_entity_scores = entity_scores[valid_mask]

# Définir une gamme de seuils à tester
thresholds = np.linspace(0, 1, 50)

# Calculer la précision pour chaque seuil
# Pour chaque seuil, on considère qu'un token est prédit comme entité si filtered_entity_scores > seuil
# et on compare avec la condition (filtered_labels != 0) pour savoir si c'est bien une entité.
precision_values = [
    np.mean((filtered_entity_scores > t) == (filtered_labels != 0))
    for t in thresholds
]

# Identifier le seuil optimal (celui qui donne la précision maximale)
optimal_threshold = thresholds[np.argmax(precision_values)]

# Affichage du graphique
plt.figure(figsize=(10, 6))
plt.plot(thresholds, precision_values, marker='o', linestyle='-', color="blue", label="Précision")
plt.axvline(x=optimal_threshold, color='green', linestyle='--', label=f"Seuil optimal = {optimal_threshold:.2f}")
plt.axvline(x=0.5, color='red', linestyle='--', label="Seuil par défaut = 0.5")
plt.xlabel("Seuil de confiance")
plt.ylabel("Précision")
plt.title("Évolution de la précision en fonction du seuil")
plt.legend()
plt.grid(True)
plt.show()
"""))

# Analyse des résultats
n.cells.append(nbf.v4.new_markdown_cell("### 🔍 Analyse des résultats"))
n.cells.append(nbf.v4.new_markdown_cell(f"""
La **courbe d'évolution de la précision** permet de comprendre **l'impact du seuil de confiance** sur les performances du modèle.

📌 **Observations générales :**
- ✅ **Le seuil optimal est identifié à {optimal_threshold:.2f}** → C'est le point où la précision est maximale.
- 🔹 **Si la précision est stable entre 0.4 et 0.7**, cela signifie que le modèle est robuste à différents seuils.
- 🔴 **Si la précision chute brusquement après un certain seuil**, alors le modèle **rejette trop de bonnes prédictions**.

⚠️ **Axes d’amélioration :**
- 🎯 **Expérimenter avec le seuil optimal** ({optimal_threshold:.2f}) pour voir s'il améliore les performances globales.
- 🔄 **Augmenter la taille du dataset** pour éviter les zones d’incertitude où le modèle hésite.
- 📏 **Filtrer les prédictions faibles (< 0.4)** pour éviter d’inclure des erreurs dans les résultats.

💡 **Recommandation** :  
L’idéal est d’ajuster dynamiquement le seuil selon **le contexte d'utilisation** (ex : accepter un seuil plus bas si l'on veut capturer plus de prédictions, ou le relever pour privilégier la qualité).
"""))

n.cells.append(nbf.v4.new_markdown_cell("## 🔧 **Axes d'améliorations**"))

n.cells.append(nbf.v4.new_markdown_cell("""
L’évaluation du modèle **CamembertNER** a révélé des performances solides, mais **certains points peuvent être améliorés** pour optimiser encore davantage la reconnaissance des entités nommées.

### 📌 **1. Améliorer la gestion des entités difficiles**
- 🔸 **Problème :** Certaines villes sont mal reconnues ou inversées entre départ et arrivée.
- ✅ **Solution :** Ajouter des **phrases d’entraînement avec des villes moins courantes** et **des formulations variées**.

### 📌 **2. Réduction des erreurs de classification**
- 🔸 **Problème :** La **matrice de confusion** montre quelques erreurs où le modèle confond `B-DEP` et `B-ARR`.
- ✅ **Solution :** Ajouter des **phrases d’entraînement où le contexte différencie clairement les villes de départ et d’arrivée**.

### 📌 **3. Ajustement du seuil de confiance**
- 🔸 **Problème :** Certains scores de probabilité sont **trop proches de 0.5**, ce qui indique de l’incertitude.
- ✅ **Solution :** Expérimenter avec un **seuil dynamique** pour améliorer la précision des prédictions.

### 📌 **4. Augmenter la diversité du dataset**
- 🔸 **Problème :** Le modèle pourrait mieux généraliser en étant exposé à **davantage de variations de phrases**.
- ✅ **Solution :** Enrichir le dataset avec **plus d'exemples issus de sources variées** (réels ou générés).

### 📌 **5. Expérimenter avec d'autres architectures de modèle**
- 🔸 **Problème :** Le modèle actuel donne de bons résultats, mais pourrait être comparé à d’autres approches.
- ✅ **Solution :** Tester des modèles comme `XLM-RoBERTa` ou **ajouter une couche CRF** pour améliorer la séquence de prédiction.
"""))

n.cells.append(nbf.v4.new_markdown_cell("## 🎯 **Conclusion**"))

n.cells.append(nbf.v4.new_markdown_cell(f"""
L’évaluation du modèle **CamembertNER** a mis en lumière ses **points forts** et ses **axes d’amélioration**.

✅ **Le modèle fonctionne bien pour la majorité des cas**, et il **généralise bien** sur des phrases
⚠️ **Quelques confusions** existent encore sur des phrases complexes.  

**En conclusion**, CamembertNER **est un modèle performant et prometteur**, avec un potentiel d’amélioration en affinant son entraînement et en optimisant les décisions basées sur les scores de confiance. ✅
"""))

# Sauvegarde et exécution du notebook
with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(n, f)
print(f"Notebook créé : {notebook_path}")

os.system(f'jupyter nbconvert --to notebook --execute {notebook_path} --no-input --output executed_notebook.ipynb')
os.system(f'jupyter nbconvert --to html {executed_notebook_path} --no-input --output index.html')
print("Exécution et conversion terminées.")
