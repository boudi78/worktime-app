from datetime import datetime

def parse_datetime_string(date_string):
    """
    Parst einen Datetime-String in verschiedenen Formaten.
    """
    if not date_string:
        return None
    
    try:
        # Versuche ISO-Format zu parsen
        return datetime.fromisoformat(date_string)
    except ValueError:
        try:
            # Versuche altes Format zu parsen
            return datetime.strptime(date_string, "%Y-%m-%d %H:%M:%S")
        except ValueError:
            try:
                # Versuche Datumsformat ohne Zeit
                return datetime.strptime(date_string, "%Y-%m-%d")
            except ValueError:
                return None
