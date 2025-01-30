import os
import sys

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

# Hide TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from models.camembert_ner_model import CamembertNERModel

# Liste des textes et des départs/arrivées attendus (None si aucun trajet)
texts = [
    ("Je veux allez de Rennes à Paris", ("Rennes", "Paris")),
    ("J'habites à Nantes, je suis à Angers et je veux rentrer chez moi", ("Rennes", "Paris"))
]

# Initialiser le modèle
camembert_ner_model = CamembertNERModel()
camembert_ner_model.load_model()

# Variables pour stocker les erreurs uniquement
incorrect_texts = []

# Boucle sur les textes pour faire les prédictions et vérifier les résultats
for text, (expected_departure, expected_destination) in texts:
    # Extraire les villes de départ et de destination
    departure, destination = camembert_ner_model.extract_trip_details(text)

    # Vérifier si la prédiction est incorrecte
    if (departure != expected_departure) or (destination != expected_destination):
        incorrect_texts.append((text, expected_departure, expected_destination, departure, destination))

# Calculer le pourcentage de réussite
total_texts = len(texts)
correct_predictions = total_texts - len(incorrect_texts)
success_rate = (correct_predictions / total_texts) * 100

# Afficher le pourcentage de réussite et les erreurs uniquement
print(f"Taux de réussite : {success_rate:.2f}%")

if incorrect_texts:
    print("\nTextes avec des prédictions incorrectes :")
    for text, expected_departure, expected_destination, departure, destination in incorrect_texts:
        print(f"Texte: {text}")
        print(f"Départ attendu: {expected_departure}, Destination attendue: {expected_destination}")
        print(f"Départ prédit: {departure}, Destination prédite: {destination}")
else:
    print("Toutes les prédictions sont correctes.")