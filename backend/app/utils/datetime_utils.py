from datetime import datetime, timedelta, timezone

RANGE_WINDOWS = {"day": timedelta(days=1), "week": timedelta(weeks=1), "month": timedelta(days=30)}


def utcnow() -> datetime:
    return datetime.now(timezone.utc)


def range_start(range_key: str) -> datetime:
    window = RANGE_WINDOWS.get(range_key)
    if window is None:
        raise ValueError(f"Unknown range '{range_key}', expected one of {list(RANGE_WINDOWS)}")
    return utcnow() - window
