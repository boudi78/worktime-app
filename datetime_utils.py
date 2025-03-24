from datetime import datetime

def parse_datetime_string(datetime_str):
    if not datetime_str:
        return None
    try:
        return datetime.fromisoformat(datetime_str)
    except ValueError:
        # Fallback für benutzerdefinierte Formate
        try:
            return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            return None