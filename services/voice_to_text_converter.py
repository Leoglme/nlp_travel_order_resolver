import speech_recognition as sr


class VoiceToTextConverter:
    def __init__(self, language="fr-FR"):
        """
        Initialise le convertisseur de voix en texte.

        :param language: Langue pour la reconnaissance vocale (par défaut, "fr-FR" pour le français).
        """
        self.recognizer = sr.Recognizer()
        self.language = language

    def convert_from_audio_file(self, file_path):
        try:
            with sr.AudioFile(file_path) as source:
                audio = self.recognizer.record(source)
            return self.recognizer.recognize_google(audio, language=self.language)
        except sr.UnknownValueError:
            return "Erreur : la reconnaissance vocale n'a pas pu comprendre l'audio."
        except sr.RequestError:
            return "Erreur : échec de la requête au service de reconnaissance vocale."

    def convert_from_microphone(self):
        """
        Convertit la voix captée par le microphone en texte.

        :return: Le texte transcrit ou une erreur en cas d'échec.
        """
        try:
            with sr.Microphone() as source:
                print("Parlez maintenant...")
                audio = self.recognizer.listen(source)
            return self.recognizer.recognize_google(audio, language=self.language)
        except sr.UnknownValueError:
            return "Erreur : la reconnaissance vocale n'a pas pu comprendre l'audio."
        except sr.RequestError:
            return "Erreur : échec de la requête au service de reconnaissance vocale."