import time
import re

from core import config
from tools.commands import handle_reminder_command
from nlp.emotion import detect_text_emotion
from nlp.intent import detect_intent, extract_tts_language
from nlp.llm import generate_response
from memory.long_term import add_memory, get_relevant_memories
from memory.short_term import memory
from nlp.prompt import build_prompt
from reminders.repository import ReminderRepository
from reminders.scheduler import ReminderScheduler
from core.settings import get_setting, load_settings, save_settings
from audio.stt import listen
from core.state import state
from tools.router import route
from tools.time_tool import extract_time, handle_time
from tools.weather_tool import handle_weather
from audio.tts import speak
from utils import log, log_debug, sleep
from audio.wake_word import wait_for_wake_word

reminder_repository = ReminderRepository()
reminder_scheduler = ReminderScheduler(reminder_repository)


def _log_stage_timing(stage: str, start_perf: float, **fields):
    elapsed_ms = round((time.perf_counter() - start_perf) * 1000, 2)
    log_debug("latency_stage", stage=stage, ms=elapsed_ms, **fields)


def _listen_with_ui(timeout=6):
    stage_start = time.perf_counter()
    state.ui_state = "listening"
    try:
        return listen(timeout=timeout)
    finally:
        _log_stage_timing("stt_listen", stage_start, timeout_sec=timeout)
        state.ui_state = "idle"


def _wait_for_wake_word_with_ui():
    stage_start = time.perf_counter()
    state.ui_state = "listening"
    try:
        return wait_for_wake_word()
    finally:
        _log_stage_timing("wake_word_wait", stage_start, timeout_sec=2)
        state.ui_state = "idle"


def _infer_text_language(text: str) -> str:
    if re.search(r"[\u0900-\u097F]", text):
        return "hi"

    tokens = set(re.findall(r"[a-z]+", text.lower()))
    hindi_hints = {
        "hai",
        "kya",
        "kaise",
        "ka",
        "ki",
        "ke",
        "mujhe",
        "mera",
        "main",
        "mein",
        "nahi",
        "haan",
        "bolo",
        "baat",
    }
    if len(tokens.intersection(hindi_hints)) >= 2:
        return "hi"

    return "en"


def _response_language_for_text(user_text: str) -> str:
    preferred = str(get_setting("tts_language", config.TTS_LANGUAGE) or config.TTS_LANGUAGE).lower()
    if preferred in ("en", "hi"):
        return preferred
    return _infer_text_language(user_text)


def _set_tts_language(language: str):
    data = load_settings()
    data["tts_language"] = language
    save_settings(data)


def _speak_with_ui(response: str, emotion: str, language=None):
    state.ui_state = "speaking"
    stage_start = time.perf_counter()
    try:
        log("ai_response", text=response, emotion=emotion)
        speak(response, emotion, language=language)
        _log_stage_timing(
            "tts_speak",
            stage_start,
            response_chars=len(response or ""),
            language=language or "auto",
        )
    finally:
        state.ui_state = "idle"
        state.idle_time = 0


def _format_long_memory_context(user_text: str):
    memories = get_relevant_memories(
        user_text,
        limit=config.LONG_MEMORY_RETRIEVAL_LIMIT,
    )
    if not memories:
        return ""

    lines = []
    for item in memories:
        title = str(item.get("title", "Memory")).strip()
        summary = str(item.get("summary", "")).strip()
        emotion = str(item.get("emotion", "neutral")).strip()
        lines.append(f"- {title} ({emotion}): {summary}")

    return "Relevant long-term memories:\n" + "\n".join(lines)


def _build_memory_context(user_text: str):
    short_context = memory.get_context()
    long_context = _format_long_memory_context(user_text)
    parts = [part for part in [short_context, long_context] if part]
    return "\n\n".join(parts)


def main_loop():
    log("main_loop_started")
    log("input_mode_ready")
    last_reminder_poll = 0.0

    try:
        while state.running:
            user_input = get_user_input()

            if not user_input:
                log("waiting_wake_word")
                if _wait_for_wake_word_with_ui():
                    log("wake_word_detected")
                    user_input = _listen_with_ui()

            if not user_input:
                log("listening_fallback")
                user_input = _listen_with_ui()

            if user_input:
                handle_user_input(user_input)

            now = time.time()
            if now - last_reminder_poll >= config.REMINDER_POLL_INTERVAL:
                for reminder in reminder_scheduler.tick(now_ts=now):
                    log("reminder_triggered", text=reminder["text"], reminder_id=reminder["id"])
                    _speak_with_ui(f"Reminder: {reminder['text']}", state.current_emotion)
                last_reminder_poll = now

            state.idle_time += config.LOOP_DELAY
            sleep(config.LOOP_DELAY)

    except KeyboardInterrupt:
        log("keyboard_interrupt")
    finally:
        shutdown()


def get_user_input():
    try:
        return input("> ").strip()
    except EOFError:
        return None


def handle_user_input(text):
    turn_start = time.perf_counter()
    state.last_user_time = time.time()
    log("user_input", text=text)

    try:
        if (text or "").strip().startswith("/reminders"):
            command_start = time.perf_counter()
            handled, command_message = handle_reminder_command(text, reminder_repository)
            _log_stage_timing("command_parse", command_start, command="/reminders")
            if handled:
                _speak_with_ui(command_message, "neutral", _response_language_for_text(text))
                return

        emotion_start = time.perf_counter()
        emotion = detect_text_emotion(text)
        _log_stage_timing("emotion_detect", emotion_start)

        intent_start = time.perf_counter()
        intent = detect_intent(text)
        _log_stage_timing("intent_detect", intent_start, intent=intent)

        response_language = _response_language_for_text(text)

        state.current_emotion = emotion
        state.current_intent = intent

        if intent == "language_change":
            requested = extract_tts_language(text)
            if requested is None:
                _speak_with_ui("Please tell me to use English, Hindi, or auto mode.", emotion, response_language)
                return

            settings_start = time.perf_counter()
            _set_tts_language(requested)
            _log_stage_timing("settings_save_tts_language", settings_start, value=requested)
            if requested == "hi":
                _speak_with_ui("Theek hai, ab main Hindi mein baat karunga.", emotion, "hi")
                return
            if requested == "en":
                _speak_with_ui("Okay, I will speak in English.", emotion, "en")
                return

            _speak_with_ui("Okay, I will reply in the same language you use.", emotion, _infer_text_language(text))
            return

        if intent == "reminder":
            parse_start = time.perf_counter()
            reminder_time = extract_time(text)
            _log_stage_timing("reminder_time_parse", parse_start)
            if reminder_time is None:
                _speak_with_ui(
                    "Please tell me a reminder time, like tomorrow 5 PM.",
                    emotion,
                    response_language,
                )
                return

            create_start = time.perf_counter()
            reminder_id = reminder_repository.create(
                text=text,
                trigger_at=reminder_time,
            )
            _log_stage_timing("reminder_create", create_start)
            log("reminder_saved", reminder_id=reminder_id, at_timestamp=reminder_time)
            _speak_with_ui("Theek hai, yaad dila dunga.", emotion, response_language)
            return

        route_start = time.perf_counter()
        tool = route(intent)
        _log_stage_timing("tool_route", route_start, tool=tool or "none")
        if tool == "time":
            tool_start = time.perf_counter()
            response = handle_time()
            _log_stage_timing("tool_time", tool_start)
            _speak_with_ui(response, emotion, response_language)
            return

        if tool == "weather":
            tool_start = time.perf_counter()
            response = handle_weather(text)
            _log_stage_timing("tool_weather", tool_start)
            _speak_with_ui(response, emotion, response_language)
            return

        memory.add_user(text)

        if intent == "life_event":
            memory_save_start = time.perf_counter()
            add_memory(
                title="Personal life event",
                summary=text,
                emotion=emotion,
            )
            _log_stage_timing("long_memory_add", memory_save_start)

        context_start = time.perf_counter()
        memory_context = _build_memory_context(text)
        _log_stage_timing("memory_context_build", context_start, context_chars=len(memory_context))

        prompt_start = time.perf_counter()
        prompt = build_prompt(
            user_text=text,
            memory_context=memory_context,
            emotion=emotion,
            intent=intent,
        )
        _log_stage_timing("prompt_build", prompt_start, prompt_chars=len(prompt))

        state.ui_state = "thinking"
        llm_start = time.perf_counter()
        try:
            response = generate_response(prompt)
        finally:
            state.ui_state = "idle"
            _log_stage_timing("llm_generate", llm_start)

        llm_elapsed = time.perf_counter() - llm_start
        if llm_elapsed < 0.15:
            time.sleep(0.15 - llm_elapsed)

        memory.add_ai(response)
        _speak_with_ui(response, emotion, response_language)
        time.sleep(0.2)
    finally:
        _log_stage_timing("turn_total", turn_start, user_text_chars=len(text or ""))


def shutdown():
    state.running = False
    state.ui_state = "idle"
    log("shutdown")
