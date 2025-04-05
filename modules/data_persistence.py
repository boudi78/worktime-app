# modules/data_persistence.py

import os
import json
from datetime import datetime
from typing import List, Dict

# -----------------------
# Dateipfade
# -----------------------
DATA_FOLDER = "data"
EMPLOYEE_FILE = os.path.join(DATA_FOLDER, "employees.json")
TIME_FILE = os.path.join(DATA_FOLDER, "time_entries.json")
VACATION_FILE = os.path.join(DATA_FOLDER, "vacation_requests.json")

# Stelle sicher, dass der data-Ordner existiert
os.makedirs(DATA_FOLDER, exist_ok=True)

# -----------------------
# JSON Helferfunktionen
# -----------------------

def load_json(path: str) -> list:
    if not os.path.exists(path):
        return []
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError:
            return []

def save_json(path: str, data: list):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# -----------------------
# Mitarbeiterfunktionen
# -----------------------

def load_employees() -> list:
    return load_json(EMPLOYEE_FILE)

def save_employees(employees: list):
    save_json(EMPLOYEE_FILE, employees)

def save_employee(employee: dict):
    employees = load_employees()
    updated = False
    for i, e in enumerate(employees):
        if e["id"] == employee["id"]:
            employees[i] = employee
            updated = True
            break
    if not updated:
        employees.append(employee)
    save_employees(employees)

# -----------------------
# Zeiteinträge
# -----------------------

def load_time_entries() -> list:
    return load_json(TIME_FILE)

def save_time_entries(entries: list):
    save_json(TIME_FILE, entries)

def save_time_entry(entry: dict):
    entries = load_time_entries()
    entries.append(entry)
    save_time_entries(entries)

# -----------------------
# Urlaubsanträge
# -----------------------

def load_vacation_requests() -> list:
    return load_json(VACATION_FILE)

def save_vacation_requests(requests: list):
    save_json(VACATION_FILE, requests)

def save_vacation_request(request: dict):
    requests = load_vacation_requests()
    requests.append(request)
    save_vacation_requests(requests)

# -----------------------
# Helper für Urlaubsauswertung
# -----------------------

def calculate_vacation_days_taken(user_id: str) -> int:
    requests = load_vacation_requests()
    total_days = 0
    for r in requests:
        if r["user_id"] == user_id:
            start = datetime.strptime(r["start_date"], "%Y-%m-%d")
            end = datetime.strptime(r["end_date"], "%Y-%m-%d")
            total_days += (end - start).days + 1
    return total_days

def calculate_remaining_vacation(user_id: str, vacation_days_entitled: int) -> int:
    taken = calculate_vacation_days_taken(user_id)
    return vacation_days_entitled - taken
