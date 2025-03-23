from datetime import datetime

def ensure_datetime(dt_value):
    """
    Stellt sicher, dass der Wert ein datetime-Objekt ist.
    Konvertiert Strings in datetime-Objekte, gibt datetime-Objekte unverändert zurück.
    """
    if isinstance(dt_value, datetime):
        return dt_value
    elif isinstance(dt_value, str):
        try:
            # Versuche ISO-Format zu parsen
            return datetime.fromisoformat(dt_value)
        except ValueError:
            try:
                # Versuche altes Format zu parsen
                return datetime.strptime(dt_value, "%Y-%m-%d %H:%M:%S")
            except ValueError:
                # Wenn beide Formate fehlschlagen, gib None zurück
                return None
    return None
