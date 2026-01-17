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





def main_loop():
    log("Main loop started")
    log("Type something and press Enter (Ctrl+C to exit)")

    try:
        while state.running:
            user_input = get_user_input()

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

    emotion = detect_text_emotion(text)
    state.current_emotion = emotion

    memory.add_user(text)
    memory_context = memory.get_context()
    intent = detect_intent(text)
    state.current_intent = intent

    prompt = build_prompt(
        user_text=text,
        memory_context=memory_context,
        emotion=emotion,
        intent=intent
    )
    if intent == "life_event":
        add_memory(
        title="Personal life event",
        summary=text,
        emotion=emotion
    )


    response = generate_response(prompt)

    memory.add_ai(response)
    log(f"AI: {response}")

    speak(response,emotion)   # 🔊 emotion-aware voice


def shutdown():
    state.running = False
    log("Shutting down AI Companion gracefully...")
