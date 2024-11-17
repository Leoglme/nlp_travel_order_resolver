import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.language_detection import LanguageIdentification

testing_text = 'Je voudrais aller de Rennes à Biarritz'

lang_identifier = LanguageIdentification()
lang, confidence = lang_identifier.stat_print(testing_text)


# Print lang, confidence
print(f'lang: {lang[0]}, confidence: {confidence}')