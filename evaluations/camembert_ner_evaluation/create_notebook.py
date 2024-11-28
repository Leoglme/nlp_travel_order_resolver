import os
import nbformat as nbf
import numpy as np
from transformers import CamembertTokenizerFast, CamembertForTokenClassification
from tqdm.auto import tqdm
import torch
from datasets import load_dataset
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, roc_curve, auc
import json

project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))

# Paths
notebook_dir = "evaluations/camembert_ner_evaluation"
notebook_path = os.path.join(notebook_dir, "camembert_ner_evaluation.ipynb")
executed_notebook_path = os.path.join(notebook_dir, "executed_notebook.ipynb")
html_output_path = os.path.join(notebook_dir, "index.html")
test_dataset_path = os.path.join(project_root, "datasets/camembert_ner_dataset.csv")
model_path = "model_output/camembert_ner"

# Delete existing files
print("Deleting old files...")
for file_path in [executed_notebook_path, html_output_path, notebook_path]:
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Deleted: {file_path}")

# Load model and tokenizer
print("Loading model and tokenizer...")
tokenizer = CamembertTokenizerFast.from_pretrained(model_path)
model = CamembertForTokenClassification.from_pretrained(model_path)

# Load dataset using `load_dataset`
print("Loading and preparing test data...")
if not os.path.exists(test_dataset_path):
    raise FileNotFoundError(f"Dataset file not found: {test_dataset_path}")

dataset = load_dataset("csv", data_files={"test": test_dataset_path})["test"]
test_texts = dataset["text"]

# Predict and collect results
print("Making predictions...")
results = []
all_true_labels = []  # To store true labels for metrics calculation
all_predicted_labels = []  # To store predicted labels for metrics calculation

for text in tqdm(test_texts, desc="Predicting"):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        logits = model(**inputs).logits
    predictions = np.argmax(logits.numpy(), axis=2)
    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0].numpy())
    true_labels = [0] * len(tokens)  # Replace this with actual labels if available
    all_true_labels.extend(true_labels)
    all_predicted_labels.extend(predictions[0])
    results.append({"text": text, "tokens": tokens, "predictions": predictions[0]})

# Calculate performance metrics
accuracy = accuracy_score(all_true_labels, all_predicted_labels)
precision = precision_score(all_true_labels, all_predicted_labels, average="weighted", zero_division=0)
recall = recall_score(all_true_labels, all_predicted_labels, average="weighted", zero_division=0)
f1 = f1_score(all_true_labels, all_predicted_labels, average="weighted", zero_division=0)
metrics = {"Accuracy": accuracy, "Precision": precision, "Recall": recall, "F1-Score": f1}

# Serialize results
results_serialized = json.dumps([
    {
        key: (value.tolist() if isinstance(value, (np.ndarray, np.generic)) else value)
        for key, value in row.items()
    }
    for row in results
])

# Create notebook
print("Creating notebook...")
n = nbf.v4.new_notebook()

# Add introduction
n.cells.append(nbf.v4.new_markdown_cell("# Évaluation du modèle Camembert NER"))
n.cells.append(nbf.v4.new_markdown_cell("""
Ce notebook évalue les performances du modèle `CamembertNERModel`, qui extrait les villes de départ (B-DEP, I-DEP)
et de destination (B-ARR, I-ARR) à partir des textes d'entrée. Les performances sont analysées à l'aide de métriques,
de visualisations des prédictions et d'analyses détaillées.
"""))

# Add metrics visualization
metrics_serialized = json.dumps(metrics)
n.cells.append(nbf.v4.new_markdown_cell("## Visualisation des métriques de performance"))
n.cells.append(nbf.v4.new_code_cell(f"""
import matplotlib.pyplot as plt
import json

# Charger les métriques
metrics = json.loads('''{metrics_serialized}''')

# Visualiser les métriques
plt.figure(figsize=(10, 6))
plt.barh(list(metrics.keys()), list(metrics.values()), color=['skyblue', 'orange', 'green', 'purple'])
plt.xlabel("Score")
plt.title("Métriques de performance du modèle")
for i, (key, val) in enumerate(metrics.items()):
    plt.text(val, i, f"{{val:.2f}}", va='center')
plt.show()
"""))

# Confusion Matrix
all_true_labels = [int(label) for label in all_true_labels]
all_predicted_labels = [int(label) for label in all_predicted_labels]
true_labels_serialized = json.dumps(all_true_labels)
predicted_labels_serialized = json.dumps(all_predicted_labels)

n.cells.append(nbf.v4.new_markdown_cell("## Matrice de confusion"))
n.cells.append(nbf.v4.new_code_cell(f"""
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay
import matplotlib.pyplot as plt
import json

all_true_labels = json.loads('''{true_labels_serialized}''')
all_predicted_labels = json.loads('''{predicted_labels_serialized}''')

# Classes attendues
classes = sorted(set(all_true_labels + all_predicted_labels))
cm = confusion_matrix(all_true_labels, all_predicted_labels, labels=classes)

disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=classes)
disp.plot(cmap=plt.cm.Blues, xticks_rotation=45)
plt.title("Matrice de confusion")
plt.show()
"""))

# ROC Curve
n.cells.append(nbf.v4.new_markdown_cell("## Courbe ROC"))
n.cells.append(nbf.v4.new_code_cell("""
from sklearn.metrics import roc_curve, auc
import matplotlib.pyplot as plt
import warnings

# Vérifier s'il existe des échantillons positifs
if len(set(all_true_labels)) > 1:
    fpr, tpr, _ = roc_curve(all_true_labels, all_predicted_labels, pos_label=1)
    roc_auc = auc(fpr, tpr)

    plt.figure(figsize=(10, 6))
    plt.plot(fpr, tpr, color='blue', label=f"Courbe ROC (AUC = {roc_auc:.2f})")
    plt.plot([0, 1], [0, 1], color="gray", linestyle="--")
    plt.xlabel("Taux de faux positifs (FPR)")
    plt.ylabel("Taux de vrais positifs (TPR)")
    plt.title("Courbe ROC")
    plt.legend()
    plt.grid()
    plt.show()
else:
    warnings.warn("Pas de classes positives, courbe ROC non applicable.")
"""))

# Confidence Score Distribution
n.cells.append(nbf.v4.new_markdown_cell("## Distribution des scores de probabilité"))
n.cells.append(nbf.v4.new_code_cell(f"""
import matplotlib.pyplot as plt
import json

results = json.loads('''{results_serialized}''')

confidences = [max(row["predictions"]) for row in results]

plt.figure(figsize=(10, 6))
plt.hist(confidences, bins=20, color="orange", alpha=0.7)
plt.xlabel("Score de probabilité")
plt.ylabel("Nombre d'exemples")
plt.title("Distribution des scores de probabilité")
plt.show()
"""))

# Save notebook
if not os.path.exists(notebook_dir):
    os.makedirs(notebook_dir)

with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(n, f)

# Execute and convert notebook
os.system(f'jupyter nbconvert --to notebook --execute {notebook_path} --no-input --output executed_notebook.ipynb')
os.system(f'jupyter nbconvert --to html {executed_notebook_path} --no-input --output index.html')

print("Execution and conversion complete.")
