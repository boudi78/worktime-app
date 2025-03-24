import os
import json
from datetime import datetime

# Custom JSON encoder to handle datetime objects
class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()  # Convert datetime to ISO format string
        return super().default(obj)

# Custom JSON decoder to handle datetime strings
def datetime_decoder(dict_):
    for key, value in dict_.items():
        if isinstance(value, str):
            try:
                # Only try to convert strings that look like ISO format
                if 'T' in value and '-' in value and ':' in value:
                    dict_[key] = datetime.fromisoformat(value)
            except (ValueError, TypeError):
                pass
    return dict_

def initialize_data_directory():
    """Initialisiert das Datenverzeichnis"""
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

def load_employees():
    """Lädt Mitarbeiterdaten aus einer JSON-Datei"""
    data_dir = "data"
    file_path = os.path.join(data_dir, "employees.json")
    
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                # First try with the custom decoder
                try:
                    return json.load(f, object_hook=datetime_decoder)
                except json.JSONDecodeError:
                    # If that fails, try without the custom decoder
                    f.seek(0)  # Reset file pointer to beginning
                    return json.load(f)
        except json.JSONDecodeError:
            # If the file is corrupted, return an empty list
            print("Error: employees.json file is corrupted. Creating a new empty file.")
            save_employees([])
            return []
    else:
        return []

def save_employees(employees):
    """Speichert Mitarbeiterdaten in einer JSON-Datei"""
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    file_path = os.path.join(data_dir, "employees.json")
    
    with open(file_path, "w") as f:
        # Use the custom encoder to handle datetime objects
        json.dump(employees, f, cls=DateTimeEncoder)

def load_time_entries():
    """Lädt Zeiteinträge aus einer JSON-Datei"""
    data_dir = "data"
    file_path = os.path.join(data_dir, "time_entries.json")
    
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                # First try with the custom decoder
                try:
                    return json.load(f, object_hook=datetime_decoder)
                except json.JSONDecodeError:
                    # If that fails, try without the custom decoder
                    f.seek(0)  # Reset file pointer to beginning
                    return json.load(f)
        except json.JSONDecodeError:
            # If the file is corrupted, return an empty list
            print("Error: time_entries.json file is corrupted. Creating a new empty file.")
            save_time_entries([])
            return []
    else:
        return []

def save_time_entries(time_entries):
    """Speichert Zeiteinträge in einer JSON-Datei mit Backup."""
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

    file_path = os.path.join(data_dir, "time_entries.json")
    timestamp = datetime.now().strftime("%Y-%m-%d_%H-%M-%S")
    backup_path = os.path.join(data_dir, f"time_entries_backup_{timestamp}.json")

    # ✅ Backup anlegen – nur wenn Datei bereits existiert
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as original, open(backup_path, "w", encoding="utf-8") as backup:
            backup.write(original.read())

    # ✅ Deine bestehende Speichermethode bleibt erhalten
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(time_entries, f, cls=DateTimeEncoder, indent=4)


def load_projects():
    """Lädt Projekte aus einer JSON-Datei"""
    data_dir = "data"
    file_path = os.path.join(data_dir, "projects.json")
    
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                # First try with the custom decoder
                try:
                    return json.load(f, object_hook=datetime_decoder)
                except json.JSONDecodeError:
                    # If that fails, try without the custom decoder
                    f.seek(0)  # Reset file pointer to beginning
                    return json.load(f)
        except json.JSONDecodeError:
            # If the file is corrupted, return default projects
            print("Error: projects.json file is corrupted. Creating a new default file.")
            default_projects = [
                {
                    "id": 1,
                    "name": "Projekt A",
                    "description": "Beschreibung für Projekt A",
                    "budget_hours": 100,
                    "used_hours": 0
                },
                {
                    "id": 2,
                    "name": "Projekt B",
                    "description": "Beschreibung für Projekt B",
                    "budget_hours": 50,
                    "used_hours": 0
                },
                {
                    "id": 3,
                    "name": "Internes",
                    "description": "Interne Tätigkeiten",
                    "budget_hours": 0,
                    "used_hours": 0
                }
            ]
            save_projects(default_projects)
            return default_projects
    else:
        # Beispielprojekte
        default_projects = [
            {
                "id": 1,
                "name": "Projekt A",
                "description": "Beschreibung für Projekt A",
                "budget_hours": 100,
                "used_hours": 0
            },
            {
                "id": 2,
                "name": "Projekt B",
                "description": "Beschreibung für Projekt B",
                "budget_hours": 50,
                "used_hours": 0
            },
            {
                "id": 3,
                "name": "Internes",
                "description": "Interne Tätigkeiten",
                "budget_hours": 0,
                "used_hours": 0
            }
        ]
        save_projects(default_projects)
        return default_projects

def save_projects(projects):
    """Speichert Projekte in einer JSON-Datei"""
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    file_path = os.path.join(data_dir, "projects.json")
    
    with open(file_path, "w") as f:
        # Use the custom encoder to handle datetime objects
        json.dump(projects, f, cls=DateTimeEncoder)

def load_teams():
    """Lädt Teams aus einer JSON-Datei"""
    data_dir = "data"
    file_path = os.path.join(data_dir, "teams.json")
    
    if os.path.exists(file_path):
        try:
            with open(file_path, "r") as f:
                # First try with the custom decoder
                try:
                    return json.load(f, object_hook=datetime_decoder)
                except json.JSONDecodeError:
                    # If that fails, try without the custom decoder
                    f.seek(0)  # Reset file pointer to beginning
                    return json.load(f)
        except json.JSONDecodeError:
            # If the file is corrupted, return default teams
            print("Error: teams.json file is corrupted. Creating a new default file.")
            default_teams = [
                {
                    "id": 1,
                    "name": "Team 1",
                    "location": "Werner-Siemens-Straße 107"
                },
                {
                    "id": 2,
                    "name": "Team 2",
                    "location": "Werner-Siemens-Straße 39"
                },
                {
                    "id": 3,
                    "name": "Team 3",
                    "location": "Werner-Siemens-Straße 39"
                },
                {
                    "id": 4,
                    "name": "Lager",
                    "location": "Werner-Siemens-Straße 107"
                }
            ]
            save_teams(default_teams)
            return default_teams
    else:
        # Standard-Teams mit Standorten
        default_teams = [
            {
                "id": 1,
                "name": "Team 1",
                "location": "Werner-Siemens-Straße 107"
            },
            {
                "id": 2,
                "name": "Team 2",
                "location": "Werner-Siemens-Straße 39"
            },
            {
                "id": 3,
                "name": "Team 3",
                "location": "Werner-Siemens-Straße 39"
            },
            {
                "id": 4,
                "name": "Lager",
                "location": "Werner-Siemens-Straße 107"
            }
        ]
        save_teams(default_teams)
        return default_teams

def save_teams(teams):
    """Speichert Teams in einer JSON-Datei"""
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    file_path = os.path.join(data_dir, "teams.json")
    
    with open(file_path, "w") as f:
        # Use the custom encoder to handle datetime objects
        json.dump(teams, f, cls=DateTimeEncoder)

def get_location_by_team(team_name):
    """Gibt den Standort basierend auf dem Teamnamen zurück"""
    teams = load_teams()
    for team in teams:
        if team["name"] == team_name:
            return team["location"]
    return None

def save_all_data(employees, time_entries=None, projects=None, teams=None):
    """Speichert alle Daten (Mitarbeiter, Zeiteinträge, Projekte, Teams)"""
    # Mitarbeiterdaten speichern
    save_employees(employees)
    
    # Zeiteinträge speichern, falls vorhanden
    if time_entries is not None:
        save_time_entries(time_entries)
    
    # Projekte speichern, falls vorhanden
    if projects is not None:
        save_projects(projects)
        
    # Teams speichern, falls vorhanden
    if teams is not None:
        save_teams(teams)
