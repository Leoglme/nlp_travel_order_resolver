import os

import nbformat as nbf

n = nbf.v4.new_notebook()

# Titre principal
n.cells.append(nbf.v4.new_markdown_cell("""
# Travel Order Resolver

## Introduction

Ce projet vise à développer un modèle NLP pour résoudre les ordres de voyage. Nous allons utiliser des modèles basés sur le langage naturel, tels que **CamemBERT**, pour extraire les entités des ordres de voyage. Ces entités incluent les villes de départ et d'arrivée.

Les modèles seront évalués en fonction de la précision de l'extraction des entités, du score F1, et d'autres métriques pertinentes.

<style>
h1 {color: navy;}
h2 {color: navy;}
</style>
"""))

# Structure du Dataset
n.cells.append(nbf.v4.new_markdown_cell("""
## Structure du Dataset

Le dataset est composé de phrases contenant des ordres de voyage. Chaque phrase contient :
- Le texte de la phrase
- La ville de départ
- La ville d'arrivée
- Un label indiquant si la phrase est valide ou non

Ces données sont utilisées pour entraîner et évaluer le modèle de reconnaissance d'entités nommées (NER).
"""))

# Explication de la classe de préparation des données
n.cells.append(nbf.v4.new_markdown_cell("""
## Préparation des Données avec DataProcessor

La classe **DataProcessor** est utilisée pour préparer le dataset. Elle permet de charger et de filtrer les phrases, d'extraire les villes de départ et d'arrivée, et de formater les données pour l'entraînement.

```python
class DataProcessor:
    def load_dataset(self, filepath):
        # Charger les données à partir du fichier CSV
        pass

    def prepare_data(self, data):
        # Préparation et tokenization des données
        pass
```
"""))

# Explication du modèle CamemBERT
n.cells.append(nbf.v4.new_markdown_cell("""
## Modèle CamemBERT pour la reconnaissance d'entités nommées (NER)

Le modèle **CamemBERT** est un modèle de type transformateur pré-entraîné sur des tâches de traitement de la langue française. Pour notre tâche, il est fine-tuné pour reconnaître les entités nommées, en particulier les villes de départ et d'arrivée.

### Construction du modèle

Le modèle est basé sur la bibliothèque `Transformers` de Hugging Face. Voici comment nous le configurons et l'entraînons :

```python
from transformers import CamembertForTokenClassification, CamembertTokenizerFast, Trainer, TrainingArguments

model = CamembertForTokenClassification.from_pretrained("camembert-base", num_labels=3)
tokenizer = CamembertTokenizerFast.from_pretrained("camembert-base")

# Arguments d'entraînement
training_args = TrainingArguments(
    output_dir='./results',
    evaluation_strategy="epoch",
    learning_rate=2e-5,
    per_device_train_batch_size=16,
    per_device_eval_batch_size=16,
    num_train_epochs=3,
    weight_decay=0.01,
    logging_dir='./logs',
)

# Entraînement
trainer = Trainer(
    model=model,
    args=training_args,
    train_dataset=train_dataset,
    eval_dataset=eval_dataset,
    tokenizer=tokenizer,
)
trainer.train()
```
"""))

# Explication des métriques d'évaluation
n.cells.append(nbf.v4.new_markdown_cell("""
## Évaluation du Modèle

Le modèle est évalué en utilisant des métriques telles que :
- **Précision** : Le pourcentage de prédictions correctes.
- **Rappel** : La capacité du modèle à identifier toutes les entités pertinentes.
- **Score F1** : La moyenne harmonique de la précision et du rappel.

Nous utilisons également une matrice de confusion pour analyser les faux positifs et les faux négatifs.

```python
from sklearn.metrics import classification_report, confusion_matrix

y_true = [1, 0, 1]  # Exemples de labels réels
y_pred = [1, 0, 0]  # Exemples de prédictions du modèle

# Affichage du rapport de classification
print(classification_report(y_true, y_pred, target_names=["O", "B-city", "I-city"]))

# Matrice de confusion
cm = confusion_matrix(y_true, y_pred)
print(cm)
```
"""))

# Affichage des résultats du modèle
n.cells.append(nbf.v4.new_markdown_cell("""
## Résultats du Modèle
"""))

code_results = """
import json
import matplotlib.pyplot as plt
import numpy as np

# Chargement des résultats du modèle NER
with open("ner_results.json", "r") as file:
    ner_results = json.load(file)

# Affichage des résultats
print("## Précision: {}".format(ner_results['precision']))
print("## Rappel: {}".format(ner_results['recall']))
print("## Score F1: {}".format(ner_results['f1']))
"""

n.cells.append(nbf.v4.new_code_cell(code_results))

# Graphique des résultats
n.cells.append(nbf.v4.new_markdown_cell("""
### Graphique des Résultats
"""))

code_graphique = """
import json
import numpy as np
import matplotlib.pyplot as plt
from sklearn.metrics import ConfusionMatrixDisplay

# Chargement des résultats
with open("ner_results.json", "r") as file:
    ner_results = json.load(file)

# Matrice de confusion
cm = np.array(ner_results['confusion_matrix'])

def plot_confusion_matrix(cm):
    disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=['O', 'B-city', 'I-city'])
    disp.plot(cmap=plt.cm.Blues)
    plt.title('Matrice de Confusion')
    plt.show()

plot_confusion_matrix(cm)
"""

n.cells.append(nbf.v4.new_code_cell(code_graphique))

# Conclusion
n.cells.append(nbf.v4.new_markdown_cell("""
## Conclusion

Le modèle **CamemBERT** fine-tuné pour la reconnaissance d'entités nommées montre une bonne performance pour identifier les villes de départ et d'arrivée dans les ordres de voyage. Il peut encore être amélioré en augmentant le volume de données et en ajustant les hyperparamètres.

### Améliorations futures
- Augmenter la taille du dataset
- Optimiser les hyperparamètres pour une meilleure précision
- Utiliser des techniques d'augmentation de données
"""))

# Enregistrement du notebook
with open('travel_order_resolver_notebook.ipynb', 'w') as f:
    nbf.write(n, f)