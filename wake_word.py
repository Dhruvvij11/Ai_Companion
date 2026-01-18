from stt import listen

WAKE_PHRASES = [
    "hey nova",
    "hello nova",
    "okay nova"
]


def wait_for_wake_word():
    """
    Lightweight wake word detector.
    """
    text = listen(timeout=2)
    if not text:
        return False

    text = text.lower()
    return any(phrase in text for phrase in WAKE_PHRASES)
