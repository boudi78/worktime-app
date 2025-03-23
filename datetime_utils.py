from datetime import datetime

def parse_datetime_string(datetime_str):
    """
    Parse a datetime string in either ISO format or custom format.
    
    This function handles both the new ISO format (with 'T') and the old
    custom format ('%Y-%m-%d %H:%M:%S') for backward compatibility.
    
    Args:
        datetime_str (str): The datetime string to parse
        
    Returns:
        datetime: The parsed datetime object, or None if parsing fails
    """
    if not datetime_str:
        return None
    
    # Try to parse as ISO format first (new format)
    if 'T' in datetime_str:
        try:
            return datetime.fromisoformat(datetime_str)
        except ValueError:
            pass
    
    # Try to parse as custom format (old format)
    try:
        return datetime.strptime(datetime_str, "%Y-%m-%d %H:%M:%S")
    except ValueError:
        pass
    
    # If all parsing attempts fail, return None
    return None
