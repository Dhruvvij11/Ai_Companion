import json
import os
import tempfile
import unittest

from core import config
from core import settings


class SettingsTests(unittest.TestCase):
    def setUp(self):
        self._old_settings_file = config.SETTINGS_FILE
        self.temp_dir = tempfile.TemporaryDirectory()
        config.SETTINGS_FILE = os.path.join(self.temp_dir.name, "settings.json")

    def tearDown(self):
        config.SETTINGS_FILE = self._old_settings_file
        self.temp_dir.cleanup()

    def test_load_defaults_when_missing(self):
        data = settings.load_settings()
        self.assertEqual(data["stt_language"], config.STT_LANGUAGE)
        self.assertEqual(data["tts_language"], config.TTS_LANGUAGE)
        self.assertEqual(data["tts_speed_multiplier"], config.DEFAULT_TTS_SPEED_MULTIPLIER)
        self.assertEqual(data["wake_phrases"], config.DEFAULT_WAKE_PHRASES)

    def test_load_sanitized_values(self):
        raw = {
            "stt_language": "HI",
            "tts_language": "EN",
            "tts_speed_multiplier": 9,
            "wake_phrases": ["  Hello Nova ", "", "ok nova"],
        }
        with open(config.SETTINGS_FILE, "w", encoding="utf-8") as file_obj:
            json.dump(raw, file_obj)

        data = settings.load_settings()
        self.assertEqual(data["stt_language"], "hi")
        self.assertEqual(data["tts_language"], "en")
        self.assertEqual(data["tts_speed_multiplier"], 2.0)
        self.assertEqual(data["wake_phrases"], ["hello nova", "ok nova"])


if __name__ == "__main__":
    unittest.main()
