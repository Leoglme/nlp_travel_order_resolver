import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.camembert_ner_model import CamemBERTNERModel
from services.device_manager import DeviceManager
from services.travel_sentences_dataset_generator import TravelSentencesDatasetGenerator

if __name__ == "__main__":
    # Compare performance between CPU and GPU
    device_manager = DeviceManager()
    device_manager.use_best_device()

    print("Generation of the dataset...")
    # Generation of the dataset (this generates the `sentences_with_cities.csv` file)
    travel_sentences_dataset_generator = TravelSentencesDatasetGenerator()
    travel_sentences_dataset_generator.generate_dataset()

    # Train the model
    camembert_ner_model = CamemBERTNERModel()
    camembert_ner_model.init_and_train_model()
