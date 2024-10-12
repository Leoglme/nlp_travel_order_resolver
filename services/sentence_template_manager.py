import csv
import random

"""
This class is responsible for generating sentence templates.
"""


class SentenceTemplateManager:
    def __init__(self, output_file="datasets/sentence_templates.csv"):
        self.output_file = output_file

        # Sentence models with placeholders
        self.templates = [
            "Je veux aller de {departure_city} à {destination_city}.",
            "Je souhaite voyager de {departure_city} vers {destination_city}.",
            "Partir de {departure_city} pour {destination_city}.",
            "Je voudrais me rendre à {destination_city} depuis {departure_city}.",
            "Je dois aller de {departure_city} à {destination_city}.",
            "Voyager de {departure_city} à {destination_city} est prévu.",
            "Prévois un trajet de {departure_city} à {destination_city}.",
            "Je vais me déplacer de {departure_city} à {destination_city}."
        ]

        # Additional variations with more verbs and prepositions
        self.verbs = ["aller", "voyager", "partir", "se rendre", "prévoir", "se déplacer"]
        self.prepositions = ["de", "depuis", "vers", "à", "pour"]

    """
    Generates a number of templates from models and variations.
    """

    def generate_templates(self, num_templates=100):
        templates = []

        for i in range(num_templates):
            # Choose a model randomly
            template = random.choice(self.templates)

            # Replace verbs and prepositions if necessary
            random_verb = random.choice(self.verbs)
            random_preposition = random.choice(self.prepositions)

            # Replace verbs and prepositions in templates
            if "{verb}" in template:
                template = template.replace("{verb}", random_verb)
            if "{preposition}" in template:
                template = template.replace("{preposition}", random_preposition)

            # Generate a template without cities at the moment
            templates.append({
                "text": template,
                "departure": "{departure_city}",
                "destination": "{destination_city}"
            })

        return templates

    """
    Saves the generated templates in a CSV file.
    """

    def save_templates_to_csv(self, templates):
        with open(self.output_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["text", "departure_placeholder", "destination_placeholder"])

            for template in templates:
                writer.writerow([template["text"], template["departure"], template["destination"]])

        print(f"{len(templates)} templates were generated and saved in {self.output_file}")
