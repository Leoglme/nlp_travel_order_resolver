import csv
from tqdm import tqdm
import random


class CityTemplateFillerManager:
    def __init__(self, city_file="datasets/city.csv", template_file="datasets/sentence_templates.csv",
                 output_file="datasets/sentences_with_cities.csv", max_lines=1000):
        self.city_file = city_file
        self.template_file = template_file
        self.output_file = output_file
        self.max_lines = max_lines

    def load_cities(self):
        """
        Charge les villes depuis le fichier city.csv.
        """
        cities = []
        with open(self.city_file, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # Sauter l'en-tête
            for row in reader:
                cities.append(row[0])  # Ajouter chaque ville dans la liste
        return cities

    def load_templates(self):
        """
        Charge les templates depuis sentence_templates.csv.
        """
        templates = []
        with open(self.template_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                templates.append(row)
        return templates

    def fill_templates_with_cities(self):
        """
        Remplace les placeholders {departure_city} et {destination_city} par un sous-ensemble aléatoire de combinaisons de villes.
        Limite le nombre total de lignes générées en fonction du paramètre max_lines.
        Génère les combinaisons aléatoirement sans tout stocker en mémoire.
        """
        cities = self.load_cities()
        templates = self.load_templates()

        # Calculer le nombre total de combinaisons à générer par template
        lines_per_template = self.max_lines // len(templates)

        with open(self.output_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["text", "departure", "destination", "status"])  # En-tête du CSV

            # Utiliser tqdm pour afficher la progress bar
            with tqdm(total=self.max_lines, desc="Génération des phrases", unit="phrase") as pbar:
                for template in templates:
                    count = 0
                    while count < lines_per_template:
                        # Choisir des villes de départ et d'arrivée aléatoirement sans doublon
                        departure_city, destination_city = random.sample(cities, 2)

                        # Remplacer les placeholders dans le template
                        text = template["text"].replace("{departure_city}", departure_city).replace(
                            "{destination_city}", destination_city)

                        # Ajouter la ligne avec les villes remplacées
                        writer.writerow([text, departure_city, destination_city, template["status"]])

                        # Mettre à jour la progress bar
                        pbar.update(1)

                        count += 1

        print(f"\nGénération terminée ! {self.max_lines} phrases ont été générées dans {self.output_file}.")
