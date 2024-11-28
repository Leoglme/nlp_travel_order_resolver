import speech_recognition as sr
import sys
import logging

# Configuration du logger
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')

class VoiceToTextError(Exception):
    """Custom exception for voice to text conversion errors."""
    def __init__(self, message, is_audio_comprehensible, is_recognition_service_available):
        super().__init__(message)
        self.is_audio_comprehensible = is_audio_comprehensible
        self.is_recognition_service_available = is_recognition_service_available


class VoiceToTextConverter:
    def __init__(self, language="fr-FR", energy_threshold=200, pause_threshold=0.8):
        """
        Initializes the voice to text converter with adjustable parameters.

        :param language: Language for voice recognition (default, "fr-FR" for French).
        :param energy_threshold: Energy threshold for noise detection (lower = more sensitive).
        :param pause_threshold: Time to wait for silence before stopping listening (in seconds).
        """
        self.recognizer = sr.Recognizer()
        self.language = language
        self.recognizer.energy_threshold = energy_threshold  # Ajuste la sensibilité au bruit ambiant
        self.recognizer.pause_threshold = pause_threshold  # Temps de pause avant de terminer l'écoute

    def convert_from_audio_file(self, file_path):
        try:
            with sr.AudioFile(file_path) as source:
                audio = self.recognizer.record(source)
            return self.recognizer.recognize_google(audio, language=self.language)
        except sr.UnknownValueError:
            logging.error("Error: Speech recognition was unable to understand the audio.")
            raise VoiceToTextError(
                "The speech recognition could not understand the audio.",
                is_audio_comprehensible=False,
                is_recognition_service_available=True,
            )
        except sr.RequestError:
            logging.error("Error: Request to speech recognition service failed.")
            raise VoiceToTextError(
                "Failed to connect to the speech recognition service.",
                is_audio_comprehensible=False,
                is_recognition_service_available=False,
            )

    def convert_from_microphone(self):
        """
        Converts the voice picked up by the microphone into text.

        :return: The transcribed text or an error on failure.
        """
        try:
            with sr.Microphone() as source:
                # Ajuste automatiquement le seuil de bruit pour l'ambiance actuelle
                print("Ambient noise calibration...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print(f"Adjusted energy threshold: {self.recognizer.energy_threshold}")

                print("Speak Now...")

                # Écoute sans timeout et attend que tu parles
                audio = self.recognizer.listen(source)

            # Reconnaissance vocale avec Google
            return self.recognizer.recognize_google(audio, language=self.language)
        except sr.UnknownValueError:
            logging.error("Error: Speech recognition was unable to understand the audio.")
            sys.exit(1)
        except sr.RequestError:
            logging.error("Error: Request to speech recognition service failed.")
            sys.exit(1)
