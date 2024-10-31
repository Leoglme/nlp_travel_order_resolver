import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from models.camembert_ner_model import CamemBERTNERModel
from services.device_manager import DeviceManager

if __name__ == "__main__":
    # Compare performance between CPU and GPU
    device_manager = DeviceManager()
    device_manager.use_best_device()

    # Train the model
    camembert_ner_model = CamemBERTNERModel()
    camembert_ner_model.init_and_train_model()
