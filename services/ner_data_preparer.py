import csv
from transformers import CamembertTokenizerFast

class NERDataPreparer:
    def __init__(self, csv_file):
        self.csv_file = csv_file
        self.tokenizer = CamembertTokenizerFast.from_pretrained("camembert-base")

    def generate_tokens_and_ner_tags(self):
        tokens_list = []
        ner_tags_list = []

        with open(self.csv_file, 'r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in reader:
                text = row.get('text')
                departure = row.get('departure')
                destination = row.get('destination')

                if not text or not departure or not destination:
                    print(f"Invalid row skipped: {row}")
                    continue

                tokens = self.tokenizer.tokenize(text)
                ner_tags = [0] * len(tokens)  # Initialiser les NER tags à 0 (O pour "Outside")

                # Générer les NER tags pour les départs et destinations
                self.assign_ner_tags(tokens, departure, ner_tags, 1)  # 1 pour "B-city" (départ)
                self.assign_ner_tags(tokens, destination, ner_tags, 2)  # 2 pour "I-city" (destination)

                # Vérification des correspondances entre la longueur des tokens et des NER tags
                if len(tokens) != len(ner_tags):
                    print(f"Mismatch tokens and NER tags for row: {row}")
                    continue

                tokens_list.append(tokens)
                ner_tags_list.append(ner_tags)

        return tokens_list, ner_tags_list

    def assign_ner_tags(self, tokens, entity, ner_tags, tag_value):
        """
        Assigne les NER tags aux tokens correspondant à une entité donnée (départ ou destination).
        """
        entity_tokens = self.tokenizer.tokenize(entity)

        for i in range(len(tokens) - len(entity_tokens) + 1):
            if tokens[i:i + len(entity_tokens)] == entity_tokens:
                for j in range(len(entity_tokens)):
                    ner_tags[i + j] = tag_value
                break  # Une fois l'entité trouvée, on s'arrête

    def generate_ner_tags(self, text, departure, destination):
        """
        Génère les NER tags pour une phrase donnée en fonction des entités de départ et de destination.
        """
        tokens = self.tokenizer.tokenize(text)
        ner_tags = [0] * len(tokens)  # Initialiser tous les tags à 0 (O pour Outside)

        # Assignation des tags pour les entités
        self.assign_ner_tags(tokens, departure, ner_tags, 1)  # B-city pour le départ
        self.assign_ner_tags(tokens, destination, ner_tags, 2)  # I-city pour la destination

        return tokens, ner_tags