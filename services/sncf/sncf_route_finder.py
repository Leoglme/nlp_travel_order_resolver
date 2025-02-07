import csv
import heapq
from typing import List, Dict, Tuple
import os


class RoutePoint:
    """
    A class representing a point on the route with essential details.

    Attributes:
        point_id (str): Unique identifier for the route point (station or stop ID).
        name (str): Name of the route point (station or city).
        latitude (float): Latitude of the route point.
        longitude (float): Longitude of the route point.
    """

    def __init__(self, point_id: str, name: str, latitude: float, longitude: float):
        self.point_id = point_id
        self.name = name
        self.latitude = latitude
        self.longitude = longitude


class SNCFRouteFinder:
    """
    A class to find the shortest route between two points in a rail network.

    Attributes:
        graph (dict): A dictionary representing the graph of connected routes.
        locations (dict): A dictionary to store station data with coordinates.
    """

    def __init__(self):
        """
        Initializes the SncfRouteFinder by loading the route data from a CSV file.
        """
        project_root = os.path.abspath(os.path.join(os.path.dirname(__file__), "../.."))
        self.csv_file_path = os.path.join(project_root, "assets/data_sncf/organized_trips.csv")
        self.graph = {}  # adjacency list representation of graph
        self.locations = {}  # to store station data with coordinates
        self._load_data()

    def _load_data(self):
        """
        Loads route data from the CSV file and initializes the graph and locations.

        Each route between two stations is stored as an edge in the graph with
        travel time as the weight, and stations are stored in the locations dictionary.
        """
        with open(self.csv_file_path, 'r', encoding='utf-8') as csvfile:
            reader = csv.DictReader(csvfile)
            for row in reader:
                dep = row['departure_city'].lower()
                arr = row['arrival_city'].lower()
                travel_time = int(row['travel_time'])

                # Conversion des coordonnées
                dep_coords = tuple(map(float, row['departure_coordinates'].split(',')))
                arr_coords = tuple(map(float, row['arrival_coordinates'].split(',')))

                # Initialiser la structure pour la ville si elle n'existe pas déjà
                if dep not in self.locations:
                    self.locations[dep] = {}
                if arr not in self.locations:
                    self.locations[arr] = {}

                # Pour la ville de départ, stocker ou mettre à jour la gare
                dep_station = row['departure_station']
                if dep_station not in self.locations[dep]:
                    self.locations[dep][dep_station] = {
                        "station": RoutePoint(dep_station, dep, *dep_coords),
                        "count": 1
                    }
                else:
                    self.locations[dep][dep_station]["count"] += 1

                # Pour la ville d'arrivée, faire de même
                arr_station = row['arrival_station']
                if arr_station not in self.locations[arr]:
                    self.locations[arr][arr_station] = {
                        "station": RoutePoint(arr_station, arr, *arr_coords),
                        "count": 1
                    }
                else:
                    self.locations[arr][arr_station]["count"] += 1

                # Construire le graphe (en utilisant toujours la ville comme nœud)
                if dep not in self.graph:
                    self.graph[dep] = []
                if arr not in self.graph:
                    self.graph[arr] = []
                self.graph[dep].append((arr, travel_time))
                self.graph[arr].append((dep, travel_time))

    def _dijkstra(self, start: str, end: str) -> Tuple[List[Tuple[str, int]], int, int]:
        """
        Finds the shortest path and calculates the total travel time between two stations using Dijkstra's algorithm.

        Args:
            start (str): The starting station name.
            end (str): The destination station name.

        Returns:
            Tuple[List[Tuple[str, int]], int]: A tuple with a list of tuples (station, cumulative time at each station)
                                               representing the shortest path and the total travel time.
        """
        # Initialisation : on commence avec 0 arrêt, 0 temps, à la station de départ et un chemin vide.
        heap = [(0, 0, start, [(start, 0)])]
        # Dictionnaire pour enregistrer, pour chaque station, le meilleur (stops, travel_time) trouvé
        best = {start: (0, 0, [(start, 0)])}

        while heap:
            stops, travel_time, station, path = heapq.heappop(heap)

            # Si nous atteignons la destination, on renvoie immédiatement le chemin trouvé.
            if station == end:
                return path, stops, travel_time

            # Pour chaque voisin accessible depuis la station actuelle
            for neighbor, t in self.graph.get(station, []):
                new_stops = stops + 1
                new_time = travel_time + t
                candidate = (new_stops, new_time)
                # Si ce chemin est meilleur (moins d'arrêts, ou même arrêts et moins de temps) que ce que l'on a déjà trouvé pour ce voisin...
                if neighbor not in best or candidate < best[neighbor]:
                    best[neighbor] = (new_stops, new_time, path + [(neighbor, new_time)])
                    new_path = path + [(neighbor, new_time)]
                    heapq.heappush(heap, (new_stops, new_time, neighbor, new_path))

        # Aucun chemin trouvé
        return [], 0, 0

    def find_shortest_route(self, departure: str, destination: str) -> Dict:
        departure = departure.lower()
        destination = destination.lower()
        path_with_times, stops, total_travel_time = self._dijkstra(departure, destination)
        if not path_with_times:
            return {"error": "No route found between the specified stations."}

        route = []
        previous_time = 0
        # Pour chaque ville du chemin, on sélectionne la gare la plus représentative
        for station, cumulative_time in path_with_times:
            segment_time = cumulative_time - previous_time
            previous_time = cumulative_time

            stations_for_city = self.locations[station]
            chosen_station = max(stations_for_city.values(), key=lambda x: x["count"])["station"]
            route.append({
                "id": chosen_station.point_id,
                "name": chosen_station.name,
                "latitude": chosen_station.latitude,
                "longitude": chosen_station.longitude,
                "travel_time": segment_time
            })

        return {
            "departure": departure,
            "destination": destination,
            "route": route,
            "total_travel_time": total_travel_time,
            "stops": stops
        }
