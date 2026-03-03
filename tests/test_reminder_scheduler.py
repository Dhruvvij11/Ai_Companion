import os
import tempfile
import unittest

from reminders.repository import ReminderRepository
from reminders.scheduler import ReminderScheduler


class ReminderSchedulerTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "assistant.db")
        self.repo = ReminderRepository(db_path=self.db_path)
        self.scheduler = ReminderScheduler(self.repo, poll_interval=0.01)

    def tearDown(self):
        self.scheduler.stop()
        self.temp_dir.cleanup()

    def test_tick_triggers_due_once(self):
        due_id = self.repo.create("Due now", trigger_at=1000)
        self.repo.create("Later", trigger_at=5000)

        first = self.scheduler.tick(now_ts=1200)
        second = self.scheduler.tick(now_ts=1200)

        self.assertEqual(len(first), 1)
        self.assertEqual(first[0]["id"], due_id)
        self.assertEqual(len(second), 0)

    def test_tick_marks_status_done(self):
        due_id = self.repo.create("Hydrate", trigger_at=1000)

        self.scheduler.tick(now_ts=1000)
        reminder = self.repo.get(due_id)

        self.assertEqual(reminder["status"], "done")
        self.assertIsNotNone(reminder["triggered_at"])


if __name__ == "__main__":
    unittest.main()
