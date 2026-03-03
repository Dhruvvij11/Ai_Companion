import unittest
from datetime import datetime

from tools.time_tool import extract_time


class TimeToolTests(unittest.TestCase):
    def test_tomorrow_with_ampm(self):
        now = datetime(2026, 2, 11, 10, 0, 0)
        ts = extract_time("remind me tomorrow at 5 pm", reference_time=now)
        target = datetime.fromtimestamp(ts)
        self.assertEqual(target, datetime(2026, 2, 12, 17, 0, 0))

    def test_hindi_morning_default_time(self):
        now = datetime(2026, 2, 11, 10, 0, 0)
        ts = extract_time("kal subah yaad dilana", reference_time=now)
        target = datetime.fromtimestamp(ts)
        self.assertEqual(target, datetime(2026, 2, 12, 9, 0, 0))

    def test_day_after_tomorrow_hhmm(self):
        now = datetime(2026, 2, 11, 10, 0, 0)
        ts = extract_time("parso 07:30 reminder", reference_time=now)
        target = datetime.fromtimestamp(ts)
        self.assertEqual(target, datetime(2026, 2, 13, 7, 30, 0))

    def test_past_same_day_rolls_to_next_day(self):
        now = datetime(2026, 2, 11, 10, 0, 0)
        ts = extract_time("remind me at 9", reference_time=now)
        target = datetime.fromtimestamp(ts)
        self.assertEqual(target, datetime(2026, 2, 12, 9, 0, 0))

    def test_returns_none_when_no_time_signal(self):
        now = datetime(2026, 2, 11, 10, 0, 0)
        self.assertIsNone(extract_time("remind me sometime", reference_time=now))


if __name__ == "__main__":
    unittest.main()
