import requests

"""
CityManager is a service that allows you to retrieve cities from the French government's Geo API.
"""


class CityManager:
    def __init__(self, api_url="https://geo.api.gouv.fr/communes"):
        self.api_url = api_url

    """
    Retrieves cities via the French government's Geo API.
    """

    def fetch_cities(self, limit=100000):
        params = {
            "fields": "nom",
            "format": "json",
            "geometry": "centre",
            "limit": limit
        }
        response = requests.get(self.api_url, params=params)

        if response.status_code == 200:
            return response.json()
        else:
            print(f"Error: Unable to retrieve cities (code {response.status_code})")
            return []

    """
    Formats city data for later use (for example, only city names).
    """

    @staticmethod
    def get_cities_names(cities):
        return [city["nom"] for city in cities]
