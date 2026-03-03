# AI Companion

A local, voice-enabled companion app with:
- Wake word detection
- Speech-to-text via Vosk
- Tool routing for time and weather
- Local LLM responses via Ollama
- Short-term + long-term memory
- Minimal floating UI state indicator

## Requirements

- Windows
- Python 3.10+
- A working microphone
- Ollama running locally (`http://localhost:11434`)
- Vosk English model at `models/vosk-en/vosk-model-small-en-us-0.15`
- Optional Hindi model at `models/vosk-hi/vosk-model-small-hi-0.22`
- Piper binary + English model under `piper/`
- Optional Hindi Piper TTS model at `piper/models/hi_IN-pratham-medium.onnx`

## Setup

1. Create and activate a virtual environment:
   - `python -m venv .venv`
   - `.venv\Scripts\activate`
2. Install dependencies:
   - `pip install -r requirements.txt`
3. Ensure Ollama is running and has model `llama3`:
   - `ollama pull llama3`
   - `ollama run llama3`
4. (Optional) Download Hindi Vosk model:
   - `powershell -ExecutionPolicy Bypass -File tools/download_vosk_hi.ps1`
5. (Optional) Create a local settings file:
   - `Copy-Item settings.example.json settings.json`

## Run

- `python app.py`

## Runtime Settings

`settings.json` supports lightweight runtime tuning without code changes:
- `stt_language`: `"en"`, `"hi"`, or `"auto"`
- `tts_language`: `"en"`, `"hi"`, or `"auto"` (`"auto"` replies in the user's language)
- `tts_speed_multiplier`: float between `0.5` and `2.0`
- `wake_phrases`: list of phrases checked by wake-word matching

If `settings.json` is missing or invalid, defaults from `config.py` are used.

## Logging

- Structured JSON logs are written to console and `logs/app.log`.
- File logs rotate automatically via `LOG_MAX_BYTES` and `LOG_BACKUP_COUNT`.
- Use `DEBUG` in `config.py` to control debug-level emission.

## Memory Behavior

- Short-term memory keeps recent turns and summarizes older evicted turns.
- Long-term memory retrieval is relevance + recency based before prompt build.
- Long-term entries are stored in `long_term_memory.json`.

## Troubleshooting

- `Missing Vosk model at ...`
  - Verify model directories match `config.py`.
- `sounddevice` input errors
  - Check microphone permissions and default input device in Windows settings.
- LLM fallback responses
  - Confirm Ollama is running on `localhost:11434` and `llama3` is available.
- Weather unavailable
  - Check internet connectivity; weather/geocoding use Open-Meteo APIs.
