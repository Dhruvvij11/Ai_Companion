import re
from datetime import datetime, timedelta


def handle_time():
    now = datetime.now().astimezone()
    zone = now.strftime("%Z")
    return f"It's {now.strftime('%I:%M %p').lstrip('0')} {zone}."


def _day_offset_from_text(text: str) -> int:
    lowered = text.lower()

    if "day after tomorrow" in lowered or "parso" in lowered:
        return 2
    if "tomorrow" in lowered or "kal" in lowered:
        return 1
    if "today" in lowered or "aaj" in lowered:
        return 0

    return 0


def _default_time_from_text(text: str):
    lowered = text.lower()

    if any(word in lowered for word in ("morning", "subah")):
        return 9, 0
    if any(word in lowered for word in ("afternoon", "dopahar")):
        return 15, 0
    if any(word in lowered for word in ("evening", "shaam")):
        return 19, 0
    if any(word in lowered for word in ("night", "raat", "tonight")):
        return 21, 0

    return None


def _normalize_hour(hour: int, meridiem: str | None) -> int:
    if meridiem is None:
        return hour

    if meridiem == "am":
        return 0 if hour == 12 else hour

    if meridiem == "pm":
        return 12 if hour == 12 else hour + 12

    return hour


def _parse_explicit_time(text: str):
    lowered = text.lower()

    am_pm = re.search(r"\b(\d{1,2})(?::(\d{2}))?\s*(am|pm)\b", lowered)
    if am_pm:
        hour = int(am_pm.group(1))
        minute = int(am_pm.group(2) or 0)
        meridiem = am_pm.group(3)
        if not (1 <= hour <= 12 and 0 <= minute <= 59):
            return None
        return _normalize_hour(hour, meridiem), minute

    baje = re.search(r"\b(\d{1,2})(?::(\d{2}))?\s*baje\b", lowered)
    if baje:
        hour = int(baje.group(1))
        minute = int(baje.group(2) or 0)
        if not (0 <= hour <= 23 and 0 <= minute <= 59):
            return None
        return hour, minute

    hhmm = re.search(r"\b([01]?\d|2[0-3]):([0-5]\d)\b", lowered)
    if hhmm:
        return int(hhmm.group(1)), int(hhmm.group(2))

    standalone = re.search(r"\b(\d{1,2})\b", lowered)
    if standalone:
        hour = int(standalone.group(1))
        if 0 <= hour <= 23:
            return hour, 0

    return None


def extract_time(text, reference_time=None):
    now = reference_time or datetime.now()
    day_offset = _day_offset_from_text(text)
    target_date = now + timedelta(days=day_offset)

    explicit_time = _parse_explicit_time(text)
    if explicit_time:
        hour, minute = explicit_time
    else:
        default_time = _default_time_from_text(text)
        if not default_time:
            return None
        hour, minute = default_time

    target = target_date.replace(hour=hour, minute=minute, second=0, microsecond=0)

    if day_offset == 0 and target <= now:
        target += timedelta(days=1)

    return int(target.timestamp())
