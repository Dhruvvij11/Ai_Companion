import os
import tempfile
import unittest

from memory import long_term as long_memory


class LongMemoryTests(unittest.TestCase):
    def setUp(self):
        self._old_file = long_memory.MEMORY_FILE
        self.temp_dir = tempfile.TemporaryDirectory()
        long_memory.MEMORY_FILE = os.path.join(self.temp_dir.name, "long_memory.json")

    def tearDown(self):
        long_memory.MEMORY_FILE = self._old_file
        self.temp_dir.cleanup()

    def test_relevant_memory_prefers_overlap(self):
        long_memory.add_memory("Job", "I lost my job last month", "low")
        long_memory.add_memory("Travel", "I visited Tokyo and loved it", "positive")
        long_memory.add_memory("Meeting", "Project meeting moved to Friday", "neutral")

        items = long_memory.get_relevant_memories("I am stressed about my job", limit=2)
        self.assertGreaterEqual(len(items), 1)
        self.assertEqual(items[0]["title"], "Job")

    def test_recent_fallback_when_no_overlap(self):
        long_memory.add_memory("A", "First entry", "neutral")
        long_memory.add_memory("B", "Second entry", "neutral")

        items = long_memory.get_relevant_memories("zzz qqq yyy", limit=1)
        self.assertEqual(len(items), 1)
        self.assertEqual(items[0]["title"], "B")


if __name__ == "__main__":
    unittest.main()
