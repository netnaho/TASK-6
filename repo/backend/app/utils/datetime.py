from datetime import UTC, datetime, timedelta


def utc_now() -> datetime:
    return datetime.now(UTC)


def add_minutes(minutes: int) -> datetime:
    return utc_now() + timedelta(minutes=minutes)


def add_hours(hours: int) -> datetime:
    return utc_now() + timedelta(hours=hours)


def add_days(days: int) -> datetime:
    return utc_now() + timedelta(days=days)
