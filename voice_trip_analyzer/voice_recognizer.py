import speech_recognition as sr

class VoiceRecognizer:
    def __init__(self):
        self.recognizer = sr.Recognizer()

    def record_and_convert(self):
        with sr.Microphone() as source:
            print("Parlez maintenant...")
            self.recognizer.adjust_for_ambient_noise(source)
            audio = self.recognizer.listen(source)

        try:
            print("Reconnaissance en cours...")
            text = self.recognizer.recognize_google(audio, language="fr-FR")
            print(f"Texte reconnu : {text}")
            return text
        except sr.UnknownValueError:
            print("Impossible de comprendre l'audio.")
            return None
        except sr.RequestError as e:
            print(f"Erreur avec le service de reconnaissance vocale : {e}")
            return None
