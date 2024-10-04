import csv

class PathFinderManager:
    def __init__(self, timetable_file="assets/timetables.csv"):
        self.timetable_file = timetable_file
        self.routes = []
        self.load_timetable()

    def load_timetable(self):
        # Charger le fichier CSV timetables et stocker les informations des trajets
        with open(self.timetable_file, mode="r", encoding="utf-8") as f:
            reader = csv.DictReader(f, delimiter='\t')
            for row in reader:
                self.routes.append(row)

    def find_best_route(self, departure, destination):
        # Implémenter un algorithme pour trouver le meilleur itinéraire (Dijkstra, A*, etc.)
        # Pour simplifier, cela peut simplement retourner le trajet direct s'il existe
        best_route = None
        for route in self.routes:
            if departure in route['trajet'] and destination in route['trajet']:
                best_route = route['trajet']
                break

        if best_route:
            print(f"Itinéraire trouvé: {best_route}")
            return best_route
        else:
            print("Aucun itinéraire trouvé.")
            return None
