def route(intent: str) -> str:
    if intent == "time":
        return "time"
    if intent == "weather":
        return "weather"
    if intent == "reminder":
        return "reminder"
    return "llm"
