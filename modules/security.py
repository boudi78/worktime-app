# modules/security.py

def authenticate_user(username_or_email: str, password: str, employees: list):
    """
    Authentifiziert einen Benutzer anhand von Benutzername oder E-Mail und Passwort.
    
    :param username_or_email: Benutzername oder E-Mail
    :param password: Passwort im Klartext
    :param employees: Liste aller Mitarbeiter
    :return: Tuple (True, user_dict) bei Erfolg, sonst (False, Fehlermeldung)
    """
    for user in employees:
        if user.get("email") == username_or_email or user.get("name") == username_or_email:
            if user.get("password") == password:
                return True, user
            else:
                return False, "❌ Ungültiges Passwort."
    return False, "❌ Benutzer nicht gefunden."
