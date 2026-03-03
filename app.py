from threading import Thread

from persistence.db import init_db
from utils import log
from ui.app_ui import start_ui
from core.engine import main_loop

def start_app():
    log("Starting AI Companion...")
    init_db()

    ui_thread = Thread(target=start_ui, daemon=True)
    ui_thread.start()

    main_loop()

    log("App exited cleanly.")

if __name__ == "__main__":
    start_app()
