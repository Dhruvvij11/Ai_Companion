def detect_text_emotion(text: str) -> str:
    text = text.lower()

    low_energy_keywords = [
        "tired", "exhausted", "drained", "burnt out",
        "sad", "down", "low", "stressed", "anxious"
    ]

    positive_keywords = [
        "happy", "good", "great", "excited", "relieved",
        "better", "awesome", "nice"
    ]

    frustrated_keywords = [
        "annoyed", "frustrated", "irritated",
        "angry", "fed up"
    ]

    for word in low_energy_keywords:
        if word in text:
            return "low"

    for word in frustrated_keywords:
        if word in text:
            return "frustrated"

    for word in positive_keywords:
        if word in text:
            return "positive"

    return "neutral"
