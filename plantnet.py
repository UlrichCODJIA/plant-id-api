import requests


class PlantNetAPI:
    def __init__(self, api_key, api_endpoint):
        self.api_key = api_key
        self.api_endpoint = api_endpoint

    def identify(self, files, data):
        response = requests.post(
            f"{self.api_endpoint}?include-related-images=false&no-reject=false&lang=fr&api-key={self.api_key}", files=files, data=data
        )
        response.raise_for_status()
        return response.json()
