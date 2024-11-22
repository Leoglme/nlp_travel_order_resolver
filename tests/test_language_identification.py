import sys
import os

sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.language_identifications import LanguageIdentification

testing_text = 'As-salamu alaykum, kayfa haluka?'

lang_identifier = LanguageIdentification()
lang, confidence = lang_identifier.stat_print(testing_text)


# Print lang, confidence
print(f'lang: {lang[0]}, confidence: {confidence}')