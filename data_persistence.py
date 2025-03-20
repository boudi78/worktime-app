import os
import json
from datetime import datetime

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
        with open(file_path, "r") as f:
            return json.load(f)
    else:
        return []

def save_employees(employees):
    """Speichert Mitarbeiterdaten in einer JSON-Datei"""
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    file_path = os.path.join(data_dir, "employees.json")
    
    with open(file_path, "w") as f:
        json.dump(employees, f)

def load_time_entries():
    """Lädt Zeiteinträge aus einer JSON-Datei"""
    data_dir = "data"
    file_path = os.path.join(data_dir, "time_entries.json")
    
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
    else:
        return []

def save_time_entries(time_entries):
    """Speichert Zeiteinträge in einer JSON-Datei"""
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    file_path = os.path.join(data_dir, "time_entries.json")
    
    with open(file_path, "w") as f:
        json.dump(time_entries, f)

def load_projects():
    """Lädt Projekte aus einer JSON-Datei"""
    data_dir = "data"
    file_path = os.path.join(data_dir, "projects.json")
    
    if os.path.exists(file_path):
        with open(file_path, "r") as f:
            return json.load(f)
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
        json.dump(projects, f)

def save_all_data(employees, time_entries=None, projects=None):
    """Speichert alle Daten (Mitarbeiter, Zeiteinträge, Projekte)"""
    # Mitarbeiterdaten speichern
    save_employees(employees)
    
    # Zeiteinträge speichern, falls vorhanden
    if time_entries is not None:
        save_time_entries(time_entries)
    
    # Projekte speichern, falls vorhanden
    if projects is not None:
        save_projects(projects)
