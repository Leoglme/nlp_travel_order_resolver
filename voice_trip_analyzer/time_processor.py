import pandas as pd
import heapq

def charger_graphe(csv_path):
    df = pd.read_csv(csv_path, delimiter='\t')
    graph = {}
    city_to_station = {}  # Dictionnaire pour relier villes et gares

    for _, row in df.iterrows():
        trajet = row['trajet']
        duree = row['duree']

        try:
            depart, arrivee = trajet.split(' - ')
        except ValueError:
            print(f"Erreur en traitant le trajet : {trajet}")
            continue

        # Extraire le nom de la ville depuis le nom de la gare
        ville_depart = depart.replace("Gare de ", "").strip()
        ville_arrivee = arrivee.replace("Gare de ", "").strip()

        # Associer la ville au nom complet de la gare
        city_to_station[ville_depart] = depart
        city_to_station[ville_arrivee] = arrivee

        # Ajouter la connexion dans le graphe
        if depart not in graph:
            graph[depart] = {}
        if arrivee not in graph:
            graph[arrivee] = {}

        graph[depart][arrivee] = duree
        graph[arrivee][depart] = duree  # Connexion aller-retour

    return graph, city_to_station


def dijkstra(graph, start, goal):
    queue = []
    heapq.heappush(queue, (0, start, []))

    visited = set()

    while queue:
        current_distance, current_node, path = heapq.heappop(queue)

        if current_node in visited:
            continue

        path = path + [current_node]

        if current_node == goal:
            return current_distance, path

        visited.add(current_node)

        for neighbor, distance in graph[current_node].items():
            if neighbor not in visited:
                heapq.heappush(queue, (current_distance + distance, neighbor, path))

    return float("inf"), []
