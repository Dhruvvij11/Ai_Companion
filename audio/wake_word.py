from core import config
from core.settings import get_setting
from audio.stt import listen


def _wake_phrases():
    phrases = get_setting("wake_phrases", config.DEFAULT_WAKE_PHRASES) or []
    return [str(phrase).lower().strip() for phrase in phrases if str(phrase).strip()]


def wait_for_wake_word():
    """
    Lightweight wake word detector.
    """
    text = listen(timeout=2)
    if not text:
        return False

    text = text.lower()
    phrases = _wake_phrases()
    return any(phrase in text for phrase in phrases)
