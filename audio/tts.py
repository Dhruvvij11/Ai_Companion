import os
import subprocess
import tempfile
import time
import winsound

from core import config
from core.settings import get_setting
from utils import log_debug

# Paths
PIPER_PATH = "piper/piper.exe"
MODEL_PATHS = {
    "en": config.TTS_MODEL_EN,
    "hi": config.TTS_MODEL_HI,
}


def _resolve_language(language=None) -> str:
    resolved = (language or get_setting("tts_language", config.TTS_LANGUAGE) or config.TTS_LANGUAGE).lower()
    if resolved not in config.SUPPORTED_TTS_LANGUAGES:
        return config.TTS_LANGUAGE
    return resolved


def _resolve_model_path(language=None) -> str:
    resolved = _resolve_language(language)
    if resolved == "auto":
        resolved = "en"

    preferred = MODEL_PATHS.get(resolved, config.TTS_MODEL_EN)
    if os.path.exists(preferred):
        return preferred

    return config.TTS_MODEL_EN


def _length_scale_for_emotion(emotion: str) -> float:
    length_scale = 1.0
    if emotion == "low":
        length_scale = 1.15
    elif emotion == "positive":
        length_scale = 0.9

    multiplier = get_setting("tts_speed_multiplier", config.DEFAULT_TTS_SPEED_MULTIPLIER)
    try:
        multiplier = float(multiplier)
    except (TypeError, ValueError):
        multiplier = config.DEFAULT_TTS_SPEED_MULTIPLIER

    multiplier = min(max(multiplier, 0.5), 2.0)
    return max(length_scale * multiplier, 0.2)


def speak(text: str, emotion: str = "neutral", language=None):
    """
    Silent, clean, stateless TTS using Piper.
    No media player popup.
    No leftover files.
    """
    if not text:
        return

    total_start = time.perf_counter()
    model_path = _resolve_model_path(language)
    if not os.path.exists(PIPER_PATH) or not os.path.exists(model_path):
        log_debug(
            "latency_stage",
            stage="tts_total",
            ms=round((time.perf_counter() - total_start) * 1000, 2),
            status="missing_binary_or_model",
            language=language or "auto",
        )
        return

    length_scale = _length_scale_for_emotion(emotion)

    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as temp_file:
        wav_path = temp_file.name

    cmd = [
        PIPER_PATH,
        "--model",
        model_path,
        "--output_file",
        wav_path,
        "--length_scale",
        str(length_scale),
    ]

    try:
        synth_start = time.perf_counter()
        process = subprocess.Popen(
            cmd,
            stdin=subprocess.PIPE,
            stdout=subprocess.DEVNULL,
            stderr=subprocess.DEVNULL,
            text=True,
        )
        process.communicate(input=text)
        log_debug(
            "latency_stage",
            stage="tts_synthesize",
            ms=round((time.perf_counter() - synth_start) * 1000, 2),
            language=language or "auto",
            model_path=model_path,
            chars=len(text),
            return_code=process.returncode,
        )

        if process.returncode != 0:
            return

        playback_start = time.perf_counter()
        winsound.PlaySound(wav_path, winsound.SND_FILENAME)
        log_debug(
            "latency_stage",
            stage="tts_playback",
            ms=round((time.perf_counter() - playback_start) * 1000, 2),
            language=language or "auto",
            chars=len(text),
        )
    finally:
        if os.path.exists(wav_path):
            os.remove(wav_path)
        log_debug(
            "latency_stage",
            stage="tts_total",
            ms=round((time.perf_counter() - total_start) * 1000, 2),
            language=language or "auto",
            chars=len(text),
        )
