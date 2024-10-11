import csv
import random


class SentenceTemplateManager:
    def __init__(self, output_file="datasets/sentence_templates.csv"):
        self.output_file = output_file

        # Modèles de phrases avec placeholders
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

        # Variations supplémentaires avec plus de verbes et prépositions
        self.verbs = ["aller", "voyager", "partir", "se rendre", "prévoir", "se déplacer"]
        self.prepositions = ["de", "depuis", "vers", "à", "pour"]

    def generate_templates(self, num_templates=100):
        """
        Génère un nombre de templates à partir des modèles et variations.
        """
        templates = []

        for i in range(num_templates):
            # Choisir un modèle aléatoirement
            template = random.choice(self.templates)

            # Remplacer éventuellement les verbes et prépositions
            random_verb = random.choice(self.verbs)
            random_preposition = random.choice(self.prepositions)

            # Remplacer les verbes et prépositions dans les templates
            if "{verb}" in template:
                template = template.replace("{verb}", random_verb)
            if "{preposition}" in template:
                template = template.replace("{preposition}", random_preposition)

            # Générer un template sans villes pour le moment
            templates.append({
                "text": template,
                "departure": "{departure_city}",
                "destination": "{destination_city}"
            })

        return templates

    def save_templates_to_csv(self, templates):
        """
        Sauvegarde les templates générés dans un fichier CSV.
        """
        with open(self.output_file, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(["text", "departure_placeholder", "destination_placeholder"])

            for template in templates:
                writer.writerow([template["text"], template["departure"], template["destination"]])

        print(f"{len(templates)} templates ont été générés et enregistrés dans {self.output_file}")
