import speech_recognition as sr
import sys
import logging

# Configuration du logger
logging.basicConfig(level=logging.ERROR, format='%(asctime)s - %(levelname)s - %(message)s')


class VoiceToTextConverter:
    def __init__(self, language="fr-FR", energy_threshold=300, pause_threshold=0.8):
        """
        Initialise le convertisseur de voix en texte avec des paramètres ajustables.

        :param language: Langue pour la reconnaissance vocale (par défaut, "fr-FR" pour le français).
        :param energy_threshold: Seuil d'énergie pour la détection du bruit (plus bas = plus sensible).
        :param pause_threshold: Temps d'attente de silence avant d'arrêter l'écoute (en secondes).
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
            logging.error("Erreur : la reconnaissance vocale n'a pas pu comprendre l'audio.")
            sys.exit(1)
        except sr.RequestError:
            logging.error("Erreur : échec de la requête au service de reconnaissance vocale.")
            sys.exit(1)

    def convert_from_microphone(self):
        """
        Convertit la voix captée par le microphone en texte.

        :return: Le texte transcrit ou une erreur en cas d'échec.
        """
        try:
            with sr.Microphone() as source:
                # Ajuste automatiquement le seuil de bruit pour l'ambiance actuelle
                print("Calibrage du bruit ambiant...")
                self.recognizer.adjust_for_ambient_noise(source, duration=1)
                print(f"Seuil d'énergie ajusté : {self.recognizer.energy_threshold}")

                print("Parlez maintenant...")

                # Écoute sans timeout et attend que tu parles
                audio = self.recognizer.listen(source)

            # Reconnaissance vocale avec Google
            return self.recognizer.recognize_google(audio, language=self.language)
        except sr.UnknownValueError:
            logging.error("Erreur : la reconnaissance vocale n'a pas pu comprendre l'audio.")
            sys.exit(1)
        except sr.RequestError:
            logging.error("Erreur : échec de la requête au service de reconnaissance vocale.")
            sys.exit(1)
