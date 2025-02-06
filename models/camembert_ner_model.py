from transformers import CamembertTokenizerFast, CamembertForTokenClassification, Trainer, TrainingArguments
from datasets import load_dataset
import numpy as np
import evaluate

from models.travel_intent_classifier_model import TravelIntentClassifierModel


class CamembertNERModel:
    def __init__(self, model_name="camembert-base", num_labels=5, batch_size=4, epochs=20,
                 output_dir="./model_output/camembert_ner", log_dir="./logs/camembert_ner"):
        """
        Initializes the CamembertNERModel with the specified parameters.

        Args:
            model_name (str): Name of the CamemBERT model to use.
            num_labels (int): Number of output labels (3 for departure, destination, and other).
            batch_size (int): Batch size for training and evaluation.
            epochs (int): Number of training epochs.
            output_dir (str): Directory where the model output will be saved.
        """
        self.model_name = model_name
        self.num_labels = num_labels
        self.batch_size = batch_size
        self.epochs = epochs
        self.output_dir = output_dir
        self.log_dir = log_dir

        self.tokenizer = CamembertTokenizerFast.from_pretrained(self.model_name)
        self.model = CamembertForTokenClassification.from_pretrained(self.model_name, num_labels=self.num_labels)

        # Initializing the intent classification model
        self.intent_classifier = TravelIntentClassifierModel()

    @staticmethod
    def load_data(csv_file):
        dataset = load_dataset('csv', data_files=csv_file)
        dataset = dataset['train'].train_test_split(test_size=0.2)
        return dataset

    def tokenize_and_align_labels(self, examples):
        # Tokenisation avec padding et troncation
        tokenized_inputs = self.tokenizer(examples['text'], padding='max_length', truncation=True,
                                          is_split_into_words=False)

        labels = []
        for i, (text, departure, destination) in enumerate(
                zip(examples['text'], examples['departure'], examples['destination'])):
            word_ids = tokenized_inputs.word_ids(batch_index=i)
            label_ids = [-100] * len(word_ids)

            departure_tokens = self.tokenizer.tokenize(departure) if departure else []
            destination_tokens = self.tokenizer.tokenize(destination) if destination else []

            dep_idx, des_idx = 0, 0  # Pointeurs pour avancer sur les tokens de départ et d'arrivée

            for idx, word_id in enumerate(word_ids):
                if word_id is None:
                    continue
                token = tokenized_inputs.tokens(batch_index=i)[idx]

                # Ignorer les tokens spéciaux pour les labels
                if token in ["<s>", "</s>", "<pad>"]:
                    continue

                # Labels pour les villes de départ
                if dep_idx < len(departure_tokens) and token == departure_tokens[dep_idx]:
                    label_ids[idx] = 1 if dep_idx == 0 else 3  # "B-DEP" ou "I-DEP"
                    dep_idx += 1
                elif des_idx < len(destination_tokens) and token == destination_tokens[des_idx]:
                    label_ids[idx] = 2 if des_idx == 0 else 4  # "B-ARR" ou "I-ARR"
                    des_idx += 1
                else:
                    label_ids[idx] = 0  # O, autre

            labels.append(label_ids)

        tokenized_inputs["labels"] = labels
        return tokenized_inputs

    @staticmethod
    def compute_metrics(p):
        metric = evaluate.load("seqeval")

        predictions, labels = p
        predictions = np.argmax(predictions, axis=2)

        label_list = ["O", "B-DEP", "B-ARR", "I-DEP", "I-ARR"]

        true_predictions = [
            [label_list[p] for (p, l) in zip(prediction, label) if l != -100]
            for prediction, label in zip(predictions, labels)
        ]
        true_labels = [
            [label_list[l] for (p, l) in zip(prediction, label) if l != -100]
            for prediction, label in zip(predictions, labels)
        ]

        results = metric.compute(predictions=true_predictions, references=true_labels)
        return {
            "precision": results["overall_precision"],
            "recall": results["overall_recall"],
            "f1": results["overall_f1"],
            "accuracy": results["overall_accuracy"],
        }

    def init_and_train_model(self):
        dataset_path = 'datasets/camembert_ner_dataset.csv'
        dataset = self.load_data(dataset_path)
        tokenized_datasets = dataset.map(self.tokenize_and_align_labels, batched=True)

        training_args = TrainingArguments(
            output_dir=self.output_dir,
            evaluation_strategy="epoch",
            save_strategy="epoch",
            learning_rate=2e-5,
            per_device_train_batch_size=self.batch_size,  # Réduire la taille du batch
            per_device_eval_batch_size=self.batch_size,  # Réduire la taille du batch
            num_train_epochs=self.epochs,
            weight_decay=0.01,
            logging_dir=self.log_dir,
            logging_steps=10,
            load_best_model_at_end=True,
        )

        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=tokenized_datasets["train"],
            eval_dataset=tokenized_datasets["test"],
            tokenizer=self.tokenizer,
            compute_metrics=self.compute_metrics,
        )

        trainer.train()
        trainer.save_model(self.output_dir)
        self.model.save_pretrained(self.output_dir)
        self.tokenizer.save_pretrained(self.output_dir)

    def load_model(self):
        self.model = CamembertForTokenClassification.from_pretrained(self.output_dir)
        self.tokenizer = CamembertTokenizerFast.from_pretrained(self.output_dir)

    def extract_trip_details(self, sentence):
        is_trip_intent = self.intent_classifier.predict(sentence) == 1
        if not is_trip_intent:
            return None, None

        inputs = self.tokenizer(sentence, return_tensors="pt", padding=True, truncation=True)
        outputs = self.model(**inputs).logits
        predictions = np.argmax(outputs.detach().numpy(), axis=2)

        tokens = self.tokenizer.convert_ids_to_tokens(inputs["input_ids"].numpy()[0])

        departure_city = []
        destination_city = []
        current_dep = []
        current_des = []

        for token, prediction in zip(tokens, predictions[0]):

            if token in ["<s>", "</s>", "<pad>"]:
                continue

            # 🔹 Supprime le caractère "▁" qui marque le début des mots
            clean_token = token.replace("▁", "")

            if prediction == 1:  # "B-DEP" (Début d'une ville de départ)
                if current_dep:
                    departure_city.append("".join(current_dep))  # Ajouter la ville précédente
                current_dep = [clean_token]  # Commencer une nouvelle ville
            elif prediction == 3:  # "I-DEP" (Suite d'une ville de départ)
                current_dep.append(clean_token)  # Ajouter le morceau

            elif prediction == 2:  # "B-ARR" (Début d'une ville d'arrivée)
                if current_des:
                    destination_city.append("".join(current_des))  # Ajouter la ville précédente
                current_des = [clean_token]  # Commencer une nouvelle ville
            elif prediction == 4:  # "I-ARR" (Suite d'une ville d'arrivée)
                current_des.append(clean_token)  # Ajouter le morceau

        # 🔹 Ajouter la dernière ville détectée
        if current_dep:
            departure_city.append("".join(current_dep))
        if current_des:
            destination_city.append("".join(current_des))

        # 🔹 Fusionner les morceaux et éviter les erreurs
        departure_city = " ".join(departure_city).capitalize() if departure_city else None
        destination_city = " ".join(destination_city).capitalize() if destination_city else None

        # **Correction principale : Vérifier que la ville ne finit pas par un seul caractère isolé**
        if destination_city and len(destination_city) == 1:
            destination_city = None  # Éviter que "S" soit pris comme ville
        # remove all spaces from the city names
        departure_city = departure_city.replace(" ", "")
        destination_city = destination_city.replace(" ", "")

        return departure_city, destination_city

