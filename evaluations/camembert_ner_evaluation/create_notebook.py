# Import necessary libraries
import os
import json
import numpy as np
from tqdm.auto import tqdm
import torch
from transformers import CamembertTokenizerFast, CamembertForTokenClassification
from datasets import load_dataset
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, ConfusionMatrixDisplay, classification_report
import nbformat as nbf
import matplotlib.pyplot as plt
import asyncio

# Fix asyncio issue on Windows
if os.name == "nt":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

# Paths and constants
project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
notebook_dir = "evaluations/camembert_ner_evaluation"
notebook_path = os.path.join(notebook_dir, "camembert_ner_evaluation.ipynb")
executed_notebook_path = os.path.join(notebook_dir, "executed_notebook.ipynb")
html_output_path = os.path.join(notebook_dir, "index.html")
test_dataset_path = os.path.join(project_root, "datasets/camembert_ner_dataset.csv")
model_path = "model_output/camembert_ner"

# Define label mapping
label_list = ["O", "B-DEP", "B-ARR", "I-DEP", "I-ARR"]

# Clean old files
print("Deleting old files...")
for file_path in [notebook_path, executed_notebook_path, html_output_path]:
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Deleted: {file_path}")

# Load model and tokenizer
print("Loading model and tokenizer...")
tokenizer = CamembertTokenizerFast.from_pretrained(model_path)
model = CamembertForTokenClassification.from_pretrained(model_path)

# Load test dataset
print("Loading and preparing test data...")
if not os.path.exists(test_dataset_path):
    raise FileNotFoundError(f"Dataset file not found: {test_dataset_path}")

dataset = load_dataset("csv", data_files={"test": test_dataset_path})["test"]

def tokenize_and_align_labels(examples):
    tokenized_inputs = tokenizer(examples["text"], padding="max_length", truncation=True, is_split_into_words=False)
    labels = []
    for i, (text, departure, destination) in enumerate(zip(examples["text"], examples["departure"], examples["destination"])):
        word_ids = tokenized_inputs.word_ids(batch_index=i)
        label_ids = [-100] * len(word_ids)

        departure_tokens = tokenizer.tokenize(departure) if departure else []
        destination_tokens = tokenizer.tokenize(destination) if destination else []

        dep_idx, des_idx = 0, 0

        for idx, word_id in enumerate(word_ids):
            if word_id is None:
                continue
            token = tokenized_inputs.tokens(batch_index=i)[idx]
            if token in ["<s>", "</s>", "<pad>"]:
                continue
            if dep_idx < len(departure_tokens) and token == departure_tokens[dep_idx]:
                label_ids[idx] = 1 if dep_idx == 0 else 3
                dep_idx += 1
            elif des_idx < len(destination_tokens) and token == destination_tokens[des_idx]:
                label_ids[idx] = 2 if des_idx == 0 else 4
                des_idx += 1
            else:
                label_ids[idx] = 0
        labels.append(label_ids)
    tokenized_inputs["labels"] = labels
    return tokenized_inputs

# Tokenize and align dataset
tokenized_dataset = dataset.map(tokenize_and_align_labels, batched=True)
test_texts = dataset["text"]
test_labels = tokenized_dataset["labels"]

# Predict and collect results
print("Making predictions...")
results = []
all_true_labels = []
all_predicted_labels = []

for i, text in enumerate(tqdm(test_texts, desc="Predicting")):
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

# Validate alignment of labels
if len(all_true_labels) != len(all_predicted_labels):
    raise ValueError("Filtered label lengths are inconsistent!")

# Calculate performance metrics
accuracy = accuracy_score(all_true_labels, all_predicted_labels)
precision = precision_score(all_true_labels, all_predicted_labels, average="weighted", zero_division=0)
recall = recall_score(all_true_labels, all_predicted_labels, average="weighted", zero_division=0)
f1 = f1_score(all_true_labels, all_predicted_labels, average="weighted", zero_division=0)
metrics = {"Accuracy": accuracy, "Precision": precision, "Recall": recall, "F1-Score": f1}

# Classification report
classification_rep = classification_report(all_true_labels, all_predicted_labels, target_names=label_list, zero_division=0)

# Serialize results
results_serialized = json.dumps(results)
true_labels_serialized = json.dumps(all_true_labels)
predicted_labels_serialized = json.dumps(all_predicted_labels)
metrics_serialized = json.dumps(metrics)

# Create notebook
n = nbf.v4.new_notebook()

# Add introduction and label description
n.cells.append(nbf.v4.new_markdown_cell("# Évaluation du modèle Camembert NER"))
n.cells.append(nbf.v4.new_markdown_cell("""
Ce notebook présente l'évaluation du modèle NER Camembert pour la détection des entités suivantes :

- **O** : Aucun intérêt, non lié à une ville.
- **B-DEP** : Début d'une ville de départ.
- **B-ARR** : Début d'une ville de destination.
- **I-DEP** : Continuation d'une ville de départ.
- **I-ARR** : Continuation d'une ville de destination.
"""))

# Add metrics visualization
n.cells.append(nbf.v4.new_markdown_cell("## Visualisation des métriques de performance"))
n.cells.append(nbf.v4.new_code_cell(f"""
import matplotlib.pyplot as plt
import json

metrics = json.loads('''{metrics_serialized}''')

plt.figure(figsize=(10, 6))
plt.barh(list(metrics.keys()), list(metrics.values()), color=['skyblue', 'orange', 'green', 'purple'])
plt.xlabel("Score")
plt.title("Métriques de performance")
for i, (key, value) in enumerate(metrics.items()):
    plt.text(value, i, f"{{value:.2f}}")
plt.show()
"""))

# Add confusion matrix
n.cells.append(nbf.v4.new_markdown_cell("## Matrice de confusion"))
n.cells.append(nbf.v4.new_markdown_cell("""
La matrice de confusion compare les prédictions du modèle avec les étiquettes réelles :

- Les **lignes** correspondent aux étiquettes réelles (ce que le modèle devait prédire).
- Les **colonnes** correspondent aux étiquettes prédites (ce que le modèle a réellement prédit).
- La diagonale principale montre les prédictions correctes.
"""))
n.cells.append(nbf.v4.new_code_cell(f"""
import json
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt

all_true_labels = json.loads('''{true_labels_serialized}''')
all_predicted_labels = json.loads('''{predicted_labels_serialized}''')

classes = {label_list}
cm = confusion_matrix(all_true_labels, all_predicted_labels, labels=range(len(classes)))
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=classes)
disp.plot(cmap=plt.cm.Blues)
plt.title("Matrice de confusion")
plt.xlabel("Étiquettes prédites")
plt.ylabel("Étiquettes réelles")
plt.show()
"""))

# Add distribution plot
n.cells.append(nbf.v4.new_markdown_cell("## Distribution des classes"))
n.cells.append(nbf.v4.new_markdown_cell("""
Ce graphique montre la répartition des classes dans les étiquettes réelles et prédites :

- **Axe X** : Les différentes classes (`O`, `B-DEP`, etc.).
- **Axe Y** : Le nombre de tokens dans chaque classe.
- Les barres permettent de comparer la répartition entre les étiquettes réelles et prédites.
"""))
n.cells.append(nbf.v4.new_code_cell(f"""
from collections import Counter

true_counts = Counter(all_true_labels)
predicted_counts = Counter(all_predicted_labels)

true_values = [true_counts.get(i, 0) for i in range(len(classes))]
predicted_values = [predicted_counts.get(i, 0) for i in range(len(classes))]

x = range(len(classes))
plt.bar(x, true_values, width=0.4, label="Étiquettes réelles", align="center")
plt.bar([p + 0.4 for p in x], predicted_values, width=0.4, label="Étiquettes prédites", align="center")
plt.xticks([p + 0.2 for p in x], classes)
plt.xlabel("Classes")
plt.ylabel("Nombre de tokens")
plt.legend()
plt.title("Distribution des classes dans les étiquettes réelles et prédites")
plt.show()
"""))

# Add F1-score per class
n.cells.append(nbf.v4.new_markdown_cell("## F1-Score par classe"))
n.cells.append(nbf.v4.new_markdown_cell("""
Le F1-score par classe combine précision et rappel pour chaque classe :

- **Axe X** : Les différentes classes (`O`, `B-DEP`, etc.).
- **Axe Y** : Le score F1 (entre 0 et 1).
- Plus le score F1 est proche de 1, meilleures sont les prédictions pour cette classe.
"""))
n.cells.append(nbf.v4.new_code_cell(f"""
from sklearn.metrics import classification_report
import matplotlib.pyplot as plt

report = classification_report(all_true_labels, all_predicted_labels, target_names=classes, zero_division=0, output_dict=True)
f1_scores = [report[cls]["f1-score"] for cls in classes]

plt.bar(classes, f1_scores, color='blue')
plt.xlabel("Classes")
plt.ylabel("F1-Score")
plt.title("F1-Score par classe")
plt.ylim(0, 1)
plt.show()
"""))

# Add ROC curve
n.cells.append(nbf.v4.new_markdown_cell("## Courbe ROC"))
n.cells.append(nbf.v4.new_markdown_cell("""
La courbe ROC évalue la capacité du modèle à discriminer entre les classes.

- **Axe X** : Taux de faux positifs (FPR).
- **Axe Y** : Taux de vrais positifs (TPR).
- Une courbe proche de la diagonale indique une mauvaise séparation des classes.
- L'AUC (Area Under Curve) mesure l'efficacité globale (1 = parfait, 0.5 = aléatoire).
"""))
n.cells.append(nbf.v4.new_code_cell("""
from sklearn.metrics import roc_curve, auc
import numpy as np
import matplotlib.pyplot as plt

# Conversion des étiquettes en un format binaire pour le ROC
true_labels_bin = np.array([1 if label in [1, 3] else 0 for label in all_true_labels])  # B-DEP/I-DEP comme positifs
predicted_labels_bin = np.array([1 if label in [1, 3] else 0 for label in all_predicted_labels])

try:
    fpr, tpr, _ = roc_curve(true_labels_bin, predicted_labels_bin)
    roc_auc = auc(fpr, tpr)
    plt.figure(figsize=(10, 6))
    plt.plot(fpr, tpr, color='blue', label=f"ROC Curve (AUC = {roc_auc:.2f})")
    plt.plot([0, 1], [0, 1], color="gray", linestyle="--")
    plt.xlabel("Taux de faux positifs (FPR)")
    plt.ylabel("Taux de vrais positifs (TPR)")
    plt.title("Courbe ROC")
    plt.legend()
    plt.grid()
    plt.show()
except ValueError as e:
    print(f"Erreur lors de la génération de la courbe ROC : {e}")
"""))

# Add initialization cell to define test_texts
n.cells.append(nbf.v4.new_code_cell(f"""
import json

# Charger les données nécessaires pour le notebook
test_texts = json.loads('''{json.dumps(test_texts)}''')
"""))

# Add sentence length histogram
n.cells.append(nbf.v4.new_markdown_cell("## Distribution des longueurs des phrases"))
n.cells.append(nbf.v4.new_markdown_cell("""
Ce graphique montre la distribution des longueurs des phrases dans le dataset.

- **Axe X** : Longueur des phrases (en tokens).
- **Axe Y** : Nombre de phrases ayant cette longueur.
- Ce graphique permet de vérifier si les performances du modèle varient en fonction de la complexité (longueur) des phrases.
"""))
n.cells.append(nbf.v4.new_code_cell("""
import matplotlib.pyplot as plt

# Calculer les longueurs des phrases
sentence_lengths = [len(text.split()) for text in test_texts]

# Tracer l'histogramme
plt.figure(figsize=(10, 6))
plt.hist(sentence_lengths, bins=30, color="skyblue", edgecolor="black")
plt.xlabel("Longueur des phrases (tokens)")
plt.ylabel("Nombre de phrases")
plt.title("Distribution des longueurs des phrases")
plt.grid()
plt.show()
"""))

if not os.path.exists(notebook_dir):
    os.makedirs(notebook_dir)

with open(notebook_path, "w", encoding="utf-8") as f:
    nbf.write(n, f)

print(f"Notebook created: {notebook_path}")
os.system(f'jupyter nbconvert --to notebook --execute {notebook_path} --no-input --output executed_notebook.ipynb')
os.system(f'jupyter nbconvert --to html {executed_notebook_path} --no-input --output index.html')
print("Notebook execution and conversion to HTML completed.")