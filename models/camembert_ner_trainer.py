import os
import torch
from transformers import CamembertForTokenClassification, CamembertTokenizerFast, Trainer, TrainingArguments
from datasets import Dataset
import evaluate
import numpy as np
from services.system_manager import SystemManager

if torch.cuda.is_available():
    print(f"Training on {torch.cuda.get_device_name(0)}")
else:
    print("Training on CPU")


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
        # Supprimer les dossiers de sortie et de logs s'ils existent déjà
        SystemManager.clean_directories([self.output_dir, self.log_dir])

        print("Initialisation du modèle CamemBERT...")
        self.model = CamembertForTokenClassification.from_pretrained(self.model_name, num_labels=self.num_labels)
        self.model = self.model.cuda() if torch.cuda.is_available() else self.model.cpu()
        self.tokenizer = CamembertTokenizerFast.from_pretrained(self.model_name)

        # Charger et préparer les données
        dataset = self.load_and_prepare_data()

        # Configurer les arguments de training
        training_args = TrainingArguments(
            output_dir=self.output_dir,  # Dossier de sortie
            eval_strategy="epoch",  # Évaluer à chaque epoch
            learning_rate=2e-5,
            per_device_train_batch_size=32,  # Taille du batch
            per_device_eval_batch_size=32,  # Taille du batch pour évaluation
            num_train_epochs=3,  # Ajustez selon vos besoins
            weight_decay=0.01,
            logging_dir=self.log_dir,  # Dossier pour les logs
            logging_steps=10,
            fp16=True  # Activer la précision mixte si GPU disponible
        )

        # Définir les métriques
        metric = evaluate.load("seqeval")

        def compute_metrics(p):
            predictions, labels = p

            # Convertir les prédictions en Tensor si elles sont en numpy.ndarray
            if isinstance(predictions, np.ndarray):
                predictions = torch.tensor(predictions)

            predictions = torch.argmax(predictions, dim=2)  # Transformer les prédictions en classe prédite (0, 1, 2)

            # Mapping des labels
            label_list = ["O", "B-city", "I-city"]

            # Retirer les valeurs -100 qui sont des tokens ignorés et convertir en labels lisibles
            true_predictions = [
                [label_list[pred] for (pred, label) in zip(prediction, label) if label != -100]
                for prediction, label in zip(predictions, labels)
            ]
            true_labels = [
                [label_list[l] for l in label if l != -100]
                for label in labels
            ]

            # Calculer les métriques avec seqeval
            results = metric.compute(predictions=true_predictions, references=true_labels, zero_division=0)
            return {
                "precision": results["overall_precision"],
                "recall": results["overall_recall"],
                "f1": results["overall_f1"],
                "accuracy": results["overall_accuracy"],
            }

        # Configurer le Trainer
        trainer = Trainer(
            model=self.model,
            args=training_args,
            train_dataset=dataset,
            eval_dataset=dataset,  # Vous pouvez séparer les datasets de train et eval
            tokenizer=self.tokenizer,
            compute_metrics=compute_metrics,
        )

        # Entraîner le modèle
        trainer.train()

        # Sauvegarder le modèle après l'entraînement
        self.save_model()

    def save_model(self):
        """
        Sauvegarde le modèle fine-tuné.
        """
        print(f"Sauvegarde du modèle dans {self.output_dir}...")
        self.model.save_pretrained(self.output_dir)
        self.tokenizer.save_pretrained(self.output_dir)

    def tokenize_and_align_labels(self, examples):
        tokenized_inputs = self.tokenizer(examples["text"], truncation=True, padding="max_length", max_length=128,
                                          return_offsets_mapping=True)

        labels = []
        for i, text in enumerate(examples["text"]):
            word_ids = tokenized_inputs.word_ids(batch_index=i)
            departure = examples["departure"][i]
            destination = examples["destination"][i]

            label_ids = []
            previous_word_idx = None
            for word_idx in word_ids:
                if word_idx is None:
                    label_ids.append(-100)  # Ignorer les tokens de padding
                elif word_idx != previous_word_idx:
                    word = examples["text"][i].split()[word_idx]
                    if word == departure:  # Ville de départ
                        label_ids.append(1)  # B-city
                    elif word == destination:  # Ville d'arrivée
                        label_ids.append(2)  # I-city
                    else:
                        label_ids.append(0)  # O (Other)
                else:
                    label_ids.append(label_ids[-1] if label_ids else 0)  # Pour les sous-mots

                previous_word_idx = word_idx

            labels.append(label_ids)

        tokenized_inputs["labels"] = labels
        tokenized_inputs.pop("offset_mapping")  # Supprimer l'offset mapping car inutile pour l'entraînement
        return tokenized_inputs

    def load_and_prepare_data(self):
        """
        Charge et prépare les données de training à partir du fichier CSV.
        Les données doivent inclure des colonnes 'text', 'departure', et 'destination' pour les phrases, villes de départ et d'arrivée.
        """
        # Charger le dataset depuis le fichier CSV
        dataset = Dataset.from_csv(self.train_file)

        # Appliquer la fonction de tokenisation et d'alignement des labels au dataset
        tokenized_dataset = dataset.map(self.tokenize_and_align_labels, batched=True)

        return tokenized_dataset

    def extract_trip_details(self, text):
        """
        Utilise le modèle NER CamemBERT pour extraire les villes de départ et d'arrivée à partir du texte donné.

        :param text: Le texte à analyser (phrase de l'utilisateur).
        :return: La ville de départ et la ville de destination si elles sont trouvées.
        """
        # Tokeniser le texte fourni
        tokens = self.tokenizer(text, return_tensors="pt", truncation=True, padding="max_length", max_length=128)
        tokens = tokens.to(self.model.device)  # Envoyer les tokens sur le même device que le modèle (CPU ou GPU)

        # Utilisation du modèle pour obtenir des prédictions
        with torch.no_grad():
            output = self.model(**tokens)

        predictions = torch.argmax(output.logits, dim=2)  # Obtenir les classes prédites pour chaque token
        labels = predictions.squeeze().tolist()

        # Liste des mots correspondant aux tokens
        words = text.split()

        # Debug : afficher les prédictions
        print(f"Texte: {text}")
        print(f"Tokens: {len(tokens['input_ids'][0])}")
        print(f"Labels: {len(labels)}")

        departure = None
        destination = None

        # Parcourir les labels et extraire les villes de départ et d'arrivée
        for idx, label in enumerate(labels):
            if label == 1:  # B-city (ville de départ)
                departure = words[idx]
            elif label == 2:  # I-city (ville d'arrivée)
                destination = words[idx]

        return departure, destination
