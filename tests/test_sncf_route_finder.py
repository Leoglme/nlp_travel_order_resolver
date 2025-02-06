import os
import sys

# Add the project root directory to the Python path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from services.sncf.sncf_route_finder import SNCFRouteFinder

departures = ["Rennes"]
destinations = ["Biarritz"]

for departure in departures:
    for destination in destinations:
        if departure != destination:
            print(f"Departure: {departure}, Destination: {destination}")
            sncf_route_finder = SNCFRouteFinder()
            route = sncf_route_finder.find_shortest_route(departure, destination)
            if route:
                print(f"Best route found: {route}")
            else:
                print("No route found between the two stations.")