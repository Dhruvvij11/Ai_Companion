import unittest

from nlp.intent import detect_intent


class IntentTests(unittest.TestCase):
    def test_detects_time_intent(self):
        self.assertEqual(detect_intent("What time is it?"), "time")

    def test_detects_weather_intent(self):
        self.assertEqual(detect_intent("weather in tokyo"), "weather")

    def test_detects_reminder_intent(self):
        self.assertEqual(detect_intent("Remind me tomorrow at 5 pm"), "reminder")

    def test_reminder_takes_priority(self):
        self.assertEqual(
            detect_intent("Remind me tomorrow about weather in Delhi"),
            "reminder",
        )

    def test_time_plus_meeting_detects_reminder(self):
        self.assertEqual(detect_intent("meeting tomorrow at 4 pm"), "reminder")

    def test_detects_language_change_english(self):
        self.assertEqual(detect_intent("please speak in english"), "language_change")

    def test_detects_language_change_hindi(self):
        self.assertEqual(detect_intent("hindi mein baat karo"), "language_change")


if __name__ == "__main__":
    unittest.main()
