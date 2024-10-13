import sys
import os

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.device_manager import DeviceManager
from models.travel_intent_classifier_model import TravelIntentClassifierModel

if __name__ == "__main__":
    # Compare performance between CPU and GPU
    device_manager = DeviceManager()
    device_manager.use_best_device()

    trip_intent_classifier_model = TravelIntentClassifierModel()
    dataset = trip_intent_classifier_model.load_data("datasets/travel_intent_dataset.csv")
    trip_intent_classifier_model.train(dataset)
    results = trip_intent_classifier_model.evaluate(dataset)
    print("Evaluation results:", results)
