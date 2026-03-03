from datetime import datetime

from utils import log

REMINDER_HELP_TEXT = (
    "Reminder commands:\n"
    "/reminders list\n"
    "/reminders cancel <id>\n"
    "/reminders help"
)


def handle_reminder_command(text: str, repository):
    """
    Handle exact `/reminders` terminal commands.

    Supported commands:
    - /reminders list
    - /reminders cancel <id>
    - /reminders help

    Returns:
        tuple[bool, str]: (handled, message)
        - handled is True when input starts with `/reminders`.
        - message is the command result or help/error text.
    """
    raw = (text or "").strip()
    if not raw.startswith("/reminders"):
        return False, ""

    log("reminder_command_received", text=raw)

    if raw == "/reminders help":
        return True, REMINDER_HELP_TEXT

    if raw == "/reminders list":
        try:
            reminders = repository.list_active()
        except Exception:
            log("reminder_command_error", command="list")
            return True, "Could not list reminders right now."

        if not reminders:
            return True, "No active reminders."

        lines = []
        for reminder in reminders:
            trigger_iso = datetime.fromtimestamp(int(reminder["trigger_at"])).isoformat()
            lines.append(f"[{reminder['id']}] {trigger_iso} — {reminder['text']}")
        return True, "\n".join(lines)

    parts = raw.split()
    if len(parts) == 3 and parts[1] == "cancel":
        reminder_id = parts[2]
        try:
            cancelled = repository.cancel(reminder_id)
        except Exception:
            log("reminder_command_error", command="cancel", reminder_id=reminder_id)
            return True, "Could not cancel the reminder right now."

        if cancelled:
            return True, f"Cancelled reminder {reminder_id}."
        return True, f"Reminder not found or already inactive: {reminder_id}"

    return True, f"Unknown reminder command.\n{REMINDER_HELP_TEXT}"
