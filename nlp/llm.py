import time

import requests
from utils import log_debug

OLLAMA_URL = "http://localhost:11434/api/generate"
MODEL_NAME = "llama3:8b"


def _ns_to_ms(value):
    if value is None:
        return None
    try:
        return round(float(value) / 1_000_000.0, 2)
    except (TypeError, ValueError):
        return None


def generate_response(prompt: str) -> str:
    payload = {
        "model": MODEL_NAME,
        "prompt": prompt,
        "stream": False,
    }

    request_start = time.perf_counter()
    try:
        response = requests.post(OLLAMA_URL, json=payload, timeout=60)
        response.raise_for_status()
        data = response.json()
    except requests.RequestException:
        elapsed_ms = round((time.perf_counter() - request_start) * 1000, 2)
        log_debug(
            "latency_stage",
            stage="llm_http",
            ms=elapsed_ms,
            status="request_error",
            model=MODEL_NAME,
            prompt_chars=len(prompt or ""),
        )
        return "I am having trouble reaching the local model right now."
    except ValueError:
        elapsed_ms = round((time.perf_counter() - request_start) * 1000, 2)
        log_debug(
            "latency_stage",
            stage="llm_http",
            ms=elapsed_ms,
            status="json_error",
            model=MODEL_NAME,
            prompt_chars=len(prompt or ""),
        )
        return "I got an invalid response from the local model."

    elapsed_ms = round((time.perf_counter() - request_start) * 1000, 2)
    text = (data.get("response") or "").strip()
    log_debug(
        "latency_stage",
        stage="llm_http",
        ms=elapsed_ms,
        status_code=response.status_code,
        model=MODEL_NAME,
        prompt_chars=len(prompt or ""),
        response_chars=len(text),
        ollama_total_ms=_ns_to_ms(data.get("total_duration")),
        ollama_load_ms=_ns_to_ms(data.get("load_duration")),
        ollama_prompt_eval_ms=_ns_to_ms(data.get("prompt_eval_duration")),
        ollama_eval_ms=_ns_to_ms(data.get("eval_duration")),
        ollama_prompt_eval_count=data.get("prompt_eval_count"),
        ollama_eval_count=data.get("eval_count"),
    )
    if not text:
        return "I could not generate a response right now."

    return text
