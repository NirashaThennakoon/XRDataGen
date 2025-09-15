from datetime import datetime, timezone
from zoneinfo import ZoneInfo

def local_now(tz_name: str) -> datetime:
    return datetime.now(ZoneInfo(tz_name))

def to_utc_iso(dt) -> str:
    # ensure aware UTC and Z suffix
    return dt.astimezone(timezone.utc).isoformat().replace("+00:00", "Z")
