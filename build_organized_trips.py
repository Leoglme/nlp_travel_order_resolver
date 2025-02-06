import csv
import aiohttp
from geopy.geocoders import Nominatim
from tqdm import tqdm
import nest_asyncio
import asyncio

# Apply the nest_asyncio patch to allow nested event loops
nest_asyncio.apply()

# Initialize geolocator
geolocator = Nominatim(user_agent="geoapiExercises")


# Function to get city name from coordinates asynchronously
async def get_city_name(session, lat, lon, city_cache):
    if (lat, lon) in city_cache:
        return city_cache[(lat, lon)]
    async with session.get(
            f"https://nominatim.openstreetmap.org/reverse?format=json&lat={lat}&lon={lon}&zoom=10") as response:
        data = await response.json()
        address = data.get('address', {})
        city = address.get('city', '') or address.get('town', '') or address.get('village', '')
        city_cache[(lat, lon)] = city
        return city


# Function to calculate trip duration from stop times
def calculate_trip_duration(start_time, end_time):
    start_hours, start_minutes, start_seconds = map(int, start_time.split(':'))
    end_hours, end_minutes, end_seconds = map(int, end_time.split(':'))
    duration_seconds = (end_hours * 3600 + end_minutes * 60 + end_seconds) - (
            start_hours * 3600 + start_minutes * 60 + start_seconds)
    duration_minutes = duration_seconds // 60
    return str(duration_minutes)


# Load stops data (only valid StopPoints)
stops = {}
with open('assets/data_sncf/stops.txt', 'r', encoding='utf-8') as file:
    reader = csv.DictReader(file)
    for row in reader:
        if row['location_type'] == '0':  # We only care about StopPoints
            stops[row['stop_id']] = {
                'stop_name': row['stop_name'],
                'stop_lat': row['stop_lat'],
                'stop_lon': row['stop_lon'],
                'parent_station': row['parent_station']
            }


# Function to dynamically find stop IDs for all cities
def find_all_stop_ids():
    stop_ids = []
    for stop_id, stop_data in stops.items():
        stop_ids.append(stop_id)
    return stop_ids


# Main function
async def main():
    target_stop_ids = find_all_stop_ids()

    # Load stop times data
    stop_times = {}
    with open('assets/data_sncf/stop_times.txt', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            trip_id = row['trip_id']
            if trip_id not in stop_times:
                stop_times[trip_id] = []
            stop_times[trip_id].append({
                'stop_id': row['stop_id'],
                'arrival_time': row['arrival_time'],
                'departure_time': row['departure_time']
            })

    # Load trips data
    trips = {}
    with open('assets/data_sncf/trips.txt', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            trips[row['trip_id']] = {
                'route_id': row['route_id'],
                'trip_headsign': row['trip_headsign']
            }

    # Load routes data
    routes = {}
    with open('assets/data_sncf/routes.txt', 'r', encoding='utf-8') as file:
        reader = csv.DictReader(file)
        for row in reader:
            routes[row['route_id']] = {
                'route_short_name': row['route_short_name'],
                'route_long_name': row['route_long_name']
            }

    # Dynamically find all trips that include the target cities
    def find_trips_involving_cities():
        trips_involving_cities = []
        for trip_id, stops_list in stop_times.items():
            for stop in stops_list:
                if stop['stop_id'] in target_stop_ids:
                    trips_involving_cities.append(trip_id)
                    break  # Exit loop after finding the first occurrence of any city in the trip
        return trips_involving_cities

    # Get the list of trips involving the target cities
    trip_ids = find_trips_involving_cities()

    city_cache = {}

    async with aiohttp.ClientSession() as session:
        with open('assets/data_sncf/organized_trips_2.csv', 'w', newline='', encoding='utf-8') as file:
            writer = csv.writer(file)
            writer.writerow(['departure_city', 'arrival_city', 'departure_station', 'arrival_station',
                             'travel_time', 'departure_coordinates', 'arrival_coordinates'])

            # Set to track unique trip segments
            unique_trips = set()

            # Process each trip that involves the target cities
            for trip_id in tqdm(trip_ids, desc="Processing trips involving target cities"):
                if trip_id in stop_times:
                    stops_list = stop_times[trip_id]

                    # Find the target cities in the stops list
                    city_index = None
                    for i, stop in enumerate(stops_list):
                        if stop['stop_id'] in target_stop_ids:
                            city_index = i
                            print(f"Target city found in trip {trip_id} at index {i}")
                            break

                    if city_index is not None:
                        # Process all segments in the trip, including before and after the target cities
                        for j in range(1, len(stops_list)):  # Iterate through all stops in the trip
                            prev_stop = stops_list[j - 1]
                            current_stop = stops_list[j]
                            departure_stop = stops.get(prev_stop['stop_id'])
                            arrival_stop = stops.get(current_stop['stop_id'])

                            if departure_stop and arrival_stop:
                                departure_city = await get_city_name(session, departure_stop['stop_lat'],
                                                                     departure_stop['stop_lon'], city_cache)
                                arrival_city = await get_city_name(session, arrival_stop['stop_lat'],
                                                                   arrival_stop['stop_lon'], city_cache)
                                travel_time = calculate_trip_duration(prev_stop['departure_time'],
                                                                      current_stop['arrival_time'])

                                # Create a tuple to represent the trip segment
                                trip_segment = (
                                    departure_city,  # departure_city
                                    arrival_city,  # arrival_city
                                    departure_stop['stop_name'],  # departure_station
                                    arrival_stop['stop_name'],  # arrival_station
                                )

                                # Check if this trip segment already exists
                                if trip_segment not in unique_trips:
                                    # Add the trip segment to the set
                                    unique_trips.add(trip_segment)

                                    # Write the trip segment to the CSV file
                                    writer.writerow([
                                        departure_city,  # departure_city
                                        arrival_city,  # arrival_city
                                        departure_stop['stop_name'],  # departure_station
                                        arrival_stop['stop_name'],  # arrival_station
                                        travel_time,  # travel_time
                                        f"{departure_stop['stop_lat']},{departure_stop['stop_lon']}",
                                        # departure_coordinates
                                        f"{arrival_stop['stop_lat']},{arrival_stop['stop_lon']}"  # arrival_coordinates
                                    ])


# Run the main function
asyncio.run(main())
print("Le fichier organized_trips_2.csv a été créé avec succès.")
