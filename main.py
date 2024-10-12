import os

# Hide TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from services.device_manager import DeviceManager
from services.travel_sentences_dataset_generator import TravelSentencesDatasetGenerator
from models.travel_intent_classifier_model import TravelIntentClassifierModel
from models.camembert_ner_model import CamemBERTNERModel
from services.voice_to_text_converter import VoiceToTextConverter
from services.language_detection import LanguageIdentification
from services.path_finder_manager import PathFinderManager

if __name__ == '__main__':
    # Voice recognition part
    # voice_text_converter = VoiceToTextConverter()

    # To use an audio file
    # text_from_file = converter.convert_from_audio_file("assets/toulouse-bordeaux.wav")
    # print(f"Text extracted from the audio file: {text_from_file}")

    # To use the microphone
    # text_from_microphone = voice_text_converter.convert_from_microphone()
    # print(f"Text taken from the microphone: {text_from_microphone}")

    # Language detection to verify that it is indeed French
    lang_identifier = LanguageIdentification()
    # lang, confidence = lang_identifier.stat_print(text_from_microphone)
    text_from_microphone = "je voudrais aller de Toulouse à bordeaux"
    print(f"Text taken from microphone : {text_from_microphone}")
    lang, confidence = lang_identifier.stat_print(text_from_microphone)

    if lang[0] == "__label__fr":
        print("French text detected.")

        # Model for verify valid sentence (subject is Ok)
        trip_intent_classifier_model = TravelIntentClassifierModel()

        # Verify if the sentence is a trip-related sentence
        prediction = trip_intent_classifier_model.predict(text_from_microphone)

        # If the sentence is a trip-related sentence
        if prediction == 1:
            print("Trip-related sentence detected.")

            # Initialize the CamemBERTNERModel
            camembert_ner_model = CamemBERTNERModel()
            camembert_ner_model.load_model()

            # Extracting departure and destination cities from text
            departure, destination = camembert_ner_model.extract_trip_details(text_from_microphone)
            print(f"departure : {departure}, destination : {destination}")

            # if departure and destination:
            #     # Use PathFinderManager to find the best route
            #     path_finder = PathFinderManager(timetable_file="assets/timetables.csv")
            #     best_route = path_finder.find_best_route(departure, destination)
            #     print(f"Best route found: {best_route}")
            # else:
            #     print("Unable to extract departure and arrival cities.")
        else:
            print("Non-trip-related sentence detected.")

    else:
        print(f"Non-French text detected: {lang[0]} with a confidence of {confidence[0]}%")
        # Save output as 'NOT_FRENCH'
