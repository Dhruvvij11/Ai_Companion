import requests
from tools.location_extractor import extract_location
from tools.geocoding import geocode_city

def handle_weather(user_text: str):
    city = extract_location(user_text)

    if not city:
        return "Tell me the city name to check the weather."

    location = geocode_city(city)

    if not location:
        return f"I couldn’t find weather data for {city}."

    lat = location["lat"]
    lon = location["lon"]
    city_name = location["name"]

    url = (
        "https://api.open-meteo.com/v1/forecast"
        f"?latitude={lat}&longitude={lon}"
        "&current_weather=true"
    )

    try:
        data = requests.get(url, timeout=5).json()
        weather = data["current_weather"]

        temp = weather["temperature"]
        wind = weather["windspeed"]

        return f"It’s {temp}°C right now in {city_name}, with wind around {wind} km/h."

    except Exception:
        return "I couldn’t fetch the weather right now."
