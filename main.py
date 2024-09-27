# from services.voice_to_text_converter import VoiceToTextConverter
#
# converter = VoiceToTextConverter()
# text_from_file = converter.convert_from_audio_file("assets/toulouse-bordeaux.wav")
# print(f"Texte extrait du fichier audio : {text_from_file}")

# Pour utiliser le microphone
# text_from_microphone = converter.convert_from_microphone()
# print(f"Texte extrait du microphone : {text_from_microphone}")

# self.model_name = "distilcamembert-base"
import os
# Masquer les warnings TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'
from services.device_manager import DeviceManager
from services.dataset_generator import DatasetGenerator
from models.camembert_ner_trainer import CamemBERTNERTrainer


if __name__ == '__main__':
    device_manager = DeviceManager()

    # Comparer les performances entre CPU et GPU
    best_device = device_manager.compare_devices()
    print(f"L'appareil le plus rapide est : {best_device}")

    if best_device == "gpu":
        # Passer au GPU
        device_manager.use_gpu()
    else:
        # Passer au CPU
        device_manager.use_cpu()

    # Créer une instance de DatasetGenerator pour générer le fichier CSV
    dataset_generator = DatasetGenerator()

    # Générer les fichiers CSV du dataset
    dataset_generator.generate_dataset()

    ner_trainer = CamemBERTNERTrainer()
    ner_trainer.train()
    ner_trainer.save_model()