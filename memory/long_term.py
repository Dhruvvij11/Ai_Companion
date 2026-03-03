import json
import os
import re
from datetime import datetime

MEMORY_FILE = "long_term_memory.json"


def _load():
    if not os.path.exists(MEMORY_FILE):
        return []

    try:
        with open(MEMORY_FILE, "r", encoding="utf-8") as file_obj:
            data = json.load(file_obj)
    except (OSError, ValueError):
        return []

    if not isinstance(data, list):
        return []

    return data


def _save(data):
    with open(MEMORY_FILE, "w", encoding="utf-8") as file_obj:
        json.dump(data, file_obj, indent=2, ensure_ascii=False)


def add_memory(title: str, summary: str, emotion: str):
    memory = _load()
    memory.append(
        {
            "time": datetime.now().isoformat(),
            "title": title,
            "summary": summary,
            "emotion": emotion,
        }
    )
    _save(memory)


def get_recent_memories(limit=3):
    memory = _load()
    return memory[-limit:]


def _tokenize(text: str):
    return [word for word in re.findall(r"[a-zA-Z0-9]+", text.lower()) if len(word) > 2]


def get_relevant_memories(query: str, limit=3):
    memories = _load()
    if not memories:
        return []

    query_tokens = set(_tokenize(query))
    scored = []
    total = len(memories)

    for index, item in enumerate(memories):
        blob = " ".join(
            [
                str(item.get("title", "")),
                str(item.get("summary", "")),
                str(item.get("emotion", "")),
            ]
        )
        item_tokens = set(_tokenize(blob))
        overlap = len(query_tokens & item_tokens)
        recency = (index + 1) / total
        score = overlap * 3 + recency
        scored.append((score, item))

    scored.sort(key=lambda pair: pair[0], reverse=True)
    selected = [item for score, item in scored if score > 0][:limit]
    if selected:
        return selected

    return get_recent_memories(limit=limit)
