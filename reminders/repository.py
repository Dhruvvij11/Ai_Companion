import time
import uuid
from contextlib import closing

from persistence.db import get_connection, init_db


def _row_to_dict(row):
    if row is None:
        return None
    return {
        "id": row["id"],
        "text": row["text"],
        "trigger_at": row["trigger_at"],
        "recurrence": row["recurrence"],
        "status": row["status"],
        "triggered_at": row["triggered_at"],
        "created_at": row["created_at"],
        "updated_at": row["updated_at"],
    }


class ReminderRepository:
    def __init__(self, db_path=None):
        self.db_path = db_path
        init_db(self.db_path)

    def create(self, text: str, trigger_at: int, recurrence: str | None = None) -> str:
        now = int(time.time())
        reminder_id = f"r_{uuid.uuid4().hex}"
        with closing(get_connection(self.db_path)) as conn:
            conn.execute(
                """
                INSERT INTO reminders (
                    id, text, trigger_at, recurrence, status, triggered_at, created_at, updated_at
                )
                VALUES (?, ?, ?, ?, 'active', NULL, ?, ?)
                """,
                (reminder_id, text, int(trigger_at), recurrence, now, now),
            )
            conn.commit()
        return reminder_id

    def list_active(self):
        with closing(get_connection(self.db_path)) as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM reminders
                WHERE status = 'active'
                ORDER BY trigger_at ASC
                """
            ).fetchall()
        return [_row_to_dict(row) for row in rows]

    def due(self, now_ts: int):
        with closing(get_connection(self.db_path)) as conn:
            rows = conn.execute(
                """
                SELECT *
                FROM reminders
                WHERE status = 'active' AND trigger_at <= ?
                ORDER BY trigger_at ASC
                """,
                (int(now_ts),),
            ).fetchall()
        return [_row_to_dict(row) for row in rows]

    def mark_triggered(self, reminder_id: str) -> bool:
        now = int(time.time())
        with closing(get_connection(self.db_path)) as conn:
            result = conn.execute(
                """
                UPDATE reminders
                SET status = 'done', triggered_at = ?, updated_at = ?
                WHERE id = ? AND status = 'active'
                """,
                (now, now, reminder_id),
            )
            conn.commit()
        return result.rowcount > 0

    def cancel(self, reminder_id: str) -> bool:
        now = int(time.time())
        with closing(get_connection(self.db_path)) as conn:
            result = conn.execute(
                """
                UPDATE reminders
                SET status = 'cancelled', updated_at = ?
                WHERE id = ? AND status = 'active'
                """,
                (now, reminder_id),
            )
            conn.commit()
        return result.rowcount > 0

    def get(self, reminder_id: str):
        with closing(get_connection(self.db_path)) as conn:
            row = conn.execute(
                "SELECT * FROM reminders WHERE id = ?",
                (reminder_id,),
            ).fetchone()
        return _row_to_dict(row)
