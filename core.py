from state import state
from utils import log, sleep
from config import LOOP_DELAY
from llm import generate_response
from prompt import build_prompt
from memory import memory
from emotion import detect_text_emotion
from tts import speak
from intent import detect_intent
from long_memory import add_memory
from stt import listen
from wake_word import wait_for_wake_word
from state import state
import time
from tool_router import route
from tools.time_tool import handle_time
from tools.weather_tool import handle_weather







def main_loop():
    log("Main loop started")
    log("Type something and press Enter (Ctrl+C to exit)")

    try:
        while state.running:
            user_input = get_user_input()

            if not user_input:
                log("🟡 Say wake word...")
            if wait_for_wake_word():
                log("🟢 Wake word detected. Listening...")
                user_input = listen()


            if not user_input:
                log("🎤 Listening...")
                user_input = listen()


            if user_input:
                handle_user_input(user_input)

            state.idle_time += LOOP_DELAY
            sleep(LOOP_DELAY)

    except KeyboardInterrupt:
        log("Keyboard interrupt received")

    finally:
        shutdown()


def get_user_input():
    try:
        return input("> ").strip()
    except EOFError:
        return None


def handle_user_input(text):
    # ----- Understanding layer -----
    emotion = detect_text_emotion(text)
    intent = detect_intent(text)

    state.current_emotion = emotion
    state.current_intent = intent

    tool = route(intent)

    # ----- TOOL ROUTING -----
    if tool == "time":
        state.ui_state = "speaking"
        response = handle_time()
        log(f"AI: {response}")
        speak(response, emotion)
        state.ui_state = "idle"
        state.idle_time = 0
        return
    if tool == "weather":
        state.ui_state = "speaking"
        response = handle_weather(text)
        log(f"AI: {response}")
        speak(response, emotion)
        state.ui_state = "idle"
        state.idle_time = 0
        return


    # ----- MEMORY (INPUT) -----
    memory.add_user(text)
    memory_context = memory.get_context()

    if intent == "life_event":
        add_memory(
            title="Personal life event",
            summary=text,
            emotion=emotion
        )

    # ----- PROMPT -----
    prompt = build_prompt(
        user_text=text,
        memory_context=memory_context,
        emotion=emotion,
        intent=intent
    )

    # ----- THINKING -----
    state.ui_state = "thinking"

    start = time.time()
    response = generate_response(prompt)
    elapsed = time.time() - start

    if elapsed < 0.15:
        time.sleep(0.15 - elapsed)

    # ----- MEMORY (OUTPUT) -----
    memory.add_ai(response)

    # ----- SPEAKING -----
    state.ui_state = "speaking"
    log(f"AI: {response}")
    speak(response, emotion)

    time.sleep(0.2)

    state.ui_state = "idle"
    state.idle_time = 0


def shutdown():
    state.running = False
    log("Shutting down AI Companion gracefully...")
