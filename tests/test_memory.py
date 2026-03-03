import unittest

from memory.short_term import MAX_TURNS, ShortTermMemory


class MemoryTests(unittest.TestCase):
    def test_empty_context(self):
        mem = ShortTermMemory()
        self.assertEqual(mem.get_context(), "")

    def test_context_order_and_format(self):
        mem = ShortTermMemory()
        mem.add_user("hello")
        mem.add_ai("hi")
        mem.add_user("how are you")

        context = mem.get_context()
        self.assertIn("Recent turns:", context)
        self.assertIn("User: hello", context)
        self.assertIn("AI: hi", context)
        self.assertIn("User: how are you", context)

    def test_max_turn_window_and_summary(self):
        mem = ShortTermMemory()
        total_turns = MAX_TURNS + 2

        for index in range(total_turns):
            mem.add_user(f"u{index}")
            mem.add_ai(f"a{index}")

        self.assertEqual(len(mem.buffer), MAX_TURNS * 2)
        self.assertGreater(len(mem.summary), 0)

        recent_context = " ".join(item["content"] for item in mem.buffer)
        self.assertNotIn("u0", recent_context)
        self.assertNotIn("a0", recent_context)
        self.assertIn(f"u{total_turns - 1}", recent_context)
        self.assertIn(f"a{total_turns - 1}", recent_context)


if __name__ == "__main__":
    unittest.main()
