import requests

class WeatherAPI:
    def fetch_weather(self, city_name: str, api_key: str):
        url = f"https://api.openweathermap.org/data/2.5/weather?q={city_name}&appid={api_key}"
        response = requests.get(url)
        response.raise_for_status()
        return response.json()
