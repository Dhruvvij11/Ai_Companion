import json
import logging
import os
import time
from logging.handlers import RotatingFileHandler

from core import config

_LOGGER = None


def _get_logger():
    global _LOGGER

    if _LOGGER is not None:
        return _LOGGER

    os.makedirs(config.LOG_DIR, exist_ok=True)

    logger = logging.getLogger("ai_companion")
    logger.setLevel(logging.DEBUG if config.DEBUG else logging.INFO)
    logger.propagate = False

    formatter = logging.Formatter("%(message)s")

    stream_handler = logging.StreamHandler()
    stream_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        config.LOG_FILE,
        maxBytes=config.LOG_MAX_BYTES,
        backupCount=config.LOG_BACKUP_COUNT,
        encoding="utf-8",
    )
    file_handler.setFormatter(formatter)

    logger.handlers.clear()
    logger.addHandler(stream_handler)
    logger.addHandler(file_handler)

    _LOGGER = logger
    return _LOGGER


def _emit(level_name: str, event: str, **fields):
    logger = _get_logger()
    level = getattr(logging, level_name, logging.INFO)

    payload = {
        "time": time.strftime("%Y-%m-%dT%H:%M:%S"),
        "level": level_name,
        "event": event,
    }
    if fields:
        payload.update(fields)

    logger.log(level, json.dumps(payload, ensure_ascii=False))


def log(message, **fields):
    _emit("INFO", str(message), **fields)


def log_debug(message, **fields):
    if config.DEBUG:
        _emit("DEBUG", str(message), **fields)


def sleep(seconds):
    time.sleep(seconds)
