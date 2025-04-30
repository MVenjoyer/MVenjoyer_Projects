from datetime import datetime
from zoneinfo import ZoneInfo

DEFAULT_TZ_NAME = "Europe/Moscow"


def now() -> datetime:
    return datetime.now(tz=ZoneInfo(key=DEFAULT_TZ_NAME))


def strftime(dt: datetime, fmt: str) -> str:
    """Return dt converted to string according to format in default timezone"""
    if not dt.tzinfo:
        dt = dt.replace(tzinfo=ZoneInfo(key=DEFAULT_TZ_NAME))
    else:
        dt = dt.astimezone(tz=ZoneInfo(key=DEFAULT_TZ_NAME))
    return dt.strftime(fmt)


def strptime(dt_str: str, fmt: str) -> datetime:
    """Return dt parsed from string according to format in default timezone"""
    ans = datetime.strptime(dt_str, fmt)
    if not ans.tzinfo:
        ans = ans.replace(tzinfo=ZoneInfo(key=DEFAULT_TZ_NAME))
    else:
        ans = ans.astimezone(tz=ZoneInfo(key=DEFAULT_TZ_NAME))
    return ans


def diff(first_dt: datetime, second_dt: datetime) -> int:
    """Return seconds between two datetimes rounded down to closest int"""
    first_dt = first_dt if first_dt.tzinfo else first_dt.replace(tzinfo=ZoneInfo(DEFAULT_TZ_NAME))
    second_dt = second_dt if second_dt.tzinfo else second_dt.replace(tzinfo=ZoneInfo(DEFAULT_TZ_NAME))
    return int((second_dt - first_dt).total_seconds())


def timestamp(dt: datetime) -> int:
    """Return timestamp for given datetime rounded down to closest int"""
    dt = dt if dt.tzinfo else dt.replace(tzinfo=ZoneInfo(DEFAULT_TZ_NAME))
    return int(dt.timestamp())


def from_timestamp(ts: float) -> datetime:
    """Return datetime from given timestamp"""
    return datetime.fromtimestamp(ts, tz=ZoneInfo(key=DEFAULT_TZ_NAME))
