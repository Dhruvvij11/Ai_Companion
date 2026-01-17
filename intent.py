def detect_intent(text: str) -> str:
    text = text.lower()

    if any(phrase in text for phrase in [
        "motivate me",
        "give me motivation",
        "inspire me",
        "encourage me"
    ]):
        return "motivation"

    if any(phrase in text for phrase in [
        "why did she",
        "why did he",
        "why me",
        "why this happened"
    ]):
        return "why_question"
    if any(phrase in text for phrase in [
    "breakup",
    "she left me",
    "he left me",
    "lost my job",
    "failed exam",
    "depressed",
    ]):
        return "life_event"


    return "normal"
