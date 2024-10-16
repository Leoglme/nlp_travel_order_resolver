import pandas as pd
from rapidfuzz import process

# Chargement des fichiers CSV
stops_df = pd.read_csv('assets/data_sncf/stops.txt')
stop_times_df = pd.read_csv('assets/data_sncf/stop_times.txt')
trips_df = pd.read_csv('assets/data_sncf/trips.txt')
routes_df = pd.read_csv('assets/data_sncf/routes.txt')

# Ajout des logs pour le suivi
print("[INFO] Fichiers CSV chargés.")


def find_closest_station(city_name, stops_df):
    """Utilisation du fuzzy matching pour trouver l'arrêt le plus proche"""
    stop_names = stops_df['stop_name'].values
    print(f"[INFO] Recherche de la gare la plus proche pour {city_name}.")
    closest_match = process.extractOne(f"Gare de {city_name}", stop_names)
    if closest_match:
        print(f"[INFO] Gare trouvée : {closest_match[0]}")
        return stops_df[stops_df['stop_name'] == closest_match[0]]
    print(f"[WARN] Aucun arrêt trouvé pour {city_name}.")
    return None


def find_trip_between_stations(departure_stop_id, arrival_stop_id, stop_times_df):
    """Cherche tous les trajets qui passent par l'arrêt de départ et l'arrêt d'arrivée"""
    print(f"[INFO] Recherche des trajets entre les arrêts {departure_stop_id} et {arrival_stop_id}.")

    # Filtre pour les départs et arrivées
    departure_times = stop_times_df[stop_times_df['stop_id'] == departure_stop_id]
    arrival_times = stop_times_df[stop_times_df['stop_id'] == arrival_stop_id]

    print(f"[INFO] Nombre de départs trouvés: {len(departure_times)}")
    print(f"[INFO] Nombre d'arrivées trouvées: {len(arrival_times)}")

    # Merge sur 'trip_id' pour trouver les trajets en commun
    common_trips = pd.merge(departure_times, arrival_times, on='trip_id')
    print(f"[INFO] Nombre de trajets communs trouvés : {len(common_trips)}")

    # Filtrer les trajets où l'arrêt de départ est avant l'arrêt d'arrivée
    valid_trips = common_trips[common_trips['stop_sequence_x'] < common_trips['stop_sequence_y']]
    print(f"[INFO] Nombre de trajets valides (départ avant arrivée) : {len(valid_trips)}")

    return valid_trips


def display_trip_details(trips_df, valid_trips):
    """Affiche les détails des trajets trouvés"""
    if valid_trips.empty:
        print("[WARN] Aucun trajet direct trouvé entre ces deux gares.")
    else:
        print("[INFO] Trajets possibles :")
        for index, trip in valid_trips.iterrows():
            trip_id = trip['trip_id']
            route = trips_df[trips_df['trip_id'] == trip_id]['route_id'].values[0]
            print(f" - Trajet ID: {trip_id} avec la route {route}")


# Recherche des gares de départ et d'arrivée avec la méthode `find_closest_station`
departure_stop = find_closest_station('Rennes', stops_df)
arrival_stop = find_closest_station('Nantes', stops_df)

# Vérification si les gares ont été trouvées
if departure_stop is not None and not departure_stop.empty:
    print(
        f"[INFO] Gare de départ : {departure_stop['stop_name'].values[0]} (ID: {departure_stop['stop_id'].values[0]})")
else:
    print("[ERROR] Gare de départ non trouvée.")
    exit(1)

if arrival_stop is not None and not arrival_stop.empty:
    print(f"[INFO] Gare d'arrivée : {arrival_stop['stop_name'].values[0]} (ID: {arrival_stop['stop_id'].values[0]})")
else:
    print("[ERROR] Gare d'arrivée non trouvée.")
    exit(1)

# Recherche des trajets entre les gares
trips_between = find_trip_between_stations(
    departure_stop['stop_id'].iloc[0],
    arrival_stop['stop_id'].iloc[0],
    stop_times_df
)

# Affichage des trajets disponibles
display_trip_details(trips_df, trips_between)