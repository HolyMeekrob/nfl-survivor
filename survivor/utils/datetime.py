from datetime import datetime, timezone


def try_fromisoformat(dt_str):
    try:
        return datetime.fromisoformat(dt_str)
    except:
        return None


def utcnow():
    return datetime.now(timezone.utc)
