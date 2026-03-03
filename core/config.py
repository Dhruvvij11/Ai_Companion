APP_NAME = "AI Companion"
DEBUG = True

LOOP_DELAY = 1.0  # seconds
REMINDER_POLL_INTERVAL = 1.0  # seconds

# Logging
LOG_DIR = "logs"
LOG_FILE = f"{LOG_DIR}/app.log"
LOG_MAX_BYTES = 1_000_000
LOG_BACKUP_COUNT = 5

# Speech-to-text settings
# Supported: "en", "hi", "auto"
SUPPORTED_STT_LANGUAGES = ("en", "hi", "auto")
STT_LANGUAGE = "auto"
STT_MODEL_EN = "models/vosk-en/vosk-model-small-en-us-0.15"
STT_MODEL_HI = "models/vosk-hi/vosk-model-small-hi-0.22"

# Text-to-speech settings
# Supported: "en", "hi", "auto"
SUPPORTED_TTS_LANGUAGES = ("en", "hi", "auto")
TTS_LANGUAGE = "auto"
TTS_MODEL_EN = "piper/models/en_US-lessac-medium.onnx"
TTS_MODEL_HI = "piper/models/hi_IN-pratham-medium.onnx"

# Runtime settings file
SETTINGS_FILE = "settings.json"
DEFAULT_WAKE_PHRASES = ["hey nova", "hello nova", "okay nova"]
DEFAULT_TTS_SPEED_MULTIPLIER = 1.0
DB_PATH = "data/assistant.db"

# Memory tuning
LONG_MEMORY_RETRIEVAL_LIMIT = 3
SHORT_MEMORY_SUMMARY_ITEMS = 8
SHORT_MEMORY_SUMMARY_CHARS = 120
