import requests


def geocode_city(city: str):
    try:
        url = (
            "https://geocoding-api.open-meteo.com/v1/search"
            f"?name={city}&count=1"
        )
        response = requests.get(url, timeout=5)
        response.raise_for_status()
        data = response.json()
    except (requests.RequestException, ValueError):
        return None

    results = data.get("results") or []
    if not results:
        return None

    result = results[0]
    name = result.get("name")
    lat = result.get("latitude")
    lon = result.get("longitude")

    if name is None or lat is None or lon is None:
        return None

    return {
        "name": name,
        "lat": lat,
        "lon": lon,
    }
