from voice_recognizer import VoiceRecognizer
from trip_processor import TripProcessor
from time_processor import charger_graphe, dijkstra
import unidecode
from fuzzywuzzy import process

def normalize_city_name(city_name):
    # Convertir en minuscules, enlever les accents et abréger
    normalized_name = unidecode.unidecode(city_name.lower())
    normalized_name = normalized_name.replace("saint", "st").replace(" ",
                                                                     "")  # Remplace "saint" par "st" et enlève les espaces
    return normalized_name

def find_closest_city(city_name, city_to_station):
    normalized_city_name = normalize_city_name(city_name)
    # Normaliser les clés du dictionnaire pour comparaison
    normalized_stations = {normalize_city_name(city): city for city in city_to_station.keys()}

    # Trouver la ville la plus proche dans le dictionnaire
    closest_city, score = process.extractOne(normalized_city_name, normalized_stations.keys())
    if score > 80:  # seuil de confiance
        return normalized_stations[closest_city]
    return None

def main():
    # Charger le graphe et le dictionnaire ville -> gare
    csv_path = "/Users/quentin/Ecoles/Epitech/MSC-2/IA/T-AIA-901/Projet/students_project/timetables.csv"
    graph, city_to_station = charger_graphe(csv_path)

    recognizer = VoiceRecognizer()
    processor = TripProcessor()

    print("En attente de commande vocale...")
    voice_text = recognizer.record_and_convert()

    if voice_text:
        print(f"Texte reçu : {voice_text}")
        departure_city, arrival_city = processor.process_voice_text(voice_text)

        if departure_city and arrival_city:
            # Chercher les noms complets des gares correspondantes
            departure_station = city_to_station.get(departure_city, None)
            arrival_station = city_to_station.get(arrival_city, None)

            # Utiliser find_closest_city si la gare n'est pas trouvée
            if departure_station is None:
                closest_departure = find_closest_city(departure_city, city_to_station)
                if closest_departure:
                    departure_station = city_to_station[closest_departure]
                    print(f"Gare trouvée pour la ville de départ : {closest_departure} (station : {departure_station})")
                else:
                    print(f"Gare introuvable pour la ville de départ : {departure_city}")

            if arrival_station is None:
                closest_arrival = find_closest_city(arrival_city, city_to_station)
                if closest_arrival:
                    arrival_station = city_to_station[closest_arrival]
                    print(f"Gare trouvée pour la ville d'arrivée : {closest_arrival} (station : {arrival_station})")
                else:
                    print(f"Gare introuvable pour la ville d'arrivée : {arrival_city}")

            if departure_station and arrival_station:
                print(f"Départ : {departure_station}, Arrivée : {arrival_station}")

                # Trouver le chemin avec Dijkstra
                distance, path = dijkstra(graph, departure_station, arrival_station)
                print(f"Le chemin le plus court de {departure_station} à {arrival_station} est : {path} avec une durée totale de {distance} minutes.")
            else:
                print(f"Impossible de trouver les gares correspondantes pour {departure_city} ou {arrival_city}.")
        else:
            print("Impossible d'extraire les villes de départ et d'arrivée.")


if __name__ == "__main__":
    main()
