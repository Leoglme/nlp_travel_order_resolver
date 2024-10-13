from models.travel_intent_classifier_model import TravelIntentClassifierModel

if __name__ == '__main__':
    texts: list = [
        "Je vais acheter des croissants à la boulangerie à Paris.",
        "Nous partirons demain matin de Nice pour rejoindre Marseille.",
        "Il a prévu de partir à vélo pour visiter le parc.",
        "Je réserve un taxi pour aller de Lyon à Grenoble.",
        "Je veux faire une balade en forêt à côté de chez moi.",
        "Nous avons acheté des billets pour un train de Lille à Bordeaux.",
        "Elle va partir de Montpellier en bus pour rejoindre Toulouse.",
        "On va simplement passer la soirée chez un ami à Nantes.",
        "Il m'a dit qu'il prévoyait de partir en vacances à Marseille.",
        "Demain, je prends un avion de Paris à New York.",
        "Je vais rendre visite à ma grand-mère à Lyon ce week-end.",
        "Ils préparent un voyage de Paris à Amsterdam pour l'été prochain.",
        "Je vais me balader dans le parc avec mon chien.",
        "On se retrouve à Paris avant de partir pour Lille.",
        "Elle a réservé un billet pour aller à Marseille en train.",
        "Nous partirons de Toulouse pour une semaine à Nice.",
        "Je vais acheter des légumes au marché à Bordeaux.",
        "Il prévoit de conduire de Paris à Lyon pour les vacances.",
        "Je vais faire du shopping à Nice ce samedi.",
        "Elle prévoit de prendre un train de Paris à Lille demain matin."
    ]
    # Model for verify valid sentence (subject is Ok)
    trip_intent_classifier_model = TravelIntentClassifierModel()

    # Map texts
    for text in texts:
        # Verify if the sentence is a trip-related sentence
        prediction = trip_intent_classifier_model.predict(text)

        # If the sentence is a trip-related sentence
        if prediction == 1:
            print("OK: {}".format(text))
        else:
            print("NOT_OK: {}".format(text))
