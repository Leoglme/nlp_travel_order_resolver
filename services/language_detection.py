import fasttext
import os
import sys


class LanguageIdentification:
    min_confidence = 0.70


    def __init__(self) -> None:
        # Charger le modèle FastText avec le chemin absolu
        pretrained_lang_model = os.path.join(os.path.dirname(__file__), "../assets/models/lid.176.bin")
        self.model = fasttext.load_model(pretrained_lang_model)

    def predict_lang(self, text):
        if not isinstance(text, str):
            raise ValueError("Le paramètre 'text' doit être une chaîne de caractères.")

        # Obtenez le résultat du modèle
        lang, confidence = self.model.predict(text, k=1)
        confidence_value = confidence[0]

        # Vérification de la confiance minimale
        if confidence_value < self.min_confidence:
            raise ValueError(f"Confiance insuffisante pour la détection de la langue : {confidence_value * 100:.2f}%")

        return lang, confidence

    def stat_print(self, text):
        try:
            lang, confidence = self.predict_lang(text)
            print(f"Langue prédite : {lang[0]} avec une confiance de {round(confidence[0] * 100, 2)}%")

            return lang, confidence
        except ValueError as e:
            print(f"Erreur : {e}")
            sys.exit(1)