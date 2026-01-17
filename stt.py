import json
import queue
import sounddevice as sd
import vosk

MODEL_PATH = "models/vosk-en/vosk-model-small-en-us-0.15"

model = vosk.Model(MODEL_PATH)
rec = vosk.KaldiRecognizer(model, 16000)

q = queue.Queue()


def callback(indata, frames, time, status):
    q.put(bytes(indata))


def listen(timeout=6):
    """
    Push-to-talk STT.
    Listens for `timeout` seconds.
    """
    with sd.RawInputStream(
        samplerate=16000,
        blocksize=8000,
        dtype="int16",
        channels=1,
        callback=callback
    ):
        for _ in range(int(timeout * 2)):
            data = q.get()
            if rec.AcceptWaveform(data):
                result = json.loads(rec.Result())
                text = result.get("text", "")
                if text:
                    return text

    final = json.loads(rec.FinalResult())
    return final.get("text", "")
