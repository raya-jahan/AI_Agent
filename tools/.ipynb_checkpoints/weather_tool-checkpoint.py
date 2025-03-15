from typing import Any, Optional
from smolagents.tools import Tool
import requests

class FreeWeatherTool(Tool):
    name = "current_weather_free"
    description = "Retrieves the current weather information for a specified location using the free Open-Meteo API and Nominatim geocoding."
    inputs = {
        'location': {
            'type': 'string',
            'description': 'The location (e.g., city name) for which to get the current weather.'
        }
    }
    output_type = "string"

    def forward(self, location: str) -> str:
        # First, use Nominatim to geocode the location (no API key needed)
        try:
            geocode_url = f"https://nominatim.openstreetmap.org/search?q={location}&format=json&limit=1"
            headers = {"User-Agent": "Mozilla/5.0"}
            geocode_response = requests.get(geocode_url, headers=headers, timeout=10)
            geocode_response.raise_for_status()
            geocode_data = geocode_response.json()
            if not geocode_data:
                return f"Location '{location}' not found."
            lat = geocode_data[0]['lat']
            lon = geocode_data[0]['lon']
        except Exception as e:
            return f"Error during geocoding: {str(e)}"

        # Next, call Open-Meteo to get current weather data
        try:
            weather_url = f"https://api.open-meteo.com/v1/forecast?latitude={lat}&longitude={lon}&current_weather=true"
            weather_response = requests.get(weather_url, timeout=10)
            weather_response.raise_for_status()
            weather_data = weather_response.json()
            current_weather = weather_data.get("current_weather", {})
            if not current_weather:
                return f"Could not retrieve current weather data for {location}."
            temperature = current_weather.get("temperature")
            windspeed = current_weather.get("windspeed")
            weather_code = current_weather.get("weathercode")
            return (f"Current weather in {location}:\n"
                    f"Temperature: {temperature}°C\n"
                    f"Windspeed: {windspeed} km/h\n"
                    f"Weather Code: {weather_code}")
        except Exception as e:
            return f"Error retrieving weather data: {str(e)}"