import requests

class CityManager:
    def __init__(self, api_url="https://geo.api.gouv.fr/communes"):
        self.api_url = api_url

    def fetch_cities(self, limit=100000):
        """
        Récupère les villes via l'API Géo du gouvernement français.
        """
        params = {
            "fields": "nom",
            "format": "json",
            "geometry": "centre",
            "limit": limit
        }
        response = requests.get(self.api_url, params=params)

        if response.status_code == 200:
            return response.json()  # On récupère le JSON brut
        else:
            print(f"Erreur : Impossible de récupérer les villes (code {response.status_code})")
            return []

    @staticmethod
    def get_cities_names(cities):
        """
        Formate les données des villes pour une utilisation ultérieure (par exemple, uniquement le nom des villes).
        """
        formatted_cities = [city["nom"] for city in cities]
        return formatted_cities