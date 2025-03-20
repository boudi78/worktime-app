import streamlit as st
import datetime
import json
import os
import pandas as pd
from datetime import datetime, timedelta

# Import der Datenpersistenz-Funktionen
from data_persistence import (
    load_employees, save_employees,
    load_time_entries, save_time_entries,
    load_projects, save_projects,
    initialize_data_directory,
    save_all_data
)

# Import der verbesserten Zeiterfassungsfunktionen
from enhanced_time_tracking import (
    implement_stopwatch_functionality,
    implement_project_time_tracking,
    implement_homeoffice_tracking,
    implement_reporting_and_analytics
)

# Import der Admin-Funktionen für Mitarbeiterverwaltung
from admin_employee_management import (
    delete_employee,
    show_employees_page
)

# Import der Urlaubs- und Krankmeldungsverwaltung
from sick_leave_vacation_management import (
    implement_sick_leave_vacation_management
)

# Import des Feiertagskalenders
from holiday_calendar import (
    implement_holiday_calendar
)

# Import der Export-Funktionalität
from export_functionality import (
    implement_export_functionality
)

# Import der Statistik mit Suchfunktion
from statistics_with_search import (
    implement_statistics_with_search
)

# Import der Management-Rollen
from management_roles import (
    implement_management_roles
)

# Initialisierung der Datenverzeichnisse
initialize_data_directory()

# Funktionen initialisieren
show_leave_management_ui, show_admin_leave_management_ui = implement_sick_leave_vacation_management()
show_holiday_calendar_ui = implement_holiday_calendar()
show_export_ui = implement_export_functionality()
show_statistics_ui = implement_statistics_with_search()
show_role_management_ui, has_permission = implement_management_roles()

# Seitentitel
st.set_page_config(page_title="Zeiterfassungs-App", page_icon="⏱️", layout="wide")

# Login-Seite
def show_login_page():
    st.title("Login")
    
    username = st.text_input("Benutzername")
    password = st.text_input("Passwort", type="password")
    
    if st.button("Login"):
        # Mitarbeiterdaten laden
        employees = load_employees()
        
        # Überprüfen, ob Benutzer existiert
        user_exists = False
        for employee in employees:
            if employee["username"] == username and employee["password"] == password:
                user_exists = True
                st.session_state.logged_in = True
                st.session_state.username = username
                st.session_state.user_id = employee["id"]
                st.session_state.is_admin = employee.get("is_admin", False)
                st.session_state.current_employee = employee
                st.success("Login erfolgreich!")
                st.rerun()
                break
        
        if not user_exists:
            st.error("Ungültiger Benutzername oder Passwort!")

# Registrierungsseite
def show_register_page():
    st.title("Registrieren")
    
    name = st.text_input("Name")
    username = st.text_input("Benutzername")
    password = st.text_input("Passwort", type="password")
    confirm_password = st.text_input("Passwort bestätigen", type="password")
    
    if st.button("Registrieren"):
        if password != confirm_password:
            st.error("Passwörter stimmen nicht überein!")
            return
        
        # Mitarbeiterdaten laden
        employees = load_employees()
        
        # Überprüfen, ob Benutzername bereits existiert
        for employee in employees:
            if employee["username"] == username:
                st.error("Benutzername bereits vergeben!")
                return
        
        # Neuen Mitarbeiter erstellen
        new_employee = {
            "id": len(employees) + 1,
            "name": name,
            "username": username,
            "password": password,
            "is_admin": len(employees) == 0,  # Erster Benutzer ist Admin
            "status": "Abwesend",
            "check_in_time": None,
            "check_out_time": None,
            "work_time_model": "vollzeit",
            "custom_schedule": {}
        }
        
        # Mitarbeiter hinzufügen
        employees.append(new_employee)
        save_employees(employees)
        
        st.success("Registrierung erfolgreich! Sie können sich jetzt einloggen.")

# Profilseite
def show_profile_page():
    st.title("Mein Profil")
    
    if "current_employee" in st.session_state:
        employee = st.session_state.current_employee
        
        # Profildaten anzeigen
        st.subheader("Persönliche Daten")
        st.write(f"Name: {employee['name']}")
        st.write(f"Benutzername: {employee['username']}")
        st.write(f"Rolle: {'Administrator' if employee.get('is_admin', False) else 'Mitarbeiter'}")
        
        # Passwort ändern
        st.subheader("Passwort ändern")
        old_password = st.text_input("Altes Passwort", type="password", key="old_password")
        new_password = st.text_input("Neues Passwort", type="password", key="new_password")
        confirm_password = st.text_input("Neues Passwort bestätigen", type="password", key="confirm_password")
        
        if st.button("Passwort ändern"):
            if old_password != employee["password"]:
                st.error("Altes Passwort ist falsch!")
            elif new_password != confirm_password:
                st.error("Neue Passwörter stimmen nicht überein!")
            else:
                # Mitarbeiterdaten laden
                employees = load_employees()
                
                # Passwort aktualisieren
                for emp in employees:
                    if emp["id"] == employee["id"]:
                        emp["password"] = new_password
                        st.session_state.current_employee = emp
                        break
                
                # Mitarbeiterdaten speichern
                save_employees(employees)
                
                st.success("Passwort erfolgreich geändert!")

# Hauptseite
def show_main_page():
    st.title("Zeiterfassung")
    
    if "current_employee" in st.session_state:
        employee = st.session_state.current_employee
        
        # Mitarbeiterdaten laden
        employees = load_employees()
        
        # Aktuellen Mitarbeiter finden
        for emp in employees:
            if emp["id"] == employee["id"]:
                employee = emp
                st.session_state.current_employee = emp
                break
        
        # Status anzeigen
        st.subheader("Status")
        st.write(f"Aktueller Status: {employee['status']}")
        
        # Check-in/Check-out
        if employee["status"] == "Abwesend":
            if st.button("Check-in"):
                # Mitarbeiterdaten aktualisieren
                for emp in employees:
                    if emp["id"] == employee["id"]:
                        emp["status"] = "Anwesend"
                        emp["check_in_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.session_state.current_employee = emp
                        break
                
                # Mitarbeiterdaten speichern
                save_employees(employees)
                
                st.success("Check-in erfolgreich!")
                st.rerun()
        else:
            if st.button("Check-out"):
                # Mitarbeiterdaten aktualisieren
                for emp in employees:
                    if emp["id"] == employee["id"]:
                        emp["status"] = "Abwesend"
                        emp["check_out_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        
                        # Zeiterfassung speichern
                        if "check_in_time" in emp and emp["check_in_time"]:
                            # Zeiteinträge laden
                            time_entries = load_time_entries()
                            
                            # Neuen Zeiteintrag erstellen
                            check_in_time = datetime.strptime(emp["check_in_time"], "%Y-%m-%d %H:%M:%S")
                            check_out_time = datetime.strptime(emp["check_out_time"], "%Y-%m-%d %H:%M:%S")
                            duration = check_out_time - check_in_time
                            
                            new_entry = {
                                "user_id": emp["id"],
                                "start_time": emp["check_in_time"],
                                "end_time": emp["check_out_time"],
                                "duration_seconds": duration.total_seconds(),
                                "duration_formatted": format_duration(duration.total_seconds()),
                                "project": "Allgemein",
                                "homeoffice": False
                            }
                            
                            time_entries.append(new_entry)
                            save_time_entries(time_entries)
                        
                        st.session_state.current_employee = emp
                        break
                
                # Mitarbeiterdaten speichern
                save_employees(employees)
                
                st.success("Check-out erfolgreich!")
                st.rerun()
        
        # Letzte Zeiterfassung anzeigen
        if "check_in_time" in employee and employee["check_in_time"]:
            st.subheader("Letzte Zeiterfassung")
            st.write(f"Check-in: {employee['check_in_time']}")
            
            if "check_out_time" in employee and employee["check_out_time"]:
                st.write(f"Check-out: {employee['check_out_time']}")
                
                # Arbeitszeit berechnen
                check_in_time = datetime.strptime(employee["check_in_time"], "%Y-%m-%d %H:%M:%S")
                check_out_time = datetime.strptime(employee["check_out_time"], "%Y-%m-%d %H:%M:%S")
                duration = check_out_time - check_in_time
                
                st.write(f"Arbeitszeit: {format_duration(duration.total_seconds())}")

# Hilfsfunktion zum Formatieren der Dauer
def format_duration(seconds):
    hours, remainder = divmod(seconds, 3600)
    minutes, seconds = divmod(remainder, 60)
    return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"

# Erweiterte Hauptseite mit allen Funktionen
def show_enhanced_main_page():
    st.sidebar.title("Navigation")
    
    # Benutzerinformationen in der Sidebar anzeigen
    if "username" in st.session_state:
        st.sidebar.write(f"Angemeldet als: {st.session_state.username}")
        if st.session_state.get("is_admin", False):
            st.sidebar.write("(Administrator)")
    
    # Navigationsmenü
    pages = ["Dashboard", "Zeiterfassung", "Projekte", "Homeoffice", "Urlaub & Krankheit", "Feiertagskalender", "Auswertungen", "Export"]
    
    # Admin-Seiten hinzufügen
    if st.session_state.get("is_admin", False):
        pages.extend(["Mitarbeiter", "Rollenverwaltung"])
    
    # Profil-Seite hinzufügen
    pages.append("Profil")
    
    # Seite auswählen
    page = st.sidebar.radio("Seite auswählen", pages)
    
    # Abmelden-Button
    if st.sidebar.button("Abmelden"):
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()
    
    # Seite anzeigen
    if page == "Dashboard":
        show_main_page()
    elif page == "Zeiterfassung":
        # Stoppuhr-Funktion initialisieren und anzeigen
        stopwatch_ui = implement_stopwatch_functionality()
        stopwatch_ui()
    elif page == "Projekte":
        # Projektverwaltung initialisieren und anzeigen
        project_management_ui = implement_project_time_tracking()
        project_management_ui()
    elif page == "Homeoffice":
        # Homeoffice-Tracking initialisieren und anzeigen
        homeoffice_ui = implement_homeoffice_tracking()
        homeoffice_ui()
    elif page == "Urlaub & Krankheit":
        # Urlaubs- und Krankmeldungsverwaltung anzeigen
        if st.session_state.get("is_admin", False):
            show_admin_leave_management_ui()
        else:
            show_leave_management_ui()
    elif page == "Feiertagskalender":
        # Feiertagskalender anzeigen
        show_holiday_calendar_ui()
    elif page == "Auswertungen":
        # Statistiken und Auswertungen anzeigen
        show_statistics_ui()
    elif page == "Export":
        # Export-Funktionalität anzeigen
        show_export_ui()
    elif page == "Mitarbeiter":
        # Mitarbeiterverwaltung anzeigen (nur für Admins)
        if st.session_state.get("is_admin", False):
            show_employees_page()
        else:
            st.warning("Sie haben keine Berechtigung, diese Seite zu sehen.")
    elif page == "Rollenverwaltung":
        # Rollenverwaltung anzeigen (nur für Admins)
        if st.session_state.get("is_admin", False):
            show_role_management_ui()
        else:
            st.warning("Sie haben keine Berechtigung, diese Seite zu sehen.")
    elif page == "Profil":
        # Profilseite anzeigen
        show_profile_page()

# Hauptfunktion der App
def main():
    # Initialisierung der Session-State-Variablen
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False
    
    # Login-Seite anzeigen, wenn nicht eingeloggt
    if not st.session_state.logged_in:
        page = st.sidebar.radio("", ["Login", "Registrieren"])
        
        if page == "Login":
            show_login_page()
        else:
            show_register_page()
    else:
        # Erweiterte Hauptseite mit allen Funktionen anzeigen
        show_enhanced_main_page()

# App starten
if __name__ == "__main__":
    main()
