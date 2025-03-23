from datetime import datetime

def parse_datetime_string(datetime_str):
    """
    Wandelt einen Datums-/Zeitstring in ein datetime-Objekt um.
    Unterstützt sowohl ISO-Format als auch benutzerdefiniertes Format.
    """
    if not datetime_str:
        return None
    
    # ISO Format (z. B. 2025-03-23T14:00:00)
    if 'T' in datetime_str:
        try:
            return datetime.fromisoformat(datetime_str)
        except ValueError:
            pass

    # Alternatives Format
    try:
        return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        pass

    return None
