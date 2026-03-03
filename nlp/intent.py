import re


def _normalize(text: str) -> str:
    t = text.lower().strip()
    return re.sub(r"[^\w\s:]", "", t)


def extract_tts_language(text: str):
    t = _normalize(text)

    hindi_markers = [
        "speak in hindi",
        "talk in hindi",
        "hindi me",
        "hindi mein",
        "hindi main",
        "hindi bolo",
        "hindi me baat",
        "hindi mein baat",
    ]
    english_markers = [
        "speak in english",
        "talk in english",
        "english me",
        "english mein",
        "english main",
        "english bolo",
        "english me baat",
        "english mein baat",
    ]
    auto_markers = [
        "same language",
        "my language",
        "auto language",
        "whatever language i speak",
        "jis language me",
        "jisme main",
    ]

    if any(marker in t for marker in hindi_markers):
        return "hi"
    if any(marker in t for marker in english_markers):
        return "en"
    if any(marker in t for marker in auto_markers):
        return "auto"
    return None


def detect_intent(text: str) -> str:
    t = _normalize(text)

    reminder_action_words = ["yaad", "remind", "reminder"]
    reminder_context_words = [
        "meeting",
        "presentation",
        "deadline",
        "appointment",
        "alarm",
    ]
    reminder_time_words = [
        "kal",
        "aaj",
        "parso",
        "tomorrow",
        "today",
        "tonight",
        "morning",
        "afternoon",
        "evening",
        "night",
        "am",
        "pm",
        "baje",
    ]

    has_reminder_action = any(word in t for word in reminder_action_words)
    has_reminder_context = any(word in t for word in reminder_context_words)
    has_time_cue = any(word in t for word in reminder_time_words) or bool(
        re.search(r"\b([01]?\d|2[0-3]):([0-5]\d)\b", t)
    )

    if has_reminder_action or (has_reminder_context and has_time_cue):
        return "reminder"

    if extract_tts_language(t) is not None:
        return "language_change"

    if any(
        phrase in t
        for phrase in [
            "what time",
            "current time",
            "time",
            "clock",
        ]
    ):
        return "time"

    if any(
        word in t
        for word in [
            "weather",
            "temperature",
            "rain",
            "forecast",
        ]
    ):
        return "weather"

    if any(
        phrase in t
        for phrase in [
            "motivate me",
            "give me motivation",
            "inspire me",
            "encourage me",
        ]
    ):
        return "motivation"

    if any(
        phrase in t
        for phrase in [
            "why did she",
            "why did he",
            "why me",
            "why this happened",
        ]
    ):
        return "why_question"

    if any(
        phrase in t
        for phrase in [
            "breakup",
            "she left me",
            "he left me",
            "lost my job",
            "failed exam",
            "depressed",
        ]
    ):
        return "life_event"

    return "normal"
