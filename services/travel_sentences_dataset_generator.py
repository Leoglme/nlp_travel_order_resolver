import csv
import os
from services.city_manager import CityManager
from services.sentence_template_manager import SentenceTemplateManager
from services.city_template_filler_manager import CityTemplateFillerManager

"""
This class is responsible for generating a dataset containing cities, sentence templates and sentences with cities.
"""


class TravelSentencesDatasetGenerator:
    def __init__(self, city_output_file="datasets/city.csv", template_output_file="datasets/sentence_templates.csv",
                 filled_output_file="datasets/sentences_with_cities.csv"):
        self.city_output_file = city_output_file
        self.template_output_file = template_output_file
        self.filled_output_file = filled_output_file
        self.city_manager = CityManager()
        self.sentence_template_manager = SentenceTemplateManager(output_file=self.template_output_file)
        self.city_template_filler = CityTemplateFillerManager(city_file=self.city_output_file,
                                                              template_file=self.template_output_file,
                                                              output_file=self.filled_output_file)

    """
    Generates a CSV file containing formatted cities from data retrieved via CityManager.
    """

    def generate_city_csv(self):
        # Create the folder if necessary
        output_dir = os.path.dirname(self.city_output_file)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Directory {output_dir} created.")

        # Retrieve cities from CityManager
        cities = self.city_manager.fetch_cities()
        if not cities:
            print("No cities recovered.")
            return

        # Format cities for CSV
        formatted_cities = self.city_manager.get_cities_names(cities)

        # Write formatted cities to a CSV file
        with open(self.city_output_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["city"])  # En-tête du CSV
            for city in formatted_cities:
                writer.writerow([city])

        print(f"File {self.city_output_file} generated with {len(formatted_cities)} cities.")

    """
    Generates a CSV file containing sentence templates.
    """

    def generate_sentence_template_csv(self, num_templates=100):
        # Create the folder if necessary
        output_dir = os.path.dirname(self.template_output_file)
        if not os.path.exists(output_dir):
            os.makedirs(output_dir)
            print(f"Dossier {output_dir} créé.")

        # Generate sentence templates
        templates = self.sentence_template_manager.generate_templates(num_templates)

        # Save templates to a CSV file
        self.sentence_template_manager.save_templates_to_csv(templates)

    """
    Replaces placeholders {departure_city} and {destination_city} with real cities.
    """

    def generate_filled_templates_csv(self):
        # Use CityTemplateFillerManager to fill templates with real cities
        self.city_template_filler.fill_templates_with_cities()

    """
    Generates a complete dataset with cities, sentence templates and sentences populated with cities.
    """

    def generate_dataset(self):
        self.generate_city_csv()
        self.generate_sentence_template_csv(num_templates=1000)
        self.generate_filled_templates_csv()
