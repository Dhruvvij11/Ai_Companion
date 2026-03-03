import os
import tempfile
import unittest
from datetime import datetime

from tools.commands import handle_reminder_command
from reminders.repository import ReminderRepository


class ReminderCommandTests(unittest.TestCase):
    def setUp(self):
        self.temp_dir = tempfile.TemporaryDirectory()
        self.db_path = os.path.join(self.temp_dir.name, "assistant.db")
        self.repo = ReminderRepository(db_path=self.db_path)

    def tearDown(self):
        self.temp_dir.cleanup()

    def test_list_no_reminders(self):
        handled, message = handle_reminder_command("/reminders list", self.repo)
        self.assertTrue(handled)
        self.assertEqual(message, "No active reminders.")

    def test_list_multiple_reminders(self):
        first_id = self.repo.create("Call mom", trigger_at=1700000000)
        second_id = self.repo.create("Drink water", trigger_at=1700003600)

        handled, message = handle_reminder_command("/reminders list", self.repo)
        self.assertTrue(handled)

        expected_first = f"[{first_id}] {datetime.fromtimestamp(1700000000).isoformat()} — Call mom"
        expected_second = f"[{second_id}] {datetime.fromtimestamp(1700003600).isoformat()} — Drink water"
        self.assertEqual(message, "\n".join([expected_first, expected_second]))

    def test_cancel_valid_reminder(self):
        reminder_id = self.repo.create("Pay bills", trigger_at=1700007200)

        handled, message = handle_reminder_command(f"/reminders cancel {reminder_id}", self.repo)
        self.assertTrue(handled)
        self.assertEqual(message, f"Cancelled reminder {reminder_id}.")

        reminder = self.repo.get(reminder_id)
        self.assertEqual(reminder["status"], "cancelled")

    def test_cancel_non_existent_reminder(self):
        handled, message = handle_reminder_command("/reminders cancel r_missing", self.repo)
        self.assertTrue(handled)
        self.assertEqual(message, "Reminder not found or already inactive: r_missing")


if __name__ == "__main__":
    unittest.main()
