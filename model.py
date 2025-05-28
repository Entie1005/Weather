from api import WeatherAPI
from ai import get_clothing_advice
import requests

class WeatherModel:
    def __init__(self):
        self.api = WeatherAPI()
        self.api_key = "869a845d6eb8ccf49238eb23c944b321Màn hình"

    def get_weather_data(self, city_name):
        try:
            data = self.api.fetch_weather(city_name, self.api_key)
            if data["cod"] == 200:
                return data
            else:
                raise ValueError("Invalid response code")
        except requests.exceptions.RequestException as e:
            raise e

    def analyze_weather(self, data):
        temp_in_k = data["main"]["temp"]
        temp_in_c = temp_in_k - 273.15
        weather_id = data["weather"][0]["id"]
        weather_description = data["weather"][0]["description"]
        wind_speed = data["wind"]["speed"] * 3.6  # m/s → km/h
        humidity = data["main"]["humidity"]
        advice = get_clothing_advice(temp_in_c, wind_speed, humidity, weather_id)

        return {
            "temp_c": temp_in_c,
            "weather_id": weather_id,
            "description": weather_description,
            "wind_speed": wind_speed,
            "humidity": humidity,
            "advice": advice
        }
