import threading
import time

from core import config


class ReminderScheduler:
    def __init__(self, repository, poll_interval=None):
        self.repository = repository
        self.poll_interval = poll_interval or config.REMINDER_POLL_INTERVAL
        self._running = False
        self._thread = None

    def tick(self, now_ts=None):
        now_ts = int(now_ts if now_ts is not None else time.time())
        due_reminders = self.repository.due(now_ts)

        triggered = []
        for reminder in due_reminders:
            if self.repository.mark_triggered(reminder["id"]):
                reminder["status"] = "done"
                reminder["triggered_at"] = now_ts
                triggered.append(reminder)
        return triggered

    def start(self, on_due):
        if self._running:
            return

        self._running = True

        def _run():
            while self._running:
                for reminder in self.tick():
                    on_due(reminder)
                time.sleep(self.poll_interval)

        self._thread = threading.Thread(target=_run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread:
            self._thread.join(timeout=2.0)
            self._thread = None
