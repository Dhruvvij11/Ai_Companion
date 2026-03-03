import json
import os
import queue
import time

import sounddevice as sd
import vosk

from core import config
from core.settings import get_setting
from utils import log_debug

MODEL_PATHS = {
    "en": config.STT_MODEL_EN,
    "hi": config.STT_MODEL_HI,
}

_model_cache = {}
q = queue.Queue()


def callback(indata, frames, time, status):
    if status:
        return
    q.put(bytes(indata))


def _clear_audio_queue():
    while True:
        try:
            q.get_nowait()
        except queue.Empty:
            return


def _resolve_language(language=None):
    resolved = (language or get_setting("stt_language", config.STT_LANGUAGE) or "auto").lower()
    if resolved not in config.SUPPORTED_STT_LANGUAGES:
        return config.STT_LANGUAGE
    return resolved


def _get_model(lang: str):
    path = MODEL_PATHS.get(lang)
    if not path:
        raise ValueError(f"Unsupported STT language: {lang}")

    if not os.path.exists(path):
        raise FileNotFoundError(
            f"Missing Vosk model at {path}. "
            f"Download a '{lang}' model and place it there."
        )

    if lang not in _model_cache:
        load_start = time.perf_counter()
        _model_cache[lang] = vosk.Model(path)
        log_debug(
            "latency_stage",
            stage="stt_model_load",
            ms=round((time.perf_counter() - load_start) * 1000, 2),
            language=lang,
        )

    return _model_cache[lang]


def _transcribe(model, audio_chunks):
    if not audio_chunks:
        return ""

    rec = vosk.KaldiRecognizer(model, 16000)
    for data in audio_chunks:
        rec.AcceptWaveform(data)

    try:
        final = json.loads(rec.FinalResult())
    except json.JSONDecodeError:
        return ""

    return (final.get("text") or "").strip()


def listen(timeout=6, language=None):
    """
    Push-to-talk STT.
    Listens for `timeout` seconds.
    """
    total_start = time.perf_counter()
    language = _resolve_language(language)
    audio_chunks = []
    _clear_audio_queue()

    capture_start = time.perf_counter()
    try:
        with sd.RawInputStream(
            samplerate=16000,
            blocksize=8000,
            dtype="int16",
            channels=1,
            callback=callback,
        ):
            for _ in range(max(int(timeout * 2), 1)):
                try:
                    data = q.get(timeout=1.0)
                    audio_chunks.append(data)
                except queue.Empty:
                    continue
    except Exception:
        log_debug(
            "latency_stage",
            stage="stt_capture",
            ms=round((time.perf_counter() - capture_start) * 1000, 2),
            language=language,
            chunks=len(audio_chunks),
            status="error",
        )
        return ""
    log_debug(
        "latency_stage",
        stage="stt_capture",
        ms=round((time.perf_counter() - capture_start) * 1000, 2),
        language=language,
        chunks=len(audio_chunks),
        status="ok",
    )

    if not audio_chunks:
        log_debug(
            "latency_stage",
            stage="stt_total",
            ms=round((time.perf_counter() - total_start) * 1000, 2),
            language=language,
            status="no_audio",
        )
        return ""

    if language == "auto":
        candidates = []
        for lang in ("en", "hi"):
            decode_start = time.perf_counter()
            try:
                model = _get_model(lang)
                text = _transcribe(model, audio_chunks)
                candidates.append(text)
                log_debug(
                    "latency_stage",
                    stage="stt_decode",
                    ms=round((time.perf_counter() - decode_start) * 1000, 2),
                    language=lang,
                    text_chars=len(text),
                    status="ok",
                )
            except (FileNotFoundError, ValueError):
                log_debug(
                    "latency_stage",
                    stage="stt_decode",
                    ms=round((time.perf_counter() - decode_start) * 1000, 2),
                    language=lang,
                    status="model_missing",
                )
                continue

        if not candidates:
            log_debug(
                "latency_stage",
                stage="stt_total",
                ms=round((time.perf_counter() - total_start) * 1000, 2),
                language=language,
                status="no_candidates",
            )
            return ""

        result = max(candidates, key=len)
        log_debug(
            "latency_stage",
            stage="stt_total",
            ms=round((time.perf_counter() - total_start) * 1000, 2),
            language=language,
            text_chars=len(result),
            status="ok",
        )
        return result

    decode_start = time.perf_counter()
    try:
        model = _get_model(language)
    except (FileNotFoundError, ValueError):
        log_debug(
            "latency_stage",
            stage="stt_decode",
            ms=round((time.perf_counter() - decode_start) * 1000, 2),
            language=language,
            status="model_missing",
        )
        return ""
    result = _transcribe(model, audio_chunks)
    log_debug(
        "latency_stage",
        stage="stt_decode",
        ms=round((time.perf_counter() - decode_start) * 1000, 2),
        language=language,
        text_chars=len(result),
        status="ok",
    )
    log_debug(
        "latency_stage",
        stage="stt_total",
        ms=round((time.perf_counter() - total_start) * 1000, 2),
        language=language,
        text_chars=len(result),
        status="ok",
    )
    return result
