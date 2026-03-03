import unittest

from tools.location_extractor import extract_location


class LocationExtractorTests(unittest.TestCase):
    def test_extracts_city_after_in(self):
        self.assertEqual(extract_location("weather in paris"), "paris")

    def test_extracts_city_after_of(self):
        self.assertEqual(extract_location("weather of mumbai"), "mumbai")

    def test_handles_question_format(self):
        self.assertEqual(extract_location("what's the weather in tokyo?"), "tokyo")

    def test_returns_none_when_missing_city(self):
        self.assertIsNone(extract_location("tell me the weather"))


if __name__ == "__main__":
    unittest.main()
