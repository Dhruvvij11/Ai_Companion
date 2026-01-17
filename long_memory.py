import json
import os
from datetime import datetime

MEMORY_FILE = "long_term_memory.json"


def _load():
    if not os.path.exists(MEMORY_FILE):
        return []
    with open(MEMORY_FILE, "r", encoding="utf-8") as f:
        return json.load(f)


def _save(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def add_memory(title: str, summary: str, emotion: str):
    memory = _load()

    memory.append({
        "time": datetime.now().isoformat(),
        "title": title,
        "summary": summary,
        "emotion": emotion
    })

    _save(memory)


def get_recent_memories(limit=3):
    memory = _load()
    return memory[-limit:]
