
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
    initialize_data_directory
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

# Implementierung der Mitarbeiterverwaltung für den Fall, dass das Modul nicht existiert
def show_employees_page():
    # Bestehender Code zur Mitarbeiterverwaltung...
    pass

# Funktion für Urlaub & Krankheit
def show_leave_and_sickness_page():
    st.title("Urlaub & Krankheit")
    leave_type = st.selectbox("Art der Abwesenheit", ["Urlaub", "Krankheit"])
    start_date = st.date_input("Startdatum")
    end_date = st.date_input("Enddatum")
    if st.button("Abwesenheit melden"):
        st.success("Abwesenheit erfolgreich gemeldet!")

# Feiertagskalender
def show_holiday_calendar_page():
    st.title("Feiertagskalender")
    st.write("Hier kannst du Feiertage einsehen.")
    # Hier könnte eine Logik zur Anzeige von Feiertagen eingebaut werden

# Export-Seite
def show_export_page():
    st.title("Export")
    if st.button("Daten exportieren"):
        time_entries = load_time_entries()
        df = pd.DataFrame(time_entries)
        df.to_csv("time_entries.csv", index=False)
        st.success("Daten erfolgreich exportiert!")

# Rollenverwaltung
def show_role_management_page():
    if st.session_state.get("is_admin", False):
        st.title("Rollenverwaltung")
        st.write("🔧 Hier kannst du Rollen verwalten.")
    else:
        st.warning("Sie haben keine Berechtigung, diese Seite zu sehen.")

# Seitenübersicht für die erweiterte Navigation
def show_enhanced_main_page():
    st.sidebar.title("Navigation")
    pages = ["Dashboard", "Zeiterfassung", "Projekte", "Homeoffice", "Auswertungen", "Urlaub & Krankheit", "Feiertagskalender", "Export", "Mitarbeiter", "Rollenverwaltung", "Profil"]
    if st.session_state.get("is_admin", False):
        pages.append("Admin")
    selected_page = st.sidebar.radio("Seite auswählen", pages)

    if selected_page == "Dashboard":
        st.write("🏠 Willkommen im Dashboard")
    elif selected_page == "Zeiterfassung":
        implement_stopwatch_functionality()
    elif selected_page == "Projekte":
        implement_project_time_tracking()
    elif selected_page == "Homeoffice":
        implement_homeoffice_tracking()
    elif selected_page == "Auswertungen":
        implement_reporting_and_analytics()
    elif selected_page == "Urlaub & Krankheit":
        show_leave_and_sickness_page()
    elif selected_page == "Feiertagskalender":
        show_holiday_calendar_page()
    elif selected_page == "Export":
        show_export_page()
    elif selected_page == "Mitarbeiter":
        show_employees_page()
    elif selected_page == "Rollenverwaltung":
        show_role_management_page()
    elif selected_page == "Profil":
        st.write("👤 Benutzerprofil")

# Hauptseite
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
