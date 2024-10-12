import fasttext
import os
import sys


class LanguageIdentification:
    min_confidence = 0.70

    """
    Class to identify the language of a given text.
    """
    def __init__(self) -> None:
        pretrained_lang_model = os.path.join(os.path.dirname(__file__), "../assets/models/lid.176.bin")
        self.model = fasttext.load_model(pretrained_lang_model)

    """
    Predicts the language of the given text.
    """
    def predict_lang(self, text):
        if not isinstance(text, str):
            raise ValueError("The 'text' parameter must be a character string.")

        # Get the model result
        lang, confidence = self.model.predict(text, k=1)
        confidence_value = confidence[0]

        # Minimum trust check
        if confidence_value < self.min_confidence:
            raise ValueError(f"Insufficient confidence for language detection: {confidence_value * 100:.2f}%")

        return lang, confidence

    """
    Prints the predicted language and its confidence.
    """
    def stat_print(self, text):
        try:
            lang, confidence = self.predict_lang(text)
            print(f"Predicted language: {lang[0]} with a confidence of {round(confidence[0] * 100, 2)}%")

            return lang, confidence
        except ValueError as e:
            print(f"Error : {e}")
            sys.exit(1)