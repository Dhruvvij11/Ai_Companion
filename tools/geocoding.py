import requests

def geocode_city(city: str):
    try:
        url = (
            "https://geocoding-api.open-meteo.com/v1/search"
            f"?name={city}&count=1"
        )
        data = requests.get(url, timeout=5).json()

        if "results" not in data:
            return None

        result = data["results"][0]
        return {
            "name": result["name"],
            "lat": result["latitude"],
            "lon": result["longitude"]
        }

    except Exception:
        return None
