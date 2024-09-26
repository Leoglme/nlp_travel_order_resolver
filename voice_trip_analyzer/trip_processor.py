import spacy

class TripProcessor:
    def __init__(self):
        self.nlp = spacy.load("fr_core_news_md")
        # Charger le modèle fine-tuné
        # self.nlp = spacy.load("/Users/quentin/Ecoles/Epitech/MSC-2/IA/T-AIA-901/Projet/ia/fine_tuned_model/model_voyage")

    def process_voice_text(self, text):
        if not text:
            print("Aucun texte reconnu.")
            return

        doc = self.nlp(text)

        departure_keywords = ["depuis", "de", "partant de"]
        arrival_keywords = ["à", "vers", "destination"]

        # Extraction des entités de localisation
        locations = [ent.text for ent in doc.ents if ent.label_ == "LOC"]
        print(locations)

        if len(locations) < 2:
            print("NOT_TRIP: Commande de voyage non reconnue.")
            return

        # Extraction des départs et arrivées
        departure, arrival = self.extract_locations(doc, departure_keywords, arrival_keywords)

        if departure and arrival:
            print(f"Départ : {departure}, Arrivée : {arrival}")
        else:
            print(f"Départ : {locations[0]}, Arrivée : {locations[1]}")

    def extract_locations(self, doc, departure_keywords, arrival_keywords):
        departure = None
        arrival = None

        for token in doc:
            if token.text.lower() in arrival_keywords:
                next_location = self.get_next_location(doc, token.i)
                if next_location:
                    arrival = next_location
            elif token.text.lower() in departure_keywords:
                next_location = self.get_next_location(doc, token.i)
                if next_location:
                    departure = next_location

        return departure, arrival

    def get_next_location(self, doc, current_index):
        # Chercher l'entité "LOC" après l'indice actuel
        for ent in doc.ents:
            if ent.label_ == "LOC" and ent.start > current_index:
                return ent.text
        return None
