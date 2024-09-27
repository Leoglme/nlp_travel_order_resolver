import fasttext

class LanguageIdentification:
    def __init__(self) -> None:
        pretrained_lang_model = "../lid.176.bin"
        self.model = fasttext.load_model(pretrained_lang_model)

    def predict_lang(self, text):
        if not isinstance(text, str):
            raise ValueError("Le paramètre 'text' doit être une chaîne de caractères.")
        # Obtenez le résultat du modèle
        print( self.model.predict(text, k=1))
        return self.model.predict(text, k=1)

    def stat_print(self, text):
        (lang, confidence) = self.predict_lang(text)
        print(f"Langue prédite : {lang[0]} avec une confiance de {round(confidence[0] * 100, 2)}%")
        return lang, confidence
