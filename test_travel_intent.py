from models.travel_intent_classifier_model import TravelIntentClassifierModel

# Liste des textes et des prédictions attendues (True = trajet, False = pas de trajet)
texts = [
    ("Je vais acheter des croissants à la boulangerie à Paris.", False),
    ("Nous partirons demain matin de Nice pour rejoindre Marseille.", True),
    ("Il a prévu de partir à vélo pour visiter le parc.", False),
    ("Je réserve un taxi pour aller de Lyon à Grenoble.", True),
    ("Je veux faire une balade en forêt à côté de chez moi.", False),
    ("Nous avons acheté des billets pour un train de Lille à Bordeaux.", True),
    ("Elle va partir de Montpellier en bus pour rejoindre Toulouse.", True),
    ("On va simplement passer la soirée chez un ami à Nantes.", False),
    ("Il m'a dit qu'il prévoyait de partir en vacances à Marseille.", False),
    ("Demain, je prends un avion de Paris à New York.", True),
    ("Je vais rendre visite à ma grand-mère à Lyon ce week-end.", False),
    ("Ils préparent un voyage de Paris à Amsterdam pour l'été prochain.", True),
    ("Je vais me balader dans le parc avec mon chien.", False),
    ("On se retrouve à Paris avant de partir pour Lille.", True),
    ("Elle a réservé un billet pour aller à Marseille en train.", True),
    ("Nous partirons de Toulouse pour une semaine à Nice.", True),
    ("Je vais acheter des légumes au marché à Bordeaux.", False),
    ("Il prévoit de conduire de Paris à Lyon pour les vacances.", True),
    ("Je vais faire du shopping à Nice ce samedi.", False),
    ("Elle prévoit de prendre un train de Paris à Lille demain matin.", True),
    ("J'habite à Rennes, je suis actuellement à paris et je veux retourner chez moi.", True),
    ("Je vais passer l’été chez mon oncle à Marseille.", False),
    ("On organise un événement à Lyon pour la semaine prochaine.", False),
    ("Je dois passer chez moi avant de partir pour Bordeaux.", False),
    ("Il partira de Bordeaux pour une réunion à Toulouse.", True),
    ("Un jour, j’aimerais partir à l’aventure à Tokyo.", False),
    ("Elle rêve d’aller de Lille à Marseille en vélo.", True),
    ("Je me demande ce que ça ferait de voyager de Paris à Barcelone.", True),
    ("On discute souvent de ses voyages à Lille.", False),
    ("Je pars à pied tous les matins pour faire un tour du quartier.", False),
    ("Ils planifient un projet qui les mènera de ville en ville.", False),
    ("Ils vont arriver de Marseille pour la réunion.", True),
    ("Il vient de Nice pour assister à la conférence.", True),
    ("Je pense prendre le bus depuis le centre-ville.", False),
    ("Je vais voir mes parents qui vivent à Nantes.", False),
    ("Peut-on partir de Paris pour arriver à Marseille en moins de trois heures ?", True),
    ("Si je partais demain, est-ce que je pourrais rejoindre Lyon sans escale ?", True),
    ("Pourrais-je aller de Bordeaux à Toulouse en bus ?", True),
    ("Est-ce que tu as déjà pensé à aller de Marseille à Nice en vélo ?", True)
]

# Initialiser le modèle
trip_intent_classifier_model = TravelIntentClassifierModel()

# Variables pour stocker les résultats
correct_predictions = 0
incorrect_texts = []

# Boucle sur les textes pour faire les prédictions et vérifier les résultats
for text, expected in texts:
    prediction = trip_intent_classifier_model.predict(text) == 1  # True si prédiction = 1, sinon False

    # Vérifier si la prédiction est correcte
    if prediction == expected:
        correct_predictions += 1
    else:
        incorrect_texts.append((text, expected, prediction))

# Calculer le pourcentage de réussite
success_rate = (correct_predictions / len(texts)) * 100

# Afficher le pourcentage de réussite et les textes incorrects
print(f"Taux de réussite : {success_rate:.2f}%")
if incorrect_texts:
    print("Textes avec des prédictions incorrectes :")
    for text, expected, prediction in incorrect_texts:
        print(f"Texte: {text} - Attendu: {expected} - Prédiction: {prediction}")
else:
    print("Toutes les prédictions sont correctes.")
