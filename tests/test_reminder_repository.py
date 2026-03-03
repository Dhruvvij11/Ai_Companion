import os
import tempfile
import unittest

from reminders.repository import ReminderRepository


class ReminderRepositoryTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "assistant.db")
        self.repo = ReminderRepository(db_path=self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_create_and_get(self):
        reminder_id = self.repo.create("Call mom", trigger_at=2000)
        reminder = self.repo.get(reminder_id)

        self.assertIsNotNone(reminder)
        self.assertEqual(reminder["id"], reminder_id)
        self.assertEqual(reminder["text"], "Call mom")
        self.assertEqual(reminder["trigger_at"], 2000)
        self.assertEqual(reminder["status"], "active")

    def test_due_filters_by_time(self):
        due_id = self.repo.create("Due", trigger_at=1000)
        self.repo.create("Later", trigger_at=5000)

        due = self.repo.due(1200)
        due_ids = [item["id"] for item in due]

        self.assertEqual(due_ids, [due_id])

    def test_mark_triggered_removes_from_active(self):
        reminder_id = self.repo.create("Task", trigger_at=1000)
        self.assertTrue(self.repo.mark_triggered(reminder_id))

        active_ids = [item["id"] for item in self.repo.list_active()]
        self.assertNotIn(reminder_id, active_ids)

        reminder = self.repo.get(reminder_id)
        self.assertEqual(reminder["status"], "done")
        self.assertIsNotNone(reminder["triggered_at"])

    def test_cancel(self):
        reminder_id = self.repo.create("Cancel me", trigger_at=1000)
        self.assertTrue(self.repo.cancel(reminder_id))

        reminder = self.repo.get(reminder_id)
        self.assertEqual(reminder["status"], "cancelled")


if __name__ == "__main__":
    unittest.main()
