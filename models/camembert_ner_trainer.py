import os
import torch
from transformers import CamembertForTokenClassification, CamembertTokenizerFast, Trainer, TrainingArguments
from datasets import Dataset
import evaluate
import numpy as np
from services.system_manager import SystemManager
from services.ner_data_preparer import NERDataPreparer


class CamemBERTNERTrainer:
    def __init__(self, model_name="camembert-base", train_file="datasets/sentences_with_cities.csv", num_labels=3,
                 output_dir="model_output", log_dir="./logs"):
        self.model_name = model_name
        self.train_file = train_file
        self.num_labels = num_labels  # Par exemple : 3 (O, B-city, I-city)
        self.output_dir = output_dir
        self.log_dir = log_dir

        # Initialiser les attributs model et tokenizer à None
        self.model = None
        self.tokenizer = None
        self.ner_data_preparer = NERDataPreparer(self.train_file)  # Initialiser le NERDataPreparer

    def load_model(self):
        """
        Charge le modèle CamemBERT et le tokenizer depuis le répertoire de sortie.
        """
        if os.path.exists(self.output_dir):  # Si le modèle existe, on le charge
            print("Chargement du modèle entraîné...")
            self.model = CamembertForTokenClassification.from_pretrained(self.output_dir)
            self.tokenizer = CamembertTokenizerFast.from_pretrained(self.output_dir)
            self.model = self.model.cuda() if torch.cuda.is_available() else self.model.cpu()
        else:
            print(f"Erreur : Aucun modèle trouvé dans {self.output_dir}. Veuillez entraîner un modèle d'abord.")

    def init_and_train_model(self):
        """
        Initialise et entraîne un nouveau modèle CamemBERT pour la reconnaissance d'entités nommées.
        """
        SystemManager.clean_directories([self.output_dir, self.log_dir])

        print("Initialisation du modèle CamemBERT...")
        self.model = CamembertForTokenClassification.from_pretrained(self.model_name, num_labels=self.num_labels)
        self.model = self.model.cuda() if torch.cuda.is_available() else self.model.cpu()
        self.tokenizer = CamembertTokenizerFast.from_pretrained(self.model_name)

        dataset = self.load_and_prepare_data()

        print(f"Exemple avant le filtrage : {dataset[0]}")
        print(f"Taille du dataset avant filtrage : {len(dataset)}")

        # Vérifier les exemples valides
        def is_valid_example(example):
            valid = 'tokens' in example and 'ner_tags' in example and example['tokens'] and example['ner_tags']
            if not valid:
                print(f"Exemple invalide trouvé : {example}")
            return valid

        dataset = dataset.filter(is_valid_example)

        print(f"Taille du dataset après filtrage : {len(dataset)}")

        if len(dataset) == 0:
            raise ValueError("Le dataset est vide après filtrage. Vérifiez les données avant de lancer l'entraînement.")

        print(f"Dataset size: {len(dataset)}")
        print(f"Example of dataset: {dataset[0]}")

        # Appliquer la tokenisation et l'alignement des labels
        tokenized_dataset = dataset.map(self.tokenize_and_align_labels, batched=True,
                                        remove_columns=dataset.column_names)

        print(f"Exemple après tokenisation : {tokenized_dataset[0]}")
        print(f"Taille du dataset tokenisé : {len(tokenized_dataset)}")

        training_args = TrainingArguments(
            output_dir=self.output_dir,
            eval_strategy="epoch",
            learning_rate=2e-5,
            per_device_train_batch_size=32,
            per_device_eval_batch_size=32,
            num_train_epochs=3,
            weight_decay=0.01,
            logging_dir=self.log_dir,
            logging_steps=10,
            fp16=True,
            # debug="underflow_overflow"
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
            train_dataset=tokenized_dataset,
            eval_dataset=tokenized_dataset,
            tokenizer=self.tokenizer,
            compute_metrics=compute_metrics,
        )

        dataloader = trainer.get_train_dataloader()
        for i, batch in enumerate(dataloader):
            print(f"Batch {i}: {batch}")
            if len(batch) == 0:
                print(f"Lot vide détecté à l'index {i}")

        try:
            trainer.train()
        except Exception as e:
            print(f"Erreur lors de l'entraînement : {e}")
            raise
        self.save_model()

    def save_model(self):
        """
        Sauvegarde le modèle fine-tuné.
        """
        print(f"Sauvegarde du modèle dans {self.output_dir}...")
        self.model.save_pretrained(self.output_dir)
        self.tokenizer.save_pretrained(self.output_dir)

    def tokenize_and_align_labels(self, examples):
        tokenized_inputs = self.tokenizer(
            examples["tokens"],
            truncation=True,
            is_split_into_words=True,
            padding="max_length",
            max_length=128
        )

        labels = []
        for i, label in enumerate(examples["ner_tags"]):
            word_ids = tokenized_inputs.word_ids(batch_index=i)
            previous_word_idx = None
            label_ids = []
            for word_idx in word_ids:
                if word_idx is None:
                    label_ids.append(-100)  # Ignore padding tokens
                elif word_idx != previous_word_idx:
                    label_ids.append(label[word_idx])
                else:
                    label_ids.append(-100)  # Ignore sub-tokens
                previous_word_idx = word_idx
            labels.append(label_ids)

        tokenized_inputs["labels"] = labels

        # Ajoute un contrôle de cohérence des longueurs
        for i, example in enumerate(examples):
            assert len(tokenized_inputs["input_ids"][i]) == len(tokenized_inputs["labels"][i]), \
                f"Incohérence à l'exemple {i}: {len(tokenized_inputs['input_ids'][i])} tokens, {len(tokenized_inputs['labels'][i])} labels"

        return tokenized_inputs

    def load_and_prepare_data(self):
        print("Chargement du fichier CSV...")
        dataset = Dataset.from_csv(self.train_file, encoding="utf-8")
        print(f"Exemple du CSV chargé: {dataset[0]}")
        print(f"Taille du dataset chargé : {len(dataset)}")
        dataset = dataset.with_format("torch")

        for idx, example in enumerate(dataset):
            text = example['text']
            departure = example['departure']
            destination = example['destination']

            if not text or not departure or not destination:
                print(f"Invalid example at index {idx}: {example}")
                continue

        tokens_list, ner_tags_list = self.ner_data_preparer.generate_tokens_and_ner_tags()

        # Vérification des longueurs
        assert len(tokens_list) == len(ner_tags_list), "Mismatch entre tokens et NER tags"

        prepared_dataset = {
            "text": [example["text"] for example in dataset],
            "tokens": tokens_list,
            "ner_tags": ner_tags_list
        }

        print("Prepared dataset sample:", prepared_dataset["tokens"][:5], prepared_dataset["ner_tags"][:5])
        print(f"Taille du dataset préparé : {len(prepared_dataset['tokens'])}")

        # Debugging : Afficher les clés disponibles après la préparation
        print(f"Clés des exemples après préparation : {list(prepared_dataset.keys())}")

        return Dataset.from_dict(prepared_dataset)

    def extract_trip_details(self, text):
        # Tokeniser le texte fourni
        tokens = self.tokenizer(text, return_tensors="pt", truncation=True, is_split_into_words=False)
        tokens = tokens.to(self.model.device)

        # Obtenir les prédictions
        with torch.no_grad():
            output = self.model(**tokens)
        predictions = torch.argmax(output.logits, dim=2)
        labels = predictions.squeeze().tolist()

        # Obtenir les tokens et les word_ids
        input_ids = tokens['input_ids'].squeeze().tolist()
        word_ids = self.tokenizer(text,
                                  return_offsets_mapping=False).word_ids()  # Méthode correcte pour récupérer word_ids
        tokens_text = self.tokenizer.convert_ids_to_tokens(input_ids)

        words = text.split()

        # Reconstruction des labels par mot
        word_labels = []
        previous_word_idx = None
        for idx, word_idx in enumerate(word_ids):
            if word_idx is not None and word_idx != previous_word_idx:
                word_labels.append(labels[idx])
                previous_word_idx = word_idx

        # Vérifie que le nombre de labels correspond au nombre de mots
        if len(word_labels) != len(words):
            print(f"Warning: nombre de labels ({len(word_labels)}) ne correspond pas au nombre de mots ({len(words)})")

        # Extraction des villes
        departure = None
        destination = None
        for word, label in zip(words, word_labels):
            if label == 1:
                departure = word
            elif label == 2:
                destination = word

        print(f"Départ : {departure}, Destination : {destination}")
        return departure, destination
