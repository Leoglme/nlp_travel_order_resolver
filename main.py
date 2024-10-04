import os

# Masquer les warnings TensorFlow
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from services.device_manager import DeviceManager
from services.dataset_generator import DatasetGenerator
from models.camembert_ner_trainer import CamemBERTNERTrainer
from services.voice_to_text_converter import VoiceToTextConverter
from services.language_detection import LanguageIdentification
from services.path_finder_manager import PathFinderManager

if __name__ == '__main__':
    # Partie reconnaissance vocale
    voice_text_converter = VoiceToTextConverter()

    # Pour utiliser un fichier audio
    # text_from_file = converter.convert_from_audio_file("assets/toulouse-bordeaux.wav")
    # print(f"Texte extrait du fichier audio : {text_from_file}")

    # Pour utiliser le microphone
    text_from_microphone = voice_text_converter.convert_from_microphone()
    print(f"Texte extrait du microphone : {text_from_microphone}")

    # Détection de la langue pour vérifier que c'est bien du français
    lang_identifier = LanguageIdentification()
    lang, confidence = lang_identifier.stat_print(text_from_microphone)

    if lang[0] == "__label__fr":  # Si la langue détectée est le français
        print("Texte en français détecté.")

        # Comparer les performances entre CPU et GPU
        device_manager = DeviceManager()
        best_device = device_manager.compare_devices()
        print(f"L'appareil le plus rapide est : {best_device}")

        if best_device == "gpu":
            device_manager.use_gpu()
        else:
            device_manager.use_cpu()

        # Initialiser le CamemBERTNERTrainer
        ner_trainer = CamemBERTNERTrainer()

        # Vérifier si le modèle est déjà entraîné ou non
        if os.path.exists(ner_trainer.output_dir):  # Si le modèle est déjà entraîné
            ner_trainer.load_model()
        else:
            print("Génération du dataset...")
            # Génération du dataset (ceci génère le fichier `sentences_with_cities.csv`)
            dataset_generator = DatasetGenerator()
            dataset_generator.generate_dataset()
            # Entraîner le modèle
            ner_trainer.init_and_train_model()

        # Extraction des villes de départ et de destination à partir du texte
        departure, destination = ner_trainer.extract_trip_details(text_from_microphone)
        print(f"Départ : {departure}, Destination : {destination}")

        if departure and destination:
            # Utiliser PathFinderManager pour trouver le meilleur itinéraire
            path_finder = PathFinderManager(timetable_file="assets/timetables.csv")
            best_route = path_finder.find_best_route(departure, destination)
            print(f"Meilleur itinéraire trouvé : {best_route}")
        else:
            print("Impossible d'extraire les villes de départ et d'arrivée.")

    else:
        print(f"Texte non-français détecté : {lang[0]} avec une confiance de {confidence[0]}%")
        # Enregistrer la sortie en tant que 'NOT_FRENCH'