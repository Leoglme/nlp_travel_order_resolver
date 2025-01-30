import csv
import heapq
from typing import List, Dict, Tuple

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
        self.csv_file_path = 'assets/data_sncf/organized_trips.csv'
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
                dep, arr = row['departure_city'].lower(), row['arrival_city'].lower()
                travel_time = int(row['travel_time'])  # travel time in minutes

                # Convert coordinates to float and store locations
                dep_coords = (float(row['departure_coordinates'].split(',')[0]), float(row['departure_coordinates'].split(',')[1]))
                arr_coords = (float(row['arrival_coordinates'].split(',')[0]), float(row['arrival_coordinates'].split(',')[1]))

                # Create or update the location dictionaries
                if dep not in self.locations:
                    self.locations[dep] = RoutePoint(row['departure_station'], dep, *dep_coords)
                if arr not in self.locations:
                    self.locations[arr] = RoutePoint(row['arrival_station'], arr, *arr_coords)

                # Add the edges in both directions since routes are bidirectional
                if dep not in self.graph:
                    self.graph[dep] = []
                if arr not in self.graph:
                    self.graph[arr] = []
                self.graph[dep].append((arr, travel_time))
                self.graph[arr].append((dep, travel_time))

    def _dijkstra(self, start: str, end: str) -> Tuple[List[Tuple[str, int]], int]:
        """
        Finds the shortest path and calculates the total travel time between two stations using Dijkstra's algorithm.

        Args:
            start (str): The starting station name.
            end (str): The destination station name.

        Returns:
            Tuple[List[Tuple[str, int]], int]: A tuple with a list of tuples (station, cumulative time at each station)
                                               representing the shortest path and the total travel time.
        """
        queue = [(0, start, [])]  # priority queue of (total_travel_time, station, path)
        visited = set()

        while queue:
            (travel_time, station, path) = heapq.heappop(queue)
            if station in visited:
                continue
            visited.add(station)

            # Record path with current station and cumulative travel time
            path = path + [(station, travel_time)]
            if station == end:
                return path, travel_time  # Return path with cumulative times and total travel time

            for neighbor, time in self.graph.get(station, []):
                if neighbor not in visited:
                    heapq.heappush(queue, (travel_time + time, neighbor, path))

        return [], 0

    def find_shortest_route(self, departure: str, destination: str) -> Dict:
        """
        Finds the shortest route between departure and destination stations.

        Args:
            departure (str): The name of the departure city.
            destination (str): The name of the destination city.

        Returns:
            Dict: Contains departure, destination, route points, each segment's travel time, and total travel time.
        """
        departure = departure.lower()
        destination = destination.lower()
        path_with_times, total_travel_time = self._dijkstra(departure, destination)
        if not path_with_times:
            return {"error": "No route found between the specified stations."}

        route = []
        previous_time = 0
        for station, cumulative_time in path_with_times:
            location = self.locations[station]
            segment_time = cumulative_time - previous_time  # Calculate travel time for this segment
            route.append({
                "id": location.point_id,
                "name": location.name,
                "latitude": location.latitude,
                "longitude": location.longitude,
                "travel_time": segment_time
            })
            previous_time = cumulative_time

        return {
            "departure": departure,
            "destination": destination,
            "route": route,
            "total_travel_time": total_travel_time  # Total travel time in minutes
        }