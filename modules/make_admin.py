# make_admin.py

from utils.db_utils import get_db_session
from modules.models import User

def make_myself_admin(username):
    with get_db_session() as session:
        # Finde den Benutzer mit dem angegebenen Benutzernamen
        user = session.query(User).filter_by(username=username).first()
        if user:
            # Ändere die Rolle zu "Admin"
            user.role = "Admin"
            session.commit()
            print(f"Erfolgreich! {username} ist jetzt ein Admin.")
        else:
            print(f"Fehler: Kein Benutzer mit dem Namen {username} gefunden.")

if __name__ == "__main__":
    # Ändere hier den Benutzernamen zu deinem eigenen!
    make_myself_admin("boudi78")
