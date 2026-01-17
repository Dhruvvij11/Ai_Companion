import subprocess
import tempfile
import os
import winsound

# Paths
PIPER_PATH = "piper/piper.exe"
MODEL_PATH = "piper/models/en_US-lessac-medium.onnx"


def speak(text: str, emotion: str = "neutral"):
    """
    Silent, clean, stateless TTS using Piper.
    No media player popup.
    No leftover files.
    """

    # Emotion → speed mapping
    length_scale = 1.0
    if emotion == "low":
        length_scale = 1.15   # slower
    elif emotion == "positive":
        length_scale = 0.9    # faster
    elif emotion == "frustrated":
        length_scale = 1.0

    # Create temp wav file
    with tempfile.NamedTemporaryFile(delete=False, suffix=".wav") as f:
        wav_path = f.name

    # Piper command
    cmd = [
        PIPER_PATH,
        "--model", MODEL_PATH,
        "--output_file", wav_path,
        "--length_scale", str(length_scale)
    ]

    # Run Piper
    process = subprocess.Popen(
        cmd,
        stdin=subprocess.PIPE,
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
        text=True
    )

    process.stdin.write(text)
    process.stdin.close()
    process.wait()

    # 🔊 Play sound silently (no UI)
    winsound.PlaySound(wav_path, winsound.SND_FILENAME)

    # 🧹 Cleanup
    os.remove(wav_path)
