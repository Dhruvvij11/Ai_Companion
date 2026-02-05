from threading import Thread
from utils import log
from ui import start_ui
from core import main_loop
from behaviour import idle_message


def start_app():
    log("Starting AI Companion...")

    # Start UI in background
    ui_thread = Thread(target=start_ui, daemon=True)
    ui_thread.start()

    # Start core loop
    main_loop()

    log("App exited cleanly.")


if __name__ == "__main__":
    start_app()
emotion = "neutral"   # abhi ke liye hardcode
msg = idle_message(emotion)
tts.speak(msg)