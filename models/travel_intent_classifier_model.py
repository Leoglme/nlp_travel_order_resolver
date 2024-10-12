from transformers import DistilBertTokenizerFast, DistilBertForSequenceClassification, Trainer, TrainingArguments
from datasets import load_dataset
import numpy as np
import evaluate
from services.system_manager import SystemManager


class TravelIntentClassifierModel:
    """
    This class is responsible for training a DistilBERT-based model to classify whether
    a sentence refers to a trip (departure and arrival cities) or not.

    **Why DistilBERT?**
    The choice of DistilBERT was made because it offers a lightweight and efficient alternative
    to heavier models like BERT and CamemBERT. DistilBERT is 40% smaller than BERT while retaining
    about 97% of its performance, making it an ideal choice for this task. It captures enough
    semantic information to differentiate between sentences talking about trips and other sentences
    without the computational overhead of larger models.

    **Why not CamemBERT?**
    CamemBERT is a strong option for French-specific tasks, but it is larger and slower to train than
    DistilBERT. Since the task here is relatively simple (classifying if a sentence involves a trip),
    DistilBERT is sufficient, and its smaller size makes it more suitable for quicker inference and
    training. Moreover, DistilBERT can be fine-tuned effectively on French sentences even though it
    was pre-trained on English, thanks to its general understanding of semantic structures.

    **Why not Logistic Regression with Scikit-learn?**
    Logistic Regression is a simpler, faster solution, but it does not capture deep semantic information
    like transformer-based models do. Given that we need to understand the meaning of a sentence in
    context (e.g., recognizing that "going to the store" is not a trip to the same sense as "traveling
    from Paris to Lyon"), Logistic Regression might fail to generalize well on complex language patterns.
    DistilBERT, by contrast, captures these nuances better thanks to its deep learning architecture.
    """

    def __init__(self, model_name="distilbert-base-uncased", num_labels=2, batch_size=16, epochs=10,
                 output_dir="./model_output/travel_intent_classifier", log_dir="./logs/travel_intent_classifier"):
        """
        Initializes the TripClassifierModel with the specified parameters.

        Args:
            model_name (str): Name of the DistilBERT model to use.
            num_labels (int): Number of output labels (2 for binary classification).
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
        # if the model is already trained (output_dir exists), load it
        if SystemManager.directory_exists(self.output_dir):
            self.model = DistilBertForSequenceClassification.from_pretrained(self.output_dir, local_files_only=True)
            self.tokenizer = DistilBertTokenizerFast.from_pretrained(self.output_dir, local_files_only=True)
            print(f"Model and tokenizer loaded from {self.output_dir}")
        else:
            self.tokenizer = DistilBertTokenizerFast.from_pretrained(self.model_name)
            self.model = DistilBertForSequenceClassification.from_pretrained(self.model_name,
                                                                             num_labels=self.num_labels)

    """
    Loads the dataset from the provided CSV file and splits it into train/test sets.

    Args:
        csv_file (str): Path to the CSV file containing text and labels.

    Returns:
        DatasetDict: A dictionary with 'train' and 'test' datasets.
    """
    @staticmethod
    def load_data(csv_file):
        dataset = load_dataset('csv', data_files=csv_file)
        dataset = dataset['train'].train_test_split(test_size=0.2)
        return dataset

    """
    Tokenizes the input text using DistilBERT tokenizer.

    Args:
        examples (dict): A batch of examples from the dataset.

    Returns:
        dict: A dictionary containing tokenized inputs.
    """
    def tokenize_data(self, examples):
        return self.tokenizer(examples['text'], padding='max_length', truncation=True)

    """
    Computes evaluation metrics like precision, recall, F1-score, and accuracy.

    Args:
        p (EvalPrediction): The predictions and labels from evaluation.

    Returns:
        dict: A dictionary containing precision, recall, f1, and accuracy scores.
    """
    @staticmethod
    def compute_metrics(p):
        metric = evaluate.load("accuracy")
        precision_metric = evaluate.load("precision")
        recall_metric = evaluate.load("recall")
        f1_metric = evaluate.load("f1")

        predictions, labels = p
        predictions = np.argmax(predictions, axis=1)

        accuracy = metric.compute(predictions=predictions, references=labels)
        precision = precision_metric.compute(predictions=predictions, references=labels, average='weighted')
        recall = recall_metric.compute(predictions=predictions, references=labels, average='weighted')
        f1 = f1_metric.compute(predictions=predictions, references=labels, average='weighted')

        return {
            'accuracy': accuracy['accuracy'],
            'precision': precision['precision'],
            'recall': recall['recall'],
            'f1': f1['f1'],
        }

    """
    Trains the DistilBERT model on the provided dataset.

    Args:
        dataset (DatasetDict): The training and test datasets.
    """
    def train(self, dataset):
        SystemManager.clean_directories([self.output_dir, self.log_dir])
        tokenized_datasets = dataset.map(self.tokenize_data, batched=True)

        # Arguments for training
        training_args = TrainingArguments(
            output_dir=self.output_dir,
            eval_strategy="epoch",
            save_strategy="epoch",
            learning_rate=2e-5,
            per_device_train_batch_size=self.batch_size,
            per_device_eval_batch_size=self.batch_size,
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

        # Train the model
        trainer.train()

        # Save the fine-tuned model and tokenizer
        trainer.save_model(self.output_dir)
        self.model.save_pretrained(self.output_dir)
        self.tokenizer.save_pretrained(self.output_dir)

    """
    Evaluates the model on the provided test dataset.

    Args:
       dataset (DatasetDict): The test dataset.

    Returns:
       dict: The computed evaluation metrics.
    """
    def evaluate(self, dataset):
        tokenized_datasets = dataset.map(self.tokenize_data, batched=True)

        trainer = Trainer(
            model=self.model,
            args=TrainingArguments(output_dir=self.output_dir),
            eval_dataset=tokenized_datasets["test"],
            tokenizer=self.tokenizer,
            compute_metrics=self.compute_metrics,
        )

        # Evaluate the model
        eval_results = trainer.evaluate()
        return eval_results
    """
    Predicts if the input sentence refers to a trip or not.

    Args:
        sentence (str): A single sentence to classify.

    Returns:
        int: Prediction (1 for trip-related, 0 for non-trip-related).
    """
    def predict(self, sentence: str):
        inputs = self.tokenizer([sentence], padding=True, truncation=True, return_tensors="pt")
        outputs = self.model(**inputs)
        predictions = np.argmax(outputs.logits.detach().numpy(), axis=1)
        return predictions[0]
