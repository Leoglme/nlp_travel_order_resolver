import csv
from tqdm import tqdm
import random

"""
This class is responsible for filling sentence templates with cities.
"""


class CityTemplateFillerManager:
    def __init__(self, city_file="datasets/city.csv", template_file="datasets/sentence_templates.csv",
                 output_file="datasets/sentences_with_cities.csv", max_lines=1000):
        self.city_file = city_file
        self.template_file = template_file
        self.output_file = output_file
        self.max_lines = max_lines

    """
    Load cities from the city.csv file.
    """

    def load_cities(self):
        cities = []
        with open(self.city_file, mode="r", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)
            for row in reader:
                cities.append(row[0])
        return cities

    """
    Loads templates from sentence_templates.csv.
    """

    def load_templates(self):
        templates = []
        with open(self.template_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f)
            for row in reader:
                templates.append(row)
        return templates

    """
    Replaces placeholders {departure_city} and {destination_city} with a random subset of city combinations.
    Limits the total number of lines generated based on the max_lines parameter.
    Generates combinations randomly without storing everything in memory.
    """

    def fill_templates_with_cities(self):
        cities = self.load_cities()
        templates = self.load_templates()

        # Calculate the total number of combinations to generate per template
        lines_per_template = self.max_lines // len(templates)

        with open(self.output_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["text", "departure", "destination"])  # En-tête du CSV

            # Use tqdm to display the progress bar
            with tqdm(total=self.max_lines, desc="Génération des phrases", unit="phrase") as pbar:
                for template in templates:
                    count = 0
                    while count < lines_per_template:
                        # Choose departure and arrival cities randomly without duplicates
                        departure_city, destination_city = random.sample(cities, 2)

                        # Replace placeholders in the template
                        text = template["text"].replace("{departure_city}", departure_city).replace(
                            "{destination_city}", destination_city)

                        # Add the row with the replaced cities
                        writer.writerow([text, departure_city, destination_city])

                        # Update the progress bar
                        pbar.update(1)

                        count += 1

        print(f"\nGeneration complete! {self.max_lines} sentences were generated in {self.output_file}.")
