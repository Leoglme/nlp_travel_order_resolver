import csv
import heapq
from tqdm import tqdm
from collections import defaultdict


class SNCFRouteFinder:
    def __init__(self):
        self.stops = self.load_stops()
        self.routes = self.load_routes()
        self.stop_times = self.load_stop_times()
        self.graph = self.build_graph_optimized()  # Utilisation de la nouvelle méthode

    @staticmethod
    def load_stops():
        stops = {}
        file_path = 'assets/data_sncf/stops.txt'
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in tqdm(reader, desc="Loading stops", unit="stop"):
                stops[row['stop_id']] = row['stop_name']
        return stops

    @staticmethod
    def load_routes():
        file_path = 'assets/data_sncf/routes.txt'
        routes = {}
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in tqdm(reader, desc="Loading routes", unit="route"):
                routes[row['route_id']] = row['route_long_name']
        return routes

    @staticmethod
    def load_stop_times():
        file_path = 'assets/data_sncf/stop_times.txt'
        stop_times = defaultdict(list)  # Utilisation d'un defaultdict pour stocker par trip_id
        with open(file_path, mode='r', encoding='utf-8') as file:
            reader = csv.DictReader(file)
            for row in tqdm(reader, desc="Loading stop times", unit="stop time"):
                stop_times[row['trip_id']].append({
                    'trip_id': row['trip_id'],
                    'stop_id': row['stop_id'],
                    'arrival_time': row['arrival_time'],
                    'departure_time': row['departure_time'],
                    'stop_sequence': int(row['stop_sequence'])
                })
        return stop_times

    def build_graph_optimized(self):
        graph = defaultdict(list)

        for trip_id, stop_times in tqdm(self.stop_times.items(), desc="Building graph", unit="trip"):
            # Trier par 'stop_sequence' pour que les arrêts soient dans l'ordre
            stop_times = sorted(stop_times, key=lambda x: x['stop_sequence'])

            for i in range(len(stop_times) - 1):
                current_stop = stop_times[i]
                next_stop = stop_times[i + 1]
                # Calcul du temps entre les arrêts actuels et suivants
                time_diff = self.calculate_time_difference(current_stop, next_stop)
                graph[current_stop['stop_id']].append((next_stop['stop_id'], time_diff))

        return graph

    @staticmethod
    def calculate_time_difference(stop_time, next_stop_time):
        h1, m1, _ = map(int, stop_time['departure_time'].split(':'))
        h2, m2, _ = map(int, next_stop_time['arrival_time'].split(':'))
        return (h2 - h1) * 60 + (m2 - m1)

    def find_shortest_route(self, departure, destination):
        departure_ids = self.get_stop_ids(departure)
        destination_ids = self.get_stop_ids(destination)

        if not departure_ids or not destination_ids:
            return None

        # Trouver le meilleur itinéraire entre toutes les combinaisons de gares de départ et d'arrivée
        best_route = None
        shortest_time = float('inf')

        for dep_id in departure_ids:
            for dest_id in destination_ids:
                route = self.dijkstra(dep_id, dest_id)
                if route:
                    # Récupérer les informations d'arrêt complètes pour calculer le temps total
                    route_time = sum(
                        self.calculate_time_difference(self.get_stop_time(route[i]), self.get_stop_time(route[i + 1]))
                        for i in range(len(route) - 1)
                    )
                    if route_time < shortest_time:
                        best_route = route
                        shortest_time = route_time

        return best_route

    def get_stop_time(self, stop_id):
        """Récupère l'arrêt complet (avec heures d'arrivée et de départ) basé sur le stop_id"""
        for trip in self.stop_times.values():
            for stop in trip:
                if stop['stop_id'] == stop_id:
                    return stop
        return None

    def get_stop_ids(self, city_name):
        """
        Récupère les IDs des arrêts associés à une ville (plusieurs gares possibles).
        """
        stop_ids = []
        for stop_id, stop_name_value in self.stops.items():
            if city_name.lower() in stop_name_value.lower():
                stop_ids.append(stop_id)
        return stop_ids

    def dijkstra(self, start, goal):
        queue = [(0, start, [])]
        visited = set()
        total_stops = len(self.graph)  # Number of stops to give tqdm an idea of total progress

        with tqdm(total=total_stops, desc="Finding shortest route", unit="stop") as progress_bar:
            while queue:
                (cost, node, path) = heapq.heappop(queue)
                if node in visited:
                    continue

                visited.add(node)
                path = path + [node]

                if node == goal:
                    return path

                for neighbor, weight in self.graph.get(node, []):
                    if neighbor not in visited:
                        heapq.heappush(queue, (cost + weight, neighbor, path))

                progress_bar.update(1)

        return None