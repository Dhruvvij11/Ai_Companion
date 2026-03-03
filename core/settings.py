import json
import os

from core import config


def _default_settings():
    return {
        "stt_language": config.STT_LANGUAGE,
        "tts_language": config.TTS_LANGUAGE,
        "tts_speed_multiplier": config.DEFAULT_TTS_SPEED_MULTIPLIER,
        "wake_phrases": list(config.DEFAULT_WAKE_PHRASES),
    }


def _sanitize(raw):
    defaults = _default_settings()
    data = dict(defaults)

    if not isinstance(raw, dict):
        return data

    stt_language = str(raw.get("stt_language", defaults["stt_language"])).lower()
    if stt_language in config.SUPPORTED_STT_LANGUAGES:
        data["stt_language"] = stt_language

    tts_language = str(raw.get("tts_language", defaults["tts_language"])).lower()
    if tts_language in config.SUPPORTED_TTS_LANGUAGES:
        data["tts_language"] = tts_language

    try:
        speed = float(raw.get("tts_speed_multiplier", defaults["tts_speed_multiplier"]))
        data["tts_speed_multiplier"] = min(max(speed, 0.5), 2.0)
    except (TypeError, ValueError):
        pass

    wake_phrases = raw.get("wake_phrases")
    if isinstance(wake_phrases, list):
        cleaned = [
            str(phrase).strip().lower()
            for phrase in wake_phrases
            if str(phrase).strip()
        ]
        if cleaned:
            data["wake_phrases"] = cleaned

    return data


def load_settings():
    if not os.path.exists(config.SETTINGS_FILE):
        return _default_settings()

    try:
        with open(config.SETTINGS_FILE, "r", encoding="utf-8") as file_obj:
            raw = json.load(file_obj)
    except (OSError, ValueError):
        return _default_settings()

    return _sanitize(raw)


def save_settings(data):
    normalized = _sanitize(data)
    with open(config.SETTINGS_FILE, "w", encoding="utf-8") as file_obj:
        json.dump(normalized, file_obj, indent=2, ensure_ascii=False)


def get_setting(key, default=None):
    settings = load_settings()
    if default is None:
        default = _default_settings().get(key)
    return settings.get(key, default)
