from datetime import datetime


def try_fromisoformat(dt_str):
    try:
        return datetime.fromisoformat(dt_str)
    except:
        return None
