import os
import json
from datetime import datetime
from datetime_utils import parse_datetime_string  # Siehe unten für datetime_utils.py

class DateTimeEncoder(json.JSONEncoder):
    def default(self, obj):
        if isinstance(obj, datetime):
            return obj.isoformat()
        return super().default(obj)

def initialize_data_directory():
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)

def load_employees():
    data_dir = "data"
    file_path = os.path.join(data_dir, "employees.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            employees = json.load(f)
            # Konvertiere Strings zurück in datetime-Objekte
            for emp in employees:
                if "check_in_time" in emp and isinstance(emp["check_in_time"], str):
                    emp["check_in_time"] = parse_datetime_string(emp["check_in_time"])
                if "check_out_time" in emp and isinstance(emp["check_out_time"], str):
                    emp["check_out_time"] = parse_datetime_string(emp["check_out_time"])
            return employees
    else:
        return []

def save_employees(employees):
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    file_path = os.path.join(data_dir, "employees.json")
    # Konvertiere datetime-Objekte in Strings
    for emp in employees:
        if "check_in_time" in emp and isinstance(emp["check_in_time"], datetime):
            emp["check_in_time"] = emp["check_in_time"].isoformat()
        if "check_out_time" in emp and isinstance(emp["check_out_time"], datetime):
            emp["check_out_time"] = emp["check_out_time"].isoformat()
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(employees, f, cls=DateTimeEncoder, indent=4)

def load_time_entries():
    data_dir = "data"
    file_path = os.path.join(data_dir, "time_entries.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            entries = json.load(f)
            # Konvertiere Strings zurück in datetime-Objekte
            for entry in entries:
                entry["start_time"] = parse_datetime_string(entry.get("start_time"))
                entry["end_time"] = parse_datetime_string(entry.get("end_time"))
            return entries
    else:
        return []

def save_time_entries(time_entries):
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    file_path = os.path.join(data_dir, "time_entries.json")
    # Konvertiere datetime-Objekte in Strings
    for entry in time_entries:
        if "start_time" in entry and isinstance(entry["start_time"], datetime):
            entry["start_time"] = entry["start_time"].isoformat()
        if "end_time" in entry and isinstance(entry["end_time"], datetime):
            entry["end_time"] = entry["end_time"].isoformat()
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(time_entries, f, cls=DateTimeEncoder, indent=4)

# Weitere Funktionen (load_projects, save_projects, etc.) analog anpassen

# Laden der Projektdaten
def load_projects():
    """Lädt Projektdaten aus der JSON-Datei."""
    data_dir = "data"
    file_path = os.path.join(data_dir, "projects.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print("Fehler: projects.json ist beschädigt. Eine neue leere Datei wird erstellt.")
                save_projects([])
                return []
    else:
        return []

# Speichern der Projektdaten
def save_projects(projects):
    """Speichert Projektdaten in der JSON-Datei."""
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    file_path = os.path.join(data_dir, "projects.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(projects, f, cls=DateTimeEncoder, indent=4)

# Laden der Urlaubs- und Krankheitsdaten
def load_leave_data():
    """Lädt Urlaubs- und Krankheitsdaten aus der JSON-Datei."""
    data_dir = "data"
    file_path = os.path.join(data_dir, "leave_data.json")
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                return json.load(f)
            except json.JSONDecodeError:
                print("Fehler: leave_data.json ist beschädigt. Eine neue leere Datei wird erstellt.")
                save_leave_data({"vacation": {}, "sick_leave": {}})
                return {"vacation": {}, "sick_leave": {}}
    else:
        return {"vacation": {}, "sick_leave": {}}

# Speichern der Urlaubs- und Krankheitsdaten
def save_leave_data(leave_data):
    """Speichert Urlaubs- und Krankheitsdaten in der JSON-Datei."""
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
    file_path = os.path.join(data_dir, "leave_data.json")
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(leave_data, f, cls=DateTimeEncoder, indent=4)

# Speichern aller Daten
def save_all_data(employees, time_entries, projects, leave_data):
    """Speichert alle Daten gleichzeitig."""
    save_employees(employees)
    save_time_entries(time_entries)
    save_projects(projects)
    save_leave_data(leave_data)