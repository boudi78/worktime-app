import os
import json
import shutil

DATA_DIR = "data"
JSON_FILES = ["employees.json", "time_entries.json", "projects.json", "teams.json", "leave_requests.json"]

def check_and_repair_json(file_name):
    file_path = os.path.join(DATA_DIR, file_name)

    # Wenn Datei nicht existiert oder leer ist
    if not os.path.exists(file_path) or os.stat(file_path).st_size == 0:
        print(f"[!] {file_name} fehlt oder ist leer – wird mit leeren Daten wiederhergestellt.")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4)
        return

    # Versuche Datei zu laden
    try:
        with open(file_path, "r", encoding="utf-8") as f:
            json.load(f)
        print(f"[OK] {file_name} ist gültig.")
    except json.JSONDecodeError:
        # Backup erstellen
        backup_path = file_path + ".backup"
        shutil.copy(file_path, backup_path)
        print(f"[⚠️] {file_name} ist beschädigt! Backup gespeichert unter {backup_path}")
        with open(file_path, "w", encoding="utf-8") as f:
            json.dump([], f, indent=4)
        print(f"[+] {file_name} wurde repariert mit leeren Daten.")

def run_repair_tool():
    print("🔍 JSON-Reparatur läuft...\n")
    for json_file in JSON_FILES:
        check_and_repair_json(json_file)
    print("\n✅ Überprüfung abgeschlossen.")

if __name__ == "__main__":
    run_repair_tool()
