import os
import sys

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

import pandas as pd
import nbformat as nbf
from services.language_identifications import LanguageIdentification

# Paths
notebook_dir = "evaluations/language_identification_evaluation"
notebook_path = os.path.join(notebook_dir, "language_identification_evaluation.ipynb")
executed_notebook_path = os.path.join(notebook_dir, "executed_notebook.ipynb")
html_output_path = os.path.join(notebook_dir, "index.html")
test_dataset_path = "datasets/test_language_identification_dataset.csv"

# Delete existing files
print("Deleting old files...")
for file_path in [executed_notebook_path, html_output_path, notebook_path]:
    if os.path.exists(file_path):
        os.remove(file_path)
        print(f"Deleted: {file_path}")

# Initialize LanguageIdentification class
print("Loading language identification model...")
lang_identifier = LanguageIdentification()

# Load dataset
print("Loading test dataset...")
df = pd.read_csv(test_dataset_path)

# Evaluate model on dataset
results = []
for _, row in df.iterrows():
    text = row['Text']
    true_label = row['Language']
    try:
        predicted_label, confidence = lang_identifier.predict_lang_for_evaluation(text)
        results.append({
            "Text": text,
            "True Label": true_label,
            "Predicted Label": predicted_label[0].replace("__label__", ""),
            "Confidence": confidence[0]
        })
    except ValueError as e:
        results.append({
            "Text": text,
            "True Label": true_label,
            "Predicted Label": "Error",
            "Confidence": None,
            "Error": str(e)
        })

# Create notebook
print("Creating notebook...")
n = nbf.v4.new_notebook()

# Notebook content
n.cells.append(nbf.v4.new_markdown_cell("# Évaluation du modèle de détection de langues `LanguageIdentification`"))
n.cells.append(nbf.v4.new_markdown_cell("""
Ce notebook évalue les performances du modèle de détection de langues.
Le modèle utilise FastText pour identifier la langue d'un texte donné.
"""))


n.cells.append(nbf.v4.new_markdown_cell("""
## 📌 Justification : Pourquoi le modèle de détection de langue n’est pas entraîné ?

#### 🔍 Utilisation du modèle `lid.176.bin` de FastText
Nous utilisons le modèle pré-entraîné `lid.176.bin` de FastText, qui est un **modèle déjà entraîné sur 176 langues**.  
Ce modèle a été conçu par **Facebook AI** et est largement utilisé pour la détection de langues grâce à son **efficacité et sa rapidité**.

#### ❓ Pourquoi ne pas entraîner notre propre modèle ?
1. **Base de données linguistique massive**  
   - `lid.176.bin` est entraîné sur un très grand corpus multilingue couvrant de nombreuses variations linguistiques.  
   - Il capture mieux **les variations d'écriture**, **les erreurs typographiques** et **les expressions courantes** dans chaque langue.

2. **Performance optimale dès le départ**  
   - Nous avons testé `lid.176.bin` avec **plusieurs phrases en différentes langues** (notamment en français).  
   - Les résultats ont montré une **précision élevée**, rendant un nouvel entraînement inutile pour notre besoin.

3. **Économie de ressources**  
   - L'entraînement d'un modèle de détection de langue **nécessite une énorme quantité de données** et des ressources GPU importantes.  
   - En utilisant un modèle pré-entraîné, nous évitons **du temps d'entraînement** tout en bénéficiant d'une **excellente précision**.

#### 📌 Conclusion
Le modèle `lid.176.bin` de FastText répond parfaitement à nos besoins.  
- Il est **rapide** ⚡  
- Il est **précis** 🎯  
- Il **gère 176 langues** sans besoin de **fine-tuning**  

Ainsi, **l'entraîner à nouveau serait redondant et inefficace**.  
Nous utilisons donc ce modèle **tel quel** pour nos prédictions.
"""))

# Inject the dataset into the notebook
n.cells.append(nbf.v4.new_code_cell(f"""
import pandas as pd

# Load dataset used for evaluation
df = pd.DataFrame({results})
df_results = df
"""))

# Add evaluation results
n.cells.append(nbf.v4.new_markdown_cell("## Résultats des prédictions"))
n.cells.append(nbf.v4.new_markdown_cell("""
Ce tableau montre les résultats des prédictions du modèle :
- **Text** : Le texte évalué.
- **True Label** : La langue réelle du texte.
- **Predicted Label** : La langue prédite par le modèle.
- **Confidence** : Le niveau de confiance de la prédiction (entre 0 et 1).
"""))
n.cells.append(nbf.v4.new_code_cell("""
# Display full evaluation results
pd.set_option("display.max_rows", None)  # Show all rows
pd.set_option("display.max_colwidth", None)  # Show full content in cells
df_results
"""))

# Add histogram of confidence scores
n.cells.append(nbf.v4.new_markdown_cell("## Distribution des scores de confiance"))
n.cells.append(nbf.v4.new_markdown_cell("""
Ce graphique montre la distribution des scores de confiance pour toutes les prédictions valides :
- L'axe **x** représente les scores de confiance (de 0 à 1).
- L'axe **y** représente le nombre de prédictions ayant un score de confiance dans une plage donnée.
Un pic élevé près de 1 indique que le modèle est confiant dans ses prédictions.
"""))
n.cells.append(nbf.v4.new_code_cell("""
import matplotlib.pyplot as plt

# Filter valid confidences
confidences = df_results["Confidence"].dropna()

plt.figure(figsize=(10, 6))
plt.hist(confidences, bins=10, color='skyblue', alpha=0.7)
plt.title("Distribution des scores de confiance des prédictions")
plt.xlabel("Score de confiance")
plt.ylabel("Nombre d'exemples")
plt.show()
"""))

# Add cumulative curve of confidence scores
n.cells.append(nbf.v4.new_markdown_cell("## Courbe cumulative des scores de confiance"))
n.cells.append(nbf.v4.new_markdown_cell("""
Ce graphique montre la proportion cumulée des prédictions atteignant un certain seuil de confiance :
- L'axe **x** représente les scores de confiance (de 0 à 1).
- L'axe **y** représente la proportion cumulative des prédictions valides.
Une montée rapide dans la courbe indique que la majorité des prédictions ont des scores élevés.
"""))
n.cells.append(nbf.v4.new_code_cell("""
# Sort and calculate cumulative confidence scores
sorted_confidences = confidences.sort_values()
cumulative = sorted_confidences.rank(pct=True).values

plt.figure(figsize=(10, 6))
plt.plot(sorted_confidences, cumulative, color="blue")
plt.title("Courbe cumulative des scores de confiance")
plt.xlabel("Score de confiance")
plt.ylabel("Proportion cumulative des prédictions")
plt.grid()
plt.show()
"""))

# Add histogram of text lengths
n.cells.append(nbf.v4.new_markdown_cell("## Distribution des longueurs de texte"))
n.cells.append(nbf.v4.new_markdown_cell("""
Ce graphique montre comment la longueur des textes évalués est répartie :
- L'axe **x** représente la longueur des textes (en caractères).
- L'axe **y** représente le nombre de textes de chaque longueur.
Cela permet d'identifier si la performance varie en fonction de la longueur des phrases.
"""))
n.cells.append(nbf.v4.new_code_cell("""
# Calculate text lengths
df_results["Text Length"] = df_results["Text"].apply(len)

plt.figure(figsize=(10, 6))
plt.hist(df_results["Text Length"], bins=15, color='orange', alpha=0.7)
plt.title("Distribution des longueurs de texte")
plt.xlabel("Longueur des textes (en caractères)")
plt.ylabel("Nombre de textes")
plt.show()
"""))

# Add performance vs confidence threshold graph
n.cells.append(nbf.v4.new_markdown_cell("## Performance en fonction du seuil de confiance"))
n.cells.append(nbf.v4.new_markdown_cell("""
Ce graphique montre comment la précision évolue en fonction du seuil de confiance :
- L'axe **x** représente les seuils de confiance.
- L'axe **y** représente la précision.
Cela aide à déterminer un seuil optimal pour garantir des prédictions fiables.
"""))
n.cells.append(nbf.v4.new_code_cell("""
import numpy as np

thresholds = np.linspace(0, 1, 50)
precisions = []

for threshold in thresholds:
    filtered = df_results[df_results["Confidence"] >= threshold]
    if len(filtered) > 0:
        precision = (filtered["True Label"] == filtered["Predicted Label"]).mean()
        precisions.append(precision)
    else:
        precisions.append(0)

plt.figure(figsize=(10, 6))
plt.plot(thresholds, precisions, color="green")
plt.title("Précision en fonction du seuil de confiance")
plt.xlabel("Seuil de confiance")
plt.ylabel("Précision")
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