import csv
import os
import random
from tqdm import tqdm

"""
This class is responsible for generating a dataset containing sentences related to travel intent and non-travel intent.
The dataset will include examples of sentences that refer to trips (departure and arrival cities) and sentences that do not.
"""


class TravelIntentDatasetGenerator:
    def __init__(self, num_samples=1000, output_file="datasets/travel_intent_dataset.csv"):
        self.output_file = output_file
        self.num_samples = num_samples

        # Trip-related sentence components
        self.subjects_trip = ["Je", "Nous", "Elle", "Il", "Vous", "On", "Mon équipe", "Ma famille"]
        self.verbs_trip = ["veux aller", "pars", "cherche un itinéraire", "prévois de partir", "réserve un billet",
                           "vais prendre un train", "prends l'avion", "vais voyager"]
        self.prepositions_trip = ["de", "depuis", "vers", "à", "pour", "jusqu'à", "en direction de"]
        self.cities_trip = ["Biarritz", "Rennes", "Paris", "Lyon", "Marseille", "Nice", "Toulouse", "Bordeaux",
                            "Nantes", "Strasbourg", "Montpellier", "Lille"]

        # Non-trip-related sentence components
        self.subjects_non_trip = ["Je", "Nous", "Elle", "Il", "On", "Mon chien", "Ma sœur", "Mes amis"]
        self.verbs_non_trip = ["vais manger", "vais faire", "prévois de", "veux acheter", "vais me promener",
                               "vais cuisiner", "vais réparer", "dois nettoyer", "vais préparer", "veux regarder",
                               "vais lire"]
        self.objects_non_trip = ["une pomme", "les courses", "un livre", "un café", "une sieste", "une promenade",
                                 "un gâteau", "une voiture", "la télévision", "un film", "un vélo", "un repas",
                                 "la maison", "le dîner"]
        self.places_non_trip = ["chez moi", "dans le jardin", "au parc", "à la maison", "dans le garage",
                                "au centre commercial", "à la cuisine", "au cinéma"]

    """
    Generates a sentence related to a trip.
    """

    def generate_trip_sentence(self):
        subject = random.choice(self.subjects_trip)
        verb = random.choice(self.verbs_trip)
        preposition = random.choice(self.prepositions_trip)
        departure_city = random.choice(self.cities_trip)
        arrival_city = random.choice([city for city in self.cities_trip if city != departure_city])
        return f"{subject} {verb} {preposition} {departure_city} à {arrival_city}", 1

    """
    Generates a sentence unrelated to a trip.
    """

    def generate_non_trip_sentence(self):
        subject = random.choice(self.subjects_non_trip)
        verb = random.choice(self.verbs_non_trip)
        object_phrase = random.choice(self.objects_non_trip)
        place = random.choice(self.places_non_trip)
        return f"{subject} {verb} {object_phrase} {place}", 0

    """
    Generates a dataset of sentences, half of which are related to travel and the other half unrelated.
    Saves the dataset as a CSV file with a progress bar.
    """

    def generate_dataset(self):
        # Ensure output directory exists
        output_dir = os.path.dirname(self.output_file)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)

        dataset = []

        # Initialize tqdm progress bar
        with tqdm(total=self.num_samples, desc="Generating dataset", unit="sentence") as pbar:
            # Generate trip-related sentences
            for _ in range(self.num_samples // 2):
                dataset.append(self.generate_trip_sentence())
                pbar.update(1)

            # Generate non-trip-related sentences
            for _ in range(self.num_samples // 2):
                dataset.append(self.generate_non_trip_sentence())
                pbar.update(1)

        # Shuffle dataset to mix trip and non-trip examples
        random.shuffle(dataset)

        # Write the dataset to a CSV file
        with open(self.output_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["text", "label"])
            writer.writerows(dataset)

        print(f"Dataset of {self.num_samples} samples generated and saved to {self.output_file}")