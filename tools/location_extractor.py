import re

def extract_location(text: str) -> str | None:
    """
    Extract city name from phrases like:
    - weather in paris
    - weather of mumbai
    - what's the weather in tokyo
    """
    text = text.lower()

    match = re.search(r"(?:in|of)\s+([a-zA-Z\s]+)", text)
    if match:
        city = match.group(1).strip()
        return city

    return None
