import os
import json

def initialize_app():
    os.makedirs("data", exist_ok=True)

    # employees.json anlegen, wenn nicht vorhanden
    employees_file = os.path.join("data", "employees.json")
    if not os.path.exists(employees_file):
        with open(employees_file, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4, ensure_ascii=False)
        print("✅ Datei employees.json wurde neu erstellt.")

    # time_entries.json anlegen, wenn nicht vorhanden
    time_entries_file = os.path.join("data", "time_entries.json")
    if not os.path.exists(time_entries_file):
        with open(time_entries_file, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4, ensure_ascii=False)
        print("✅ Datei time_entries.json wurde neu erstellt.")

    # sick_leave.json anlegen
    sick_leave_file = os.path.join("data", "sick_leave.json")
    if not os.path.exists(sick_leave_file):
        with open(sick_leave_file, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4, ensure_ascii=False)

    # vacation_requests.json anlegen
    vacation_file = os.path.join("data", "vacation_requests.json")
    if not os.path.exists(vacation_file):
        with open(vacation_file, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4, ensure_ascii=False)

    # events.json anlegen (für Feiertage, Home Office etc.)
    events_file = os.path.join("data", "events.json")
    if not os.path.exists(events_file):
        with open(events_file, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4, ensure_ascii=False)

    print("📁 Alle Dateien sind vorbereitet.")
