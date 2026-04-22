import requests
from tools.base import BaseTool

class WeatherTool(BaseTool):
    name = "weather"
    description = "Get current weather for a city. Input: city name as string."

    def run(self, city: str) -> str:
        try:
            url = f"https://wttr.in/{city}?format=3"
            response = requests.get(url, timeout=5)
            response.raise_for_status()
            return response.text.strip()
        except Exception as e:
            return f"Weather error: {str(e)}"