import csv
import os
from services.city_manager import CityManager
from services.sentence_template_manager import SentenceTemplateManager
from services.city_template_filler_manager import CityTemplateFillerManager

class DatasetGenerator:
    def __init__(self, city_output_file="datasets/city.csv", template_output_file="datasets/sentence_templates.csv", filled_output_file="datasets/sentences_with_cities.csv"):
        self.city_output_file = city_output_file
        self.template_output_file = template_output_file
        self.filled_output_file = filled_output_file
        self.city_manager = CityManager()
        self.sentence_template_manager = SentenceTemplateManager(output_file=self.template_output_file)
        self.city_template_filler = CityTemplateFillerManager(city_file=self.city_output_file,
                                                       template_file=self.template_output_file,
                                                       output_file=self.filled_output_file)

    def generate_city_csv(self):
        """
        Génère un fichier CSV contenant les villes formatées à partir des données récupérées via CityManager.
        """

        # Créer le dossier si nécessaire
        output_dir = os.path.dirname(self.city_output_file)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Dossier {output_dir} créé.")

        # Récupérer les villes depuis CityManager
        cities = self.city_manager.fetch_cities()
        if not cities:
            print("Aucune ville récupérée.")
            return

        # Formater les villes pour le CSV
        formatted_cities = self.city_manager.get_cities_names(cities)

        # Écrire les villes formatées dans un fichier CSV
        with open(self.city_output_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["city"])  # En-tête du CSV
            for city in formatted_cities:
                writer.writerow([city])

        print(f"Fichier {self.city_output_file} généré avec {len(formatted_cities)} villes.")

    def generate_sentence_template_csv(self, num_templates=100):
        """
        Génère un fichier CSV contenant des templates de phrases.
        """
        # Créer le dossier si nécessaire
        output_dir = os.path.dirname(self.template_output_file)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Dossier {output_dir} créé.")

        # Générer les templates de phrases
        templates = self.sentence_template_manager.generate_templates(num_templates)

        # Sauvegarder les templates dans un fichier CSV
        self.sentence_template_manager.save_templates_to_csv(templates)

    def generate_filled_templates_csv(self):
        """
        Remplace les placeholders {departure_city} et {destination_city} avec des villes réelles.
        """
        # Utiliser CityTemplateFillerManager pour remplir les templates avec des villes réelles
        self.city_template_filler.fill_templates_with_cities()
    def generate_dataset(self):
        """
        Génère un dataset complet avec les villes, les templates de phrases et les phrases remplies avec des villes.
        """
        self.generate_city_csv()
        self.generate_sentence_template_csv(num_templates=200)
        self.generate_filled_templates_csv()