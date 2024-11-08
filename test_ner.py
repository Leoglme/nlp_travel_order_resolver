import os

# Hide TensorFlow warnings
os.environ['TF_CPP_MIN_LOG_LEVEL'] = '2'

from models.camembert_ner_model import CamembertNERModel

# Liste des textes et des départs/arrivées attendus (None si aucun trajet)
texts = [
    ("Je vais acheter des croissants à la boulangerie à Paris", (None, None)),
    ("Nous partirons demain matin de Nice pour rejoindre Marseille", ("Nice", "Marseille")),
    ("Il a prévu de partir à vélo pour visiter le parc", (None, None)),
    ("Je réserve un taxi pour aller de Lyon à Grenoble", ("Lyon", "Grenoble")),
    ("Je veux faire une balade en forêt à côté de chez moi", (None, None)),
    ("Nous avons acheté des billets pour un train de Lille à Bordeaux", ("Lille", "Bordeaux")),
    ("Elle va partir de Montpellier en bus pour rejoindre Toulouse", ("Montpellier", "Toulouse")),
    ("On va simplement passer la soirée chez un ami à Nantes", (None, None)),
    ("Il m'a dit qu'il prévoyait de partir en vacances à Marseille", (None, None)),
    ("Je vais rendre visite à ma grand-mère à Lyon ce week-end", (None, None)),
    ("Ils préparent un voyage de Paris à Amsterdam pour l'été prochain", ("Paris", "Amsterdam")),
    ("Je vais me balader dans le parc avec mon chien.", (None, None)),
    ("On se retrouve à Paris avant de partir pour Lille", ("Paris", "Lille")),
    ("Elle a réservé un billet pour aller à Marseille en train", (None, None)),
    ("Nous partirons de Toulouse pour une semaine à Nice", ("Toulouse", "Nice")),
    ("Je vais acheter des légumes au marché à Bordeaux", (None, None)),
    ("Il prévoit de conduire de Paris à Lyon pour les vacances", ("Paris", "Lyon")),
    ("Je vais faire du shopping à Nice ce samedi", (None, None)),
    ("Elle prévoit de prendre un train de Paris à Lille demain matin", ("Paris", "Lille")),
    ("J'habite à Rennes, je suis actuellement à paris et je veux retourner chez moi", ("Paris", "Rennes")),
    ("Je vais passer l’été chez mon oncle à Marseille", (None, None)),
    ("On organise un événement à Lyon pour la semaine prochaine", (None, None)),
    ("Je dois passer chez moi avant de partir pour Bordeaux", (None, None)),
    ("Il partira de Bordeaux pour une réunion à Toulouse", ("Bordeaux", "Toulouse")),
    ("Un jour, j’aimerais partir à l’aventure à Tokyo", (None, None)),
    ("Elle rêve d’aller de Lille à Marseille en vélo", ("Lille", "Marseille")),
    ("Je me demande ce que ça ferait de voyager de Paris à Barcelone", ("Paris", "Barcelone")),
    ("On discute souvent de ses voyages à Lille.", (None, None)),
    ("Je pars à pied tous les matins pour faire un tour du quartier.", (None, None)),
    ("Ils vont arriver de Marseille pour la réunion.", (None, None)),
    ("Il vient de Nice pour assister à la conférence", (None, None)),
    ("Je pense prendre le bus depuis le centre-ville", (None, None)),
    ("Je vais voir mes parents qui vivent à Nantes", (None, None)),
    ("Peut-on partir de Paris pour arriver à Marseille en moins de trois heures ?", ("Paris", "Marseille")),
    ("Si je partais demain, est-ce que je pourrais rejoindre Lyon sans escale ?", (None, None)),
    ("Pourrais-je aller de Bordeaux à Toulouse en bus ?", ("Bordeaux", "Toulouse")),
    ("Est-ce que tu as déjà pensé à aller de Marseille à Nice en vélo ?", ("Marseille", "Nice"))
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