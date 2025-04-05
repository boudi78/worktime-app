# modules/data_loader.py
import json
import os
import bcrypt  # Zum Hashen der Passwörter

DATA_FOLDER = "data"
EMPLOYEE_FILE = os.path.join(DATA_FOLDER, "employees.json")

# Funktion zum Hashen des Passworts
def hash_password(password: str) -> str:
    salt = bcrypt.gensalt()
    hashed = bcrypt.hashpw(password.encode('utf-8'), salt)
    return hashed.decode('utf-8')  # Rückgabe als String

# Funktion zur Überprüfung des Passworts
def check_password(stored_hash: str, password: str) -> bool:
    return bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8'))

def load_employees():
    """Lädt die Mitarbeiterdaten aus der JSON-Datei."""
    if os.path.exists(EMPLOYEE_FILE):
        try:
            with open(EMPLOYEE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Could not decode JSON from {EMPLOYEE_FILE}. Returning an empty list.")
            return []
    else:
        print(f"Warning: Employee file not found at {EMPLOYEE_FILE}. Returning an empty list.")
        return []

def save_employees(employees):
    """Speichert die Mitarbeiterdaten in der JSON-Datei."""
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
    with open(EMPLOYEE_FILE, "w", encoding="utf-8") as f:
        json.dump(employees, f, indent=4, ensure_ascii=False)

def load_employees_with_hashed_passwords():
    """Lädt Mitarbeiterdaten und stellt sicher, dass Passwörter gehasht sind."""
    employees = load_employees()
    passwords_changed = False
    for emp in employees:
        if "password" in emp and not emp["password"].startswith("$2b$"):  # Grundlegende Prüfung auf bcrypt-Hash
            emp["password"] = hash_password(emp["password"])
            passwords_changed = True
    if passwords_changed:
        save_employees(employees)
    return employees

# Optional: Funktion zum Finden eines Mitarbeiters anhand des Benutzernamens (nützlich für Login)
def get_employee_by_username(username):
    employees = load_employees_with_hashed_passwords()
    return next((emp for emp in employees if emp.get("username") == username), None)

# Optional: Funktion zum Finden eines Mitarbeiters anhand der ID
def get_employee_by_id(employee_id):
    employees = load_employees()
    return next((emp for emp in employees if emp.get("id") == employee_id), None)
