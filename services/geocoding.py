import requests

class GeocodingService:
    def __init__(self):
        self.base_url = "https://nominatim.openstreetmap.org"
    
    def get_address(self, lat, lng):
        params = {
            'format': 'json',
            'lat': lat,
            'lon': lng,
            'zoom': 18,
            'addressdetails': 1
        }
        headers = {'User-Agent': 'LineLedger/1.0'}
        
        response = requests.get(f"{self.base_url}/reverse", params=params, headers=headers)
        if response.status_code == 200:
            data = response.json()
            return data.get('display_name', '')
        return ''
    
    def search_location(self, query):
        params = {
            'format': 'json',
            'q': query,
            'limit': 5,
            'countrycodes': 'tw'
        }
        headers = {'User-Agent': 'LineLedger/1.0'}
        
        response = requests.get(f"{self.base_url}/search", params=params, headers=headers)
        if response.status_code == 200:
            return response.json()
        return []
