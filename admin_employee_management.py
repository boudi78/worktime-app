import streamlit as st
import json
import os
from typing import List, Dict, Any

def load_employees() -> List[Dict[str, Any]]:
    """Lädt Mitarbeiterdaten aus der JSON-Datei."""
    data_dir = "data"
    file_path = os.path.join(data_dir, "employees.json")
    
    if os.path.exists(file_path):
        with open(file_path, "r", encoding="utf-8") as f:
            return json.load(f)
    else:
        return []

def save_employees(employees: List[Dict[str, Any]]) -> None:
    """Speichert Mitarbeiterdaten in der JSON-Datei."""
    data_dir = "data"
    if not os.path.exists(data_dir):
        os.makedirs(data_dir)
        
    file_path = os.path.join(data_dir, "employees.json")
    
    with open(file_path, "w", encoding="utf-8") as f:
        json.dump(employees, f, indent=4)

def delete_employee(employee_id: int) -> None:
    """Löscht einen Mitarbeiter anhand seiner ID."""
    employees = load_employees()
    employees = [e for e in employees if e["id"] != employee_id]
    save_employees(employees)

def reset_password(employee_id: int, new_password: str) -> bool:
    """Setzt das Passwort eines Mitarbeiters zurück."""
    employees = load_employees()
    for employee in employees:
        if employee["id"] == employee_id:
            employee["password"] = new_password
            save_employees(employees)
            return True
    return False

def add_employee(name: str, username: str, password: str, team: str, standort: str, is_admin: bool = False) -> bool:
    """Fügt einen neuen Mitarbeiter hinzu."""
    employees = load_employees()
    
    # Überprüfen, ob Benutzername bereits existiert
    for employee in employees:
        if employee["username"] == username:
            return False
    
    # Neue ID generieren
    new_id = 1
    if employees:
        new_id = max(e["id"] for e in employees) + 1
    
    # Neuen Mitarbeiter erstellen
    new_employee = {
        "id": new_id,
        "name": name,
        "username": username,
        "password": password,
        "is_admin": is_admin,
        "status": "Abwesend",
        "check_in_time": None,
        "check_out_time": None,
        "work_time_model": "vollzeit",
        "custom_schedule": {},
        "team": team,
        "standort": standort
    }
    
    employees.append(new_employee)
    save_employees(employees)
    return True

def show_employees_page():
    """Zeigt die Mitarbeiterverwaltungsseite für Administratoren an."""
    st.title("Mitarbeiterverwaltung")
    
    if not st.session_state.get("is_admin", False):
        st.error("Sie haben keine Berechtigung, auf diese Seite zuzugreifen.")
        return
    
    employees = load_employees()
    
    # Tabs für verschiedene Funktionen
    tab1, tab2, tab3 = st.tabs(["Mitarbeiter hinzufügen", "Passwort zurücksetzen", "Mitarbeiter löschen"])
    
    with tab1:
        st.header("Neuen Mitarbeiter hinzufügen")
        
        name = st.text_input("Name", key="add_name")
        username = st.text_input("Benutzername", key="add_username")
        password = st.text_input("Passwort", type="password", key="add_password")
        confirm_password = st.text_input("Passwort bestätigen", type="password", key="add_confirm_password")
        
        # Team-Auswahl
        team_options = ["Team 1", "Team 2", "Team 3", "Lager"]
        selected_team = st.selectbox("Team auswählen", team_options, key="add_team")
        
        # Standort automatisch basierend auf Team bestimmen
        if selected_team == "Team 1":
            standort = "Werner-Siemens-Straße 107, 22113 Hamburg"
        elif selected_team == "Team 2":
            standort = "Werner-Siemens-Straße 39, 22113 Hamburg"
        elif selected_team == "Team 3":
            standort = "Werner-Siemens-Straße 39, 22113 Hamburg"
        elif selected_team == "Lager":
            standort = "Werner-Siemens-Straße 107, 22113 Hamburg"
        
        # Anzeige des zugewiesenen Standorts
        st.info(f"Zugewiesener Standort: {standort}")
        
        # Admin-Rechte
        is_admin = st.checkbox("Administrator-Rechte gewähren", key="add_is_admin")
        
        if st.button("Mitarbeiter hinzufügen"):
            if not name or not username or not password:
                st.error("Bitte füllen Sie alle Felder aus.")
            elif password != confirm_password:
                st.error("Passwörter stimmen nicht überein!")
            else:
                success = add_employee(name, username, password, selected_team, standort, is_admin)
                if success:
                    st.success(f"Mitarbeiter {name} wurde erfolgreich hinzugefügt.")
                    # Felder zurücksetzen
                    st.session_state.add_name = ""
                    st.session_state.add_username = ""
                    st.session_state.add_password = ""
                    st.session_state.add_confirm_password = ""
                    st.session_state.add_is_admin = False
                else:
                    st.error(f"Benutzername {username} ist bereits vergeben.")
    
    with tab2:
        st.header("Passwort zurücksetzen")
        
        # Mitarbeiter auswählen
        employee_options = [f"{e['name']} ({e['username']})" for e in employees]
        selected_employee = st.selectbox("Mitarbeiter auswählen", [""] + employee_options, key="reset_employee")
        
        if selected_employee:
            # Ausgewählten Mitarbeiter finden
            selected_username = selected_employee.split("(")[1].split(")")[0]
            employee = next((e for e in employees if e["username"] == selected_username), None)
            
            if employee:
                new_password = st.text_input("Neues Passwort", type="password", key="reset_password")
                confirm_password = st.text_input("Passwort bestätigen", type="password", key="reset_confirm_password")
                
                if st.button("Passwort zurücksetzen"):
                    if not new_password:
                        st.error("Bitte geben Sie ein neues Passwort ein.")
                    elif new_password != confirm_password:
                        st.error("Passwörter stimmen nicht überein!")
                    else:
                        success = reset_password(employee["id"], new_password)
                        if success:
                            st.success(f"Passwort für {employee['name']} wurde erfolgreich zurückgesetzt.")
                            # Felder zurücksetzen
                            st.session_state.reset_password = ""
                            st.session_state.reset_confirm_password = ""
                        else:
                            st.error("Fehler beim Zurücksetzen des Passworts.")
    
    with tab3:
        st.header("Mitarbeiter löschen")
        
        # Mitarbeiter auswählen
        employee_options = [f"{e['name']} ({e['username']})" for e in employees]
        selected_employee = st.selectbox("Mitarbeiter auswählen", [""] + employee_options, key="delete_employee")
        
        if selected_employee:
            # Ausgewählten Mitarbeiter finden
            selected_username = selected_employee.split("(")[1].split(")")[0]
            employee = next((e for e in employees if e["username"] == selected_username), None)
            
            if employee:
                st.warning(f"Sind Sie sicher, dass Sie den Mitarbeiter {employee['name']} löschen möchten? Diese Aktion kann nicht rückgängig gemacht werden.")
                
                if st.button("Mitarbeiter löschen"):
                    delete_employee(employee["id"])
                    st.success(f"Mitarbeiter {employee['name']} wurde erfolgreich gelöscht.")
                    st.rerun()  # Seite neu laden, um die Liste zu aktualisieren

# Exportiere die Funktionen
__all__ = ['delete_employee', 'show_employees_page', 'reset_password', 'add_employee']
