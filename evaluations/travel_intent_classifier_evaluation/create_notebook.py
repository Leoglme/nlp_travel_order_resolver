import os
import nbformat as nbf
import numpy as np
import torch
from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification
from sklearn.metrics import precision_score, recall_score, f1_score, accuracy_score
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

# Load and prepare data
print("Loading and preparing data...")
dataset = load_dataset("csv", data_files="datasets/travel_intent_dataset.csv")["train"].train_test_split(test_size=0.2)
test_data = dataset["test"].select(range(min(500, len(dataset["test"]))))  # Limit to 500 examples

# Tokenize with progress bar
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
batch_size = 16
predictions = []
probs = []

for i in tqdm(range(0, len(labels), batch_size), desc="Predicting"):
    batch_input_ids = test_encodings["input_ids"][i:i+batch_size]
    batch_attention_mask = test_encodings["attention_mask"][i:i+batch_size]
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

# Create notebook
print("Creating notebook...")
n = nbf.v4.new_notebook()

# Add content to notebook
n.cells.append(nbf.v4.new_markdown_cell("# Model Evaluation\nThis notebook evaluates the performance of an intent classification model."))
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
n.cells.append(nbf.v4.new_markdown_cell("## Performance Metrics Visualization"))
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
n.cells.append(nbf.v4.new_markdown_cell("## Confusion Matrix"))
n.cells.append(nbf.v4.new_code_cell("""
from sklearn.metrics import confusion_matrix, ConfusionMatrixDisplay

cm = confusion_matrix(labels, predictions)
disp = ConfusionMatrixDisplay(confusion_matrix=cm, display_labels=["Non-Intent", "Intent"])
disp.plot(cmap=plt.cm.Blues)
plt.title("Confusion Matrix")
plt.show()
"""))

# ROC Curve
n.cells.append(nbf.v4.new_markdown_cell("## ROC Curve"))
n.cells.append(nbf.v4.new_code_cell("""
from sklearn.metrics import roc_curve, auc
import numpy as np

if not isinstance(probs, np.ndarray):
    probs = np.array(probs)

fpr, tpr, _ = roc_curve(labels, probs[:, 1])
roc_auc = auc(fpr, tpr)

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
n.cells.append(nbf.v4.new_markdown_cell("## Prediction Score Distribution"))
n.cells.append(nbf.v4.new_code_cell("""
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