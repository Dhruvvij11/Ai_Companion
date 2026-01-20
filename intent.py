import re

def detect_intent(text: str) -> str:
    t = text.lower().strip()
    t = re.sub(r"[^\w\s]", "", t)  # remove punctuation

    # ---------- TOOL INTENTS (HIGHEST PRIORITY) ----------
    if any(word in t for word in [
        "time",
        "what time",
        "current time",
        "clock"
    ]):
        return "time"

    if any(word in t for word in [
        "weather",
        "temperature",
        "rain",
        "forecast"
    ]):
        return "weather"

    # ---------- EMOTIONAL / CONVERSATIONAL INTENTS ----------
    if any(phrase in t for phrase in [
        "motivate me",
        "give me motivation",
        "inspire me",
        "encourage me"
    ]):
        return "motivation"

    if any(phrase in t for phrase in [
        "why did she",
        "why did he",
        "why me",
        "why this happened"
    ]):
        return "why_question"

    if any(phrase in t for phrase in [
        "breakup",
        "she left me",
        "he left me",
        "lost my job",
        "failed exam",
        "depressed"
    ]):
        return "life_event"

    return "normal"
