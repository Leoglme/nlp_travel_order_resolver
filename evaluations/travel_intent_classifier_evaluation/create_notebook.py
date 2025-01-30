import warnings
warnings.filterwarnings("ignore", category=RuntimeWarning, module="zmq._future")

import os
import nbformat as nbf
import numpy as np
import torch
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score, confusion_matrix, roc_curve, auc
from datasets import load_dataset
from tqdm.auto import tqdm

# Paths
notebook_dir = "evaluations/travel_intent_classifier_evaluation"
notebook_path = os.path.join(notebook_dir, "travel_intent_classifier_evaluation.ipynb")
executed_notebook_path = os.path.join(notebook_dir, "executed_notebook.ipynb")
html_output_path = os.path.join(notebook_dir, "index.html")

# Delete existing files
print("Deleting old files...")
for file_path in [executed_notebook_path, html_output_path, notebook_path]:
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Deleted: {file_path}")

# Load model and tokenizer
print("Loading model and tokenizer...")
model_path = "model_output/travel_intent_classifier"
model = DistilBertForSequenceClassification.from_pretrained(model_path)
tokenizer = DistilBertTokenizerFast.from_pretrained(model_path)

# Load and prepare test data
print("Loading and preparing test data...")
test_dataset_path = "datasets/test_travel_intent_dataset.csv"
test_data = load_dataset("csv", data_files={"test": test_dataset_path})["test"]
num_rows_test_data = len(test_data)

# Tokenize test data
print("Tokenizing data...")
tokenized_test_data = {"input_ids": [], "attention_mask": [], "label": []}
for example in tqdm(test_data, desc="Tokenizing"):
    tokenized = tokenizer(example["text"], padding="max_length", truncation=True)
    tokenized_test_data["input_ids"].append(tokenized["input_ids"])
    tokenized_test_data["attention_mask"].append(tokenized["attention_mask"])
    tokenized_test_data["label"].append(example["label"])

# Convert data to tensors
print("Converting data to tensors...")
test_encodings = {
    key: torch.tensor(np.array(tokenized_test_data[key])) for key in ["input_ids", "attention_mask"]
}
labels = np.array(tokenized_test_data["label"])

# Make predictions with progress bar
print("Making predictions...")
batch_size = 32
predictions = []
probs = []

for i in tqdm(range(0, len(labels), batch_size), desc="Predicting"):
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

# Calculate metrics
accuracy = accuracy_score(labels, predictions)
precision = precision_score(labels, predictions, average="weighted")
recall = recall_score(labels, predictions, average="weighted")
f1 = f1_score(labels, predictions, average="weighted")

# Debug: Print confusion matrix
cm = confusion_matrix(labels, predictions)
print(f"Confusion matrix:\n{cm}")

# Create notebook
print("Creating notebook...")
n = nbf.v4.new_notebook()

# Add content to notebook
n.cells.append(nbf.v4.new_markdown_cell(f"# Évaluation du modèle `TravelIntentClassifier`"))
n.cells.append(nbf.v4.new_markdown_cell(f"### Ce notebook évalue les performances d'un modèle de classification des intentions. "
                                        "Il est basé sur un modèle DistilBERT fine-tuné sur un ensemble de données de "
                                        "textes annotés pour la classification des intentions de voyage. "
                                        f"Le modèle est évalué sur un dataset de test de {num_rows_test_data} lignes."))
# Display accuracy, precision, recall, f1-score
n.cells.append(nbf.v4.new_markdown_cell(f"""
- Accuracy: {accuracy}
- Precision: {precision}
- Recall: {recall}
- F1-Score: {f1}
"""))
n.cells.append(nbf.v4.new_code_cell(f"""
# Evaluation Results
accuracy = {accuracy}
precision = {precision}
recall = {recall}
f1 = {f1}
predictions = {list(predictions)}
labels = {list(labels)}
probs = {probs.tolist()}
"""))

# Performance Metrics Graph
n.cells.append(nbf.v4.new_markdown_cell("## Visualisation des métriques de performance"))
n.cells.append(nbf.v4.new_markdown_cell("""
Ce graphique en barres montre les métriques de performance du modèle :
- **Précision (Accuracy)** : La proportion des prédictions correctes.
- **Précision (Precision)** : Parmi les cas prédits comme positifs, combien sont corrects.
- **Rappel (Recall)** : Parmi les cas réellement positifs, combien ont été correctement identifiés.
- **Score F1** : Une moyenne harmonique entre la précision et le rappel, équilibrant les deux.
"""))

n.cells.append(nbf.v4.new_code_cell("""
import matplotlib.pyplot as plt

metrics = {
    "Accuracy": accuracy,
    "Precision": precision,
    "Recall": recall,
    "F1-Score": f1,
}

plt.figure(figsize=(10, 6))
plt.barh(list(metrics.keys()), list(metrics.values()), color=['skyblue', 'orange', 'green', 'purple'])
plt.xlabel("Score")
plt.title("Model Performance Metrics")
for i, value in enumerate(metrics.values()):
    plt.text(value, i, f"{value:.2f}")
plt.show()
"""))

# Confusion Matrix
n.cells.append(nbf.v4.new_markdown_cell("## Matrice de confusion"))
n.cells.append(nbf.v4.new_markdown_cell("""
La matrice de confusion compare les prédictions du modèle avec les étiquettes réelles :
- **Vrais positifs (TP)** : Cas positifs correctement prédits.
- **Vrais négatifs (TN)** : Cas négatifs correctement prédits.
- **Faux positifs (FP)** : Cas négatifs incorrectement prédits comme positifs.
- **Faux négatifs (FN)** : Cas positifs incorrectement prédits comme négatifs.
"""))
n.cells.append(nbf.v4.new_code_cell("""
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

cm = confusion_matrix(labels, predictions)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Non-Intent", "Intent"])
disp.plot(cmap=plt.cm.Blues)
plt.title("Confusion Matrix")
plt.show()
"""))

# ROC Curve
n.cells.append(nbf.v4.new_markdown_cell("## Courbe ROC"))
n.cells.append(nbf.v4.new_markdown_cell("""
La courbe ROC illustre le compromis entre le taux de vrais positifs (**Recall**) et le taux de faux positifs à différents seuils :
- **Taux de vrais positifs (TPR)** : Proportion des vrais cas positifs correctement identifiés.
- **Taux de faux positifs (FPR)** : Proportion des cas négatifs incorrectement classés comme positifs.
- **AUC (Surface sous la courbe)** : Représente la capacité globale du modèle à discriminer entre classes. Une valeur proche de 1 indique de meilleures performances.
"""))
n.cells.append(nbf.v4.new_code_cell("""
from sklearn.metrics import roc_curve, auc
import numpy as np
import matplotlib.pyplot as plt

if not isinstance(probs, np.ndarray):
    probs = np.array(probs)

# Calculate False Positive Rate, True Positive Rate, and AUC
fpr, tpr, thresholds = roc_curve(labels, probs[:, 1])
roc_auc = auc(fpr, tpr)

# Plot ROC Curve
plt.figure(figsize=(8, 6))
plt.plot(fpr, tpr, color='blue', lw=2, label=f'ROC Curve (AUC = {roc_auc:.2f})')
plt.plot([0, 1], [0, 1], color='gray', linestyle='--')
plt.xlabel("False Positive Rate (FPR)")
plt.ylabel("True Positive Rate (TPR)")
plt.title("ROC Curve")
plt.legend(loc="lower right")
plt.show()
"""))

# Prediction Scores Distribution
n.cells.append(nbf.v4.new_markdown_cell("## Distribution des scores de probabilité"))
n.cells.append(nbf.v4.new_markdown_cell("""
Ce graphique montre la distribution des scores de probabilité pour chaque classe :
- **Non-Intention** : Scores pour les exemples classés comme "Non-Intention".
- **Intention** : Scores pour les exemples classés comme "Intention".
Une bonne séparation entre les deux classes est souhaitable pour un modèle performant.
"""))
n.cells.append(nbf.v4.new_code_cell("""
import numpy as np
import matplotlib.pyplot as plt

if not isinstance(labels, np.ndarray):
    labels = np.array(labels)
if not isinstance(probs, np.ndarray):
    probs = np.array(probs)

plt.figure(figsize=(10, 6))
plt.hist(probs[labels == 0, 1], bins=20, alpha=0.6, label="Non-Intent")
plt.hist(probs[labels == 1, 1], bins=20, alpha=0.6, label="Intent")
plt.xlabel("Probability Score")
plt.ylabel("Number of Examples")
plt.title("Distribution of Prediction Scores")
plt.legend()
plt.show()
"""))

# Save the notebook
with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(n, f)
print(f"Notebook created: {notebook_path}")

# Execute the notebook and save it with outputs
print("Executing and converting notebook...")
os.system(f'jupyter nbconvert --to notebook --execute {notebook_path} --no-input --output executed_notebook.ipynb')

# Convert executed notebook to HTML
os.system(f'jupyter nbconvert --to html {executed_notebook_path} --no-input --output index.html')

print("Execution and conversion complete.")