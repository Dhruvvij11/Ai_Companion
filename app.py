from core import main_loop
from utils import log

def start_app():
    log("Starting AI Companion...")
    main_loop()
    log("App exited cleanly.")

if __name__ == "__main__":
    start_app()
