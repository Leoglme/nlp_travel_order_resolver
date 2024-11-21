import os
import nbformat as nbf
import numpy as np
from transformers import CamembertTokenizerFast, CamembertForTokenClassification
from tqdm.auto import tqdm
import torch
from datasets import load_dataset

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
for text in tqdm(test_texts, desc="Predicting"):
    inputs = tokenizer(text, return_tensors="pt", padding=True, truncation=True)
    with torch.no_grad():
        logits = model(**inputs).logits
    predictions = np.argmax(logits.numpy(), axis=2)
    tokens = tokenizer.convert_ids_to_tokens(inputs["input_ids"][0].numpy())
    results.append({"text": text, "tokens": tokens, "predictions": predictions[0]})

# Create notebook
print("Creating notebook...")
n = nbf.v4.new_notebook()

# Add introduction
n.cells.append(nbf.v4.new_markdown_cell("# Évaluation du modèle Camembert NER"))
n.cells.append(nbf.v4.new_markdown_cell("""
Ce notebook évalue les performances du modèle `CamembertNERModel`, qui extrait les villes de départ (B-DEP, I-DEP)
et de destination (B-ARR, I-ARR) à partir des textes d'entrée. Les performances du modèle sont analysées en fonction
des métriques classiques et d'autres visualisations telles que la distribution des scores de confiance et des longueurs de texte.
"""))

# Add dataset overview
n.cells.append(nbf.v4.new_markdown_cell("## Aperçu des données de test"))
n.cells.append(nbf.v4.new_code_cell(f"""
from datasets import load_dataset

# Load dataset
dataset = load_dataset("csv", data_files={{"test": r"{test_dataset_path}"}})["test"]
dataset.to_pandas().head()
"""))

# Add predictions and token-level results
n.cells.append(nbf.v4.new_markdown_cell("## Résultats des prédictions au niveau des tokens"))
n.cells.append(nbf.v4.new_code_cell(f"""
import pandas as pd
import numpy as np

# Display predictions
results = {results}
df_results = pd.DataFrame(results)
df_results.head()
"""))

# Add histogram of confidence scores
n.cells.append(nbf.v4.new_markdown_cell("## Distribution des scores de confiance"))
n.cells.append(nbf.v4.new_markdown_cell("""
Ce graphique montre la distribution des scores de confiance pour chaque prédiction :
- **L'axe X** représente les scores de confiance.
- **L'axe Y** représente le nombre de prédictions ayant ce niveau de confiance.
"""))
n.cells.append(nbf.v4.new_code_cell("""
import matplotlib.pyplot as plt

# Extract confidences
confidences = [np.max(row["predictions"]) for row in results]
plt.figure(figsize=(10, 6))
plt.hist(confidences, bins=10, color='skyblue', alpha=0.7)
plt.title("Distribution des scores de confiance")
plt.xlabel("Score de confiance")
plt.ylabel("Nombre de prédictions")
plt.show()
"""))

# Add cumulative confidence plot
n.cells.append(nbf.v4.new_markdown_cell("## Courbe cumulative des scores de confiance"))
n.cells.append(nbf.v4.new_markdown_cell("""
Ce graphique montre la proportion cumulative des prédictions atteignant un certain score de confiance.
"""))
n.cells.append(nbf.v4.new_code_cell("""
sorted_confidences = sorted(confidences)
cumulative = np.cumsum(sorted_confidences) / sum(sorted_confidences)
plt.figure(figsize=(10, 6))
plt.plot(sorted_confidences, cumulative, color='blue')
plt.title("Courbe cumulative des scores de confiance")
plt.xlabel("Score de confiance")
plt.ylabel("Proportion cumulative")
plt.grid()
plt.show()
"""))

# Save notebook
if not os.path.exists(notebook_dir):
    os.makedirs(notebook_dir)

with open(notebook_path, 'w', encoding='utf-8') as f:
    nbf.write(n, f)
print(f"Notebook created: {notebook_path}")

# Execute and convert the notebook
print("Executing and converting notebook...")
os.system(f'jupyter nbconvert --to notebook --execute {notebook_path} --no-input --output executed_notebook.ipynb')
os.system(f'jupyter nbconvert --to html {executed_notebook_path} --no-input --output index.html')

print("Execution and conversion complete.")