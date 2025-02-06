import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, module="zmq._future")

import os
import nbformat as nbf
import numpy as np
import torch
from transformers import CamembertTokenizerFast, CamembertForTokenClassification
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score, confusion_matrix
from datasets import load_dataset
from tqdm.auto import tqdm

# Paths
notebook_dir = "evaluations/camembert_ner_evaluation"
notebook_path = os.path.join(notebook_dir, "camembert_ner_evaluation.ipynb")
executed_notebook_path = os.path.join(notebook_dir, "executed_notebook.ipynb")
html_output_path = os.path.join(notebook_dir, "index.html")

test_dataset_path = "datasets/test_camembert_ner_dataset.csv"

# Delete existing files
print("Deleting old files...")
for file_path in [executed_notebook_path, html_output_path, notebook_path]:
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Deleted: {file_path}")

# Load model and tokenizer
print("Loading model and tokenizer...")
model_path = "model_output/camembert_ner"
model = CamembertForTokenClassification.from_pretrained(model_path)
tokenizer = CamembertTokenizerFast.from_pretrained(model_path)

# Load and prepare test data
print("Loading and preparing test data...")
test_data = load_dataset("csv", data_files={"test": test_dataset_path})["test"]
num_rows_test_data = len(test_data)

# Tokenize test data
print("Tokenizing data...")
tokenized_test_data = {"input_ids": [], "attention_mask": [], "label": []}
for example in tqdm(test_data, desc="Tokenizing"):
    tokenized = tokenizer(example["text"], padding="max_length", truncation=True)
    tokenized_test_data["input_ids"].append(tokenized["input_ids"])
    tokenized_test_data["attention_mask"].append(tokenized["attention_mask"])
    tokenized_test_data["label"].append(example["departure"] + " | " + example["destination"])

# Convert data to tensors
test_encodings = {
    key: torch.tensor(np.array(tokenized_test_data[key])) for key in ["input_ids", "attention_mask"]
}
labels = np.array(tokenized_test_data["label"])

# Make predictions with progress bar
print("Making predictions...")
batch_size = 16
predictions = []

for i in tqdm(range(0, len(labels), batch_size), desc="Predicting"):
    batch_input_ids = test_encodings["input_ids"][i:i + batch_size]
    batch_attention_mask = test_encodings["attention_mask"][i:i + batch_size]
    with torch.no_grad():
        outputs = model(input_ids=batch_input_ids, attention_mask=batch_attention_mask)
        batch_predictions = np.argmax(outputs.logits.numpy(), axis=2)
        predictions.extend(batch_predictions)

# Calculate metrics
label_list = ["O", "B-DEP", "B-ARR", "I-DEP", "I-ARR"]

# Convert predictions to label format
predictions = np.argmax(predictions, axis=2)

# Transformer les prédictions et labels en une liste plate (sans -100)
true_labels = []
true_predictions = []

for i in range(len(labels)):
    for j in range(len(labels[i])):
        if labels[i][j] != -100:  # Ignore les tokens spéciaux
            true_labels.append(label_list[labels[i][j]])
            true_predictions.append(label_list[predictions[i][j]])

# Calcul des métriques
accuracy = accuracy_score(true_labels, true_predictions)
precision = precision_score(true_labels, true_predictions, average="weighted")
recall = recall_score(true_labels, true_predictions, average="weighted")
f1 = f1_score(true_labels, true_predictions, average="weighted")

# Affichage des résultats
print(f"Accuracy: {accuracy:.3f}")
print(f"Precision: {precision:.3f}")
print(f"Recall: {recall:.3f}")
print(f"F1-Score: {f1:.3f}")

# Confusion Matrix
cm = confusion_matrix(labels, predictions)

# Create notebook
print("Creating notebook...")
n = nbf.v4.new_notebook()

# Add Introduction
n.cells.append(nbf.v4.new_markdown_cell("""
# 📌 Évaluation du modèle `CamembertNERModel`

Ce notebook présente l'évaluation du modèle **CamembertNERModel**, un modèle de reconnaissance d'entités nommées (NER) entraîné pour extraire **les villes de départ et d'arrivée** à partir de phrases en français.

Nous allons :
- Analyser la **précision du modèle**.
- Observer **les erreurs de classification** à travers une matrice de confusion.
- Étudier la **distribution des prédictions** et visualiser des exemples concrets.
"""))

# Display Accuracy, Precision, Recall, F1-Score
n.cells.append(nbf.v4.new_markdown_cell(f"""
## 📊 Principales métriques du modèle

- **Accuracy** : {accuracy:.3f}
- **Precision** : {precision:.3f}
- **Recall** : {recall:.3f}
- **F1-Score** : {f1:.3f}
"""))

# Confusion Matrix Visualization
n.cells.append(nbf.v4.new_markdown_cell("## 🔍 Matrice de confusion"))
n.cells.append(nbf.v4.new_code_cell("""
import seaborn as sns
import matplotlib.pyplot as plt

plt.figure(figsize=(8,6))
sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', xticklabels=['Non-Voyage', 'Voyage'], yticklabels=['Non-Voyage', 'Voyage'])
plt.xlabel("Prédictions")
plt.ylabel("Vérités")
plt.title("Matrice de Confusion")
plt.show()
"""))

n.cells.append(nbf.v4.new_markdown_cell("""
### 🔎 Interprétation de la matrice de confusion
- Une diagonale forte montre que le modèle classe bien les intentions de voyage.
- Les erreurs (hors diagonale) représentent des phrases mal classifiées.
"""))

# Save the notebook
if not os.path.exists(notebook_dir):
    os.makedirs(notebook_dir)

with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(n, f)
print(f"Notebook created: {notebook_path}")

# Execute the notebook and save it with outputs
print("Executing and converting notebook...")
os.system(f'jupyter nbconvert --to notebook --execute {notebook_path} --no-input --output executed_notebook.ipynb')

# Convert executed notebook to HTML
os.system(f'jupyter nbconvert --to html {executed_notebook_path} --no-input --output index.html')

print("Execution and conversion complete.")