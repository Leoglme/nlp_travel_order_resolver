from services.sncf.sncf_route_finder import SNCFRouteFinder

route_finder = SNCFRouteFinder()

departure_city = "Rennes"
destination_city = "Lyon"

# Find the shortest route
route_data = route_finder.find_shortest_route(departure_city, destination_city)

# Check if a route was found and view the results
if "error" in route_data:
    print(route_data["error"])
else:
    print(route_data)