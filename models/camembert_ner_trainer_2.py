import torch
from transformers import CamembertForTokenClassification, CamembertTokenizerFast, Trainer, TrainingArguments
from datasets import Dataset
import evaluate
import numpy as np
from services.system_manager import SystemManager

class CamemBERTNERTrainer:
    def __init__(self, model_name="camembert-base", train_file="datasets/sentences_with_cities.csv", num_labels=3,
                 output_dir="model_output", log_dir="./logs"):
        self.model_name = model_name
        self.train_file = train_file
        self.num_labels = num_labels
        self.output_dir = output_dir
        self.log_dir = log_dir

        # Supprimer les dossiers de sortie et de logs s'ils existent déjà
        SystemManager.clean_directories([self.output_dir, self.log_dir])

        # Charger le modèle et le tokenizer CamemBERT
        self.model = CamembertForTokenClassification.from_pretrained(self.model_name, num_labels=self.num_labels)
        if torch.cuda.is_available():
            self.model = self.model.cuda()  # Envoi du modèle sur le GPU si disponible
        self.tokenizer = CamembertTokenizerFast.from_pretrained(self.model_name)

    def load_and_prepare_data(self):
        dataset = Dataset.from_csv(self.train_file)

        def tokenize_and_align_labels(examples):
            tokenized_inputs = self.tokenizer(examples["text"], truncation=True, padding="max_length", max_length=128)

            labels = []
            for i, text in enumerate(examples["text"]):
                words = text.split()
                word_ids = tokenized_inputs.word_ids(batch_index=i)
                label_ids = []

                for word_idx in word_ids:
                    if word_idx is None:
                        label_ids.append(-100)  # Ignorer les tokens de padding
                    elif words[word_idx] == examples["departure"][i]:
                        label_ids.append(1)  # B-city
                    elif words[word_idx] == examples["destination"][i]:
                        label_ids.append(2)  # I-city
                    else:
                        label_ids.append(0)  # O

                labels.append(label_ids)

            tokenized_inputs["labels"] = labels
            return tokenized_inputs

        tokenized_dataset = dataset.map(tokenize_and_align_labels, batched=True, num_proc=4)  # Ajout du multiprocessing
        return tokenized_dataset

    def analyze_token_lengths(self):
        dataset = Dataset.from_csv(self.train_file)
        lengths = [len(self.tokenizer(text)["input_ids"]) for text in dataset["text"]]

        avg_length = sum(lengths) / len(lengths)
        max_length = max(lengths)

        print(f"Longueur moyenne des tokens : {avg_length}")
        print(f"Longueur maximale des tokens : {max_length}")
        return avg_length, max_length

    def train(self):
        avg_length, max_length = self.analyze_token_lengths()
        print(f"Ajustement possible du max_length : {max_length}")

        dataset = self.load_and_prepare_data()

        # Séparer l'entraînement et l'évaluation
        train_size = int(0.8 * len(dataset))
        train_dataset = dataset.select(range(train_size))
        eval_dataset = dataset.select(range(train_size, len(dataset)))

        training_args = TrainingArguments(
            output_dir=self.output_dir,
            eval_strategy="epoch",  # Évaluer après chaque epoch
            learning_rate=2e-5,
            per_device_train_batch_size=16,  # Réduction pour gérer la mémoire
            per_device_eval_batch_size=16,
            num_train_epochs=3,
            weight_decay=0.01,
            gradient_accumulation_steps=4,  # Meilleure utilisation des ressources mémoire
            logging_dir=self.log_dir,
            logging_steps=10,
            fp16=True,  # Activer la précision mixte pour accélérer les calculs
            save_strategy="epoch",  # Sauvegarder le modèle après chaque epoch
        )

        metric = evaluate.load("seqeval")

        def compute_metrics(p):
            predictions, labels = p
            if isinstance(predictions, np.ndarray):
                predictions = torch.tensor(predictions)

            predictions = torch.argmax(predictions, dim=2)

            label_list = ["O", "B-city", "I-city"]

            true_predictions = [
                [label_list[pred] for (pred, label) in zip(prediction, label) if label != -100]
                for prediction, label in zip(predictions, labels)
            ]
            true_labels = [
                [label_list[l] for l in label if l != -100]
                for label in labels
            ]

            results = metric.compute(predictions=true_predictions, references=true_labels, zero_division=0)
            return {
                "precision": results["overall_precision"],
                "recall": results["overall_recall"],
                "f1": results["overall_f1"],
                "accuracy": results["overall_accuracy"],
            }

        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=train_dataset,
            eval_dataset=eval_dataset,
            tokenizer=self.tokenizer,
            compute_metrics=compute_metrics,
        )

        trainer.train()

    def save_model(self):
        self.model.save_pretrained(self.output_dir)
        self.tokenizer.save_pretrained(self.output_dir)