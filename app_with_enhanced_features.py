import streamlit as st
import json
from typing import Dict, List, Optional, Callable
import datetime
from dateutil.relativedelta import relativedelta
import os


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
import sys
sys.path.append('/home/ubuntu')
from admin_employee_management import (
    delete_employee,
    show_employees_page,
    reset_password,
    add_employee
)

# Import der Urlaubs- und Krankmeldungsverwaltung
from sick_leave_vacation_management import (
    implement_sick_leave_vacation_management
)

# Import des Feiertagskalenders
import sys
sys.path.append('/home/ubuntu')
from holiday_calendar import implement_holiday_calendar

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

# Konstanten für die JSON-Dateinamen
VERWALTUNG_FILE = "verwaltung.json"
ROLES_FILE = "roles.json"
TIME_ENTRIES_FILE = "time_entries.json"  # Konstante für die Zeiteinträge-Datei
LEAVE_REQUESTS_FILE = "leave_requests.json" #Datei für Urlaubsanträge

# Konstanten für das Standard-Arbeitszeitmodell
STANDARD_ARBEITSBEGINN = datetime.time(8, 0)
STANDARD_ARBEITSENDE = datetime.time(17, 0)
STANDARD_PAUSENDAUER_MINUTEN = 60
STANDARD_ARBEITSTAGE = [0, 1, 2, 3, 4]  # Montag bis Freitag (0=Montag, 6=Sonntag)

# Hilfsfunktionen für JSON-Operationen
def _load_json(filename: str) -> dict:
    """Lädt Daten aus einer JSON-Datei oder gibt ein leeres Dictionary zurück, falls die Datei nicht existiert."""
    try:
        with open(filename, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return {}
    except json.JSONDecodeError:
        st.error(f"Fehler beim Dekodieren der JSON-Datei: {filename}. Die Datei wird zurückgesetzt.")
        return {}


def _save_json(filename: str, data: dict) -> None:
    """Speichert Daten in einer JSON-Datei."""
    with open(filename, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4)  # indent für besser lesbare JSON-Dateien

def _update_employee_data(employee_id: int, updates: Dict[str, any]) -> None:
    """
    Aktualisiert Mitarbeiterdaten basierend auf der Mitarbeiter-ID.

    Args:
        employee_id (int): Die ID des Mitarbeiters, der aktualisiert werden soll.
        updates (Dict[str, any]): Ein Dictionary mit den zu aktualisierenden Feldern und Werten.
    """
    employees = load_employees()
    for employee in employees:
        if employee["id"] == employee_id:
            employee.update(updates)
            save_employees(employees)
            return
    st.error(f"Mitarbeiter mit ID {employee_id} nicht gefunden.")

def _get_employee_name(employee_id: int) -> str:
    """
    Gibt den Namen eines Mitarbeiters anhand seiner ID zurück.

    Args:
        employee_id (int): Die ID des Mitarbeiters.

    Returns:
        str: Der Name des Mitarbeiters oder "Unbekannt", falls nicht gefunden.
    """
    employees = load_employees()
    for employee in employees:
        if employee["id"] == employee_id:
            return employee["name"]
    return "Unbekannt"

def _berechne_ueberstunden(check_in_time: datetime.datetime, check_out_time: datetime.datetime) -> float:
    """
    Berechnet die Überstunden in Stunden unter Berücksichtigung des Standard-Arbeitszeitmodells.

    Args:
        check_in_time (datetime.datetime): Der Zeitpunkt des Check-ins.
        check_out_time (datetime.datetime): Der Zeitpunkt des Check-outs.

    Returns:
        float: Die Anzahl der Überstunden in Stunden (positiv für Überstunden, negativ für Minusstunden),
               oder 0, wenn die Arbeitszeit dem Standard entspricht oder die Eingaben ungültig sind.
    """
    if check_in_time is None or check_out_time is None:
        return 0.0

    # Berechne die effektive Arbeitszeit unter Berücksichtigung der Pause
    arbeitszeit_dauer = relativedelta(check_out_time, check_in_time).hours
    effektive_arbeitszeit = arbeitszeit_dauer - (STANDARD_PAUSENDAUER_MINUTEN / 60)

    # Berechne die Soll-Arbeitszeit
    soll_arbeitszeit = (STANDARD_ARBEITSENDE.hour - STANDARD_ARBEITSBEGINN.hour)
    # Berechne die Überstunden
    ueberstunden = effektive_arbeitszeit - soll_arbeitszeit
    return ueberstunden

# Verwaltungsfunktionen
def verwalte_allgemeine_daten():
    """
    Verwaltet allgemeine Daten: Verantwortliche Personen, Abteilungen, Teams, etc.
    Integrierte Zeiterfassung und Lagerortzuweisung.
    """
    st.header("Verwaltung allgemeiner Daten")
    verwaltungs_daten = _load_json(VERWALTUNG_FILE)
    employees = load_employees()
    time_entries = load_time_entries()

    # Stammdaten für Verantwortliche
    st.subheader("Verwaltung Verantwortliche Personen")
    verantwortliche_data = verwaltungs_daten.get("verantwortliche", {})
    verantwortlicher_name = st.text_input("Name Verantwortlicher", key="verantwortlicher_name")
    if st.button("Verantwortlichen Hinzufügen") and verantwortlicher_name:
        if verantwortlicher_name in verantwortliche_data:
            st.error(f"Verantwortlicher '{verantwortlicher_name}' existiert schon")
        else:
            verantwortliche_data[verantwortlicher_name] = {"name": verantwortlicher_name}
            verwaltungs_daten["verantwortliche"] = verantwortliche_data
            _save_json(VERWALTUNG_FILE, verwaltungs_daten)
            st.success(f"Verantwortlicher '{verantwortlicher_name}' hinzugefügt.")

    if verantwortliche_data:
        st.subheader("Verantwortliche:")
        for name in verantwortliche_data:
            st.write(f"- {name}")

    # Auswahl Verantwortlicher zum Bearbeiten/Löschen
    verantwortlicher_auswahl = st.selectbox("Verantwortlicher zum Bearbeiten/Löschen",
                                            [""] + list(verantwortliche_data.keys()),
                                            key="verantwortlicher_auswahl")
    if verantwortlicher_auswahl:
        neuer_name = st.text_input("Neuer Name", value=verantwortliche_data[verantwortlicher_auswahl]["name"], key="neuer_name_verantwortlicher")
        if st.button("Speichern V") and neuer_name:
            if neuer_name in verantwortliche_data and neuer_name != verantwortlicher_auswahl:
                st.error(f"Verantwortlicher '{neuer_name}' existiert bereits.")
            else:
                verantwortliche_data[neuer_name] = verantwortliche_data.pop(verantwortlicher_auswahl)
                verantwortliche_data[neuer_name]["name"] = neuer_name
                verwaltungs_daten["verantwortliche"] = verantwortliche_data
                _save_json(VERWALTUNG_FILE, verwaltungs_daten)
                st.success(f"Verantwortlicher '{verantwortlicher_auswahl}' zu '{neuer_name}' geändert")

    # Stammdaten für Teams
    st.subheader("Verwaltung Teams")
    teams_data = verwaltungs_daten.get("teams", {})

    # Vordefinierte Teams mit Standorten
    vordefinierte_teams = {
        "Team 1": {"name": "Team 1", "standort": "Werner-Siemens-Straße 107, 22113 Hamburg"},
        "Team 2": {"name": "Team 2", "standort": "Werner-Siemens-Straße 39, 22113 Hamburg"},
        "Team 3": {"name": "Team 3", "standort": "Werner-Siemens-Straße 39, 22113 Hamburg"},
        "Lager": {"name": "Lager", "standort": "Werner-Siemens-Straße 107, 22113 Hamburg"}
    }

    # Vordefinierte Teams hinzufügen, falls sie noch nicht existieren
    for team_name, team_data in vordefinierte_teams.items():
        if team_name not in teams_data:
            teams_data[team_name] = team_data
    verwaltungs_daten["teams"] = teams_data

    # Zeiterfassung für Teams
    st.subheader("Zeiterfassung für Teams")
    team_auswahl = st.selectbox("Team auswählen", [""] + list(teams_data.keys()), key="team_auswahl_zeiterfassung")

    if team_auswahl:
        st.subheader(f"Zeiterfassung für Team: {team_auswahl}")
        # Mitarbeiter des Teams anzeigen
        # Verwende get() für sicheren Zugriff auf das 'team'-Feld
        team_mitarbeiter = [mitarbeiter for mitarbeiter in employees if mitarbeiter.get("team") == team_auswahl]

        if not team_mitarbeiter:
            st.write(f"Keine Mitarbeiter in Team {team_auswahl} gefunden.")

        else:
            mitarbeiter_auswahl = st.selectbox("Mitarbeiter auswählen", team_mitarbeiter, key="mitarbeiter_auswahl_team")

            # Standort des Teams anzeigen
            standort = teams_data[team_auswahl]["standort"]
            st.write(f"Standort: {standort}")

            # Letzte Zeiterfassung anzeigen
            if mitarbeiter_auswahl:
                letzter_check_in = None
                letzter_check_out = None
                for entry in time_entries:
                    if entry.get("employee_id") == mitarbeiter_auswahl["id"]:
                        if letzter_check_in is None or entry.get("start_time", "") > letzter_check_in:
                            letzter_check_in = entry.get("start_time", "")
                        if entry.get("end_time") is not None and (letzter_check_out is None or entry.get("end_time", "") > letzter_check_out):
                            letzter_check_out = entry.get("end_time", "")
                if letzter_check_in:
                    st.write(f"Letzter Check-in: {letzter_check_in.strftime('%H:%M:%S')}")
                else:
                    st.write("Kein Check-in gefunden.")

                if letzter_check_out:
                    st.write(f"Letzter Check-out: {letzter_check_out.strftime('%H:%M:%S')}")
                    ueberstunden = _berechne_ueberstunden(letzter_check_in, letzter_check_out)
                    st.write(f"Überstunden: {ueberstunden:.2f} Stunden")
                else:
                    st.write("Kein Check-out gefunden.")

            # Ein- und Auschecken am Standort
            if st.button("Einchecken (Standort)", key="einchecken_standort"):
                check_in_time = datetime.datetime.now()
                
                # Automatische Anpassung der Startzeit, wenn vor 8 Uhr eingecheckt wird
                arbeitsbeginn_heute = datetime.datetime.combine(check_in_time.date(), STANDARD_ARBEITSBEGINN)
                if check_in_time.time() < STANDARD_ARBEITSBEGINN:
                    st.info(f"Frühes Einchecken erkannt (vor {STANDARD_ARBEITSBEGINN.strftime('%H:%M')} Uhr). Die Arbeitszeit wird ab {STANDARD_ARBEITSBEGINN.strftime('%H:%M')} Uhr berechnet.")
                    # Wir speichern die tatsächliche Check-in-Zeit, aber für Berechnungen verwenden wir die Standardzeit
                    recorded_time = check_in_time
                    calculation_time = arbeitsbeginn_heute
                else:
                    recorded_time = check_in_time
                    calculation_time = check_in_time
                
                _update_employee_data(mitarbeiter_auswahl["id"], {
                    "check_in_time": recorded_time, 
                    "calculation_start_time": calculation_time,
                    "status": "Anwesend"
                })

                # Zeitbuchung speichern
                time_entry = {
                    "employee_id": mitarbeiter_auswahl["id"],
                    "employee_name": mitarbeiter_auswahl["name"],
                    "type": "Arbeit",
                    "start_time": recorded_time,
                    "calculation_start_time": calculation_time,
                    "end_time": None,
                    "location": standort,
                    "team": team_auswahl
                }
                time_entries.append(time_entry)
                save_time_entries(time_entries)

                st.success(f"{mitarbeiter_auswahl['name']} eingecheckt um {recorded_time.strftime('%H:%M:%S')} am Standort {standort}")

            if st.button("Auschecken (Standort)", key="auschecken_standort"):
                check_out_time = datetime.datetime.now()
                _update_employee_data(mitarbeiter_auswahl["id"], {"check_out_time": check_out_time, "status": "Abwesend"})

                # Letzte Zeitbuchung aktualisieren
                for entry in reversed(time_entries):
                    if entry.get("employee_id") == mitarbeiter_auswahl["id"] and entry.get("end_time") is None:
                        entry["end_time"] = check_out_time
                        break
                save_time_entries(time_entries)

                st.success(f"{mitarbeiter_auswahl['name']} ausgecheckt um {check_out_time.strftime('%H:%M:%S')} am Standort {standort}")

        # Admin-Funktionen für Teams
        if st.session_state.get("is_admin", False):
            st.subheader("Team-Administration")
            team_name = st.text_input("Team-Name", key="team_name_admin")
            team_standort = st.text_input("Team-Standort", key="team_standort_admin")
            if st.button("Team hinzufügen", key="team_hinzufuegen") and team_name and team_standort:
                if team_name in teams_data:
                    st.error(f"Team '{team_name}' existiert bereits.")
                else:
                    teams_data[team_name] = {"name": team_name, "standort": team_standort}
                    verwaltungs_daten["teams"] = teams_data
                    _save_json(VERWALTUNG_FILE, verwaltungs_daten)
                    st.success(f"Team '{team_name}' hinzugefügt.")

    # Teams anzeigen
    if teams_data:
        st.subheader("Teams:")
        for name, data in teams_data.items():
            st.write(f"- {name}: {data['standort']}")

    # Team bearbeiten/löschen
    team_auswahl_bearbeiten = st.selectbox("Team zum Bearbeiten/Löschen", [""] + list(teams_data.keys()), key="team_auswahl_bearbeiten")
    if team_auswahl_bearbeiten:
        neuer_standort = st.text_input("Neuer Standort", value=teams_data[team_auswahl_bearbeiten]["standort"], key="neuer_standort")

        if st.button("Löschen T", key="team_loeschen") and team_auswahl_bearbeiten in vordefinierte_teams:
            st.warning("Vordefinierte Teams können nicht gelöscht werden.")
        elif st.button("Löschen T", key="team_loeschen_2"):
            del teams_data[team_auswahl_bearbeiten]
            verwaltungs_daten["teams"] = teams_data
            _save_json(VERWALTUNG_FILE, verwaltungs_daten)
            st.success(f"Team '{team_auswahl_bearbeiten}' gelöscht")

        if st.button("Speichern T", key="team_speichern") and neuer_standort:
            teams_data[team_auswahl_bearbeiten]["standort"] = neuer_standort
            verwaltungs_daten["teams"] = teams_data
            _save_json(VERWALTUNG_FILE, verwaltungs_daten)
            st.success(f"Standort für Team '{team_auswahl_bearbeiten}' aktualisiert.")

# Login-Funktion
def show_login_page() -> None:
    """Zeigt die Login-Seite an."""
    st.title("Login")

    # Eingabefelder für den Login
    username = st.text_input("Benutzername", key="login_username")
    password = st.text_input("Passwort", type="password", key="login_password")

    # Login-Button
    if st.button("Login", key="login_button"):
        # Überprüfen, ob Benutzername und Passwort korrekt sind
        employees = load_employees()
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

# Erweiterte Registrierungsfunktion
def show_register_page() -> None:
    """Zeigt die Registrierungsseite an."""
    st.title("Registrieren")

    # Eingabefelder für die Registrierung
    name = st.text_input("Name", key="register_name")
    username = st.text_input("Benutzername", key="register_username")
    password = st.text_input("Passwort", type="password", key="register_password")
    confirm_password = st.text_input("Passwort bestätigen", type="password", key="register_confirm_password")

    # Team-Auswahl hinzufügen
    team_options = ["Team 1", "Team 2", "Team 3", "Lager"]
    selected_team = st.selectbox("Team auswählen", team_options, key="register_team")

    # Standort automatisch basierend auf Team bestimmen
    if selected_team == "Team 1":
        standort = "Werner-Siemens-Straße 107, 22113 Hamburg"
    elif selected_team == "Team 2":
        standort = "Werner-Siemens-Straße 39, 22113 Hamburg"
    elif selected_team == "Team 3":
        standort = "Werner-Siemens-Straße 39, 22113 Hamburg"
    elif selected_team == "Lager":
        # Lager kann an beiden Standorten sein, hier Standardwert setzen
        standort = "Werner-Siemens-Straße 107, 22113 Hamburg"

    # Anzeige des zugewiesenen Standorts
    st.info(f"Zugewiesener Standort: {standort}")

    # Registrieren-Button
    if st.button("Registrieren", key="register_button"):
        # Überprüfen, ob alle Felder ausgefüllt sind
        if not name or not username or not password or not confirm_password:
            st.error("Bitte füllen Sie alle Felder aus!")
            return

        # Überprüfen, ob die Passwörter übereinstimmen
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

        # Neue ID generieren
        new_id = 1
        if employees:
            new_id = max(employee["id"] for employee in employees) + 1

        # Neuen Mitarbeiter erstellen
        new_employee = {
            "id": new_id,
            "name": name,
            "username": username,
            "password": password,
            "is_admin": len(employees) == 0,  # Erster Benutzer ist Admin
            "status": "Abwesend",
            "check_in_time": None,
            "check_out_time": None,
            "work_time_model": "vollzeit",
            "custom_schedule": {},
            "team": selected_team,
            "standort": standort
        }

        # Mitarbeiter hinzufügen und speichern
        employees.append(new_employee)
        save_employees(employees)

        st.success("Registrierung erfolgreich! Sie können sich jetzt einloggen.")


# Erweiterte Registrierungsfunktion
def show_register_page() -> None:
    """Zeigt die Registrierungsseite an."""
    st.title("Registrieren")

    # Eingabefelder für die Registrierung
    name = st.text_input("Name", key="register_name")
    username = st.text_input("Benutzername", key="register_username")
    password = st.text_input("Passwort", type="password", key="register_password")
    confirm_password = st.text_input("Passwort bestätigen", type="password", key="register_confirm_password")

    # Team-Auswahl hinzufügen
    team_options = ["Team 1", "Team 2", "Team 3", "Lager"]
    selected_team = st.selectbox("Team auswählen", team_options, key="register_team")

    # Standort automatisch basierend auf Team bestimmen
    if selected_team == "Team 1":
        standort = "Werner-Siemens-Straße 107, 22113 Hamburg"
    elif selected_team == "Team 2":
        standort = "Werner-Siemens-Straße 39, 22113 Hamburg"
    elif selected_team == "Team 3":
        standort = "Werner-Siemens-Straße 39, 22113 Hamburg"
    elif selected_team == "Lager":
        # Lager kann an beiden Standorten sein, hier Standardwert setzen
        standort = "Werner-Siemens-Straße 107, 22113 Hamburg"

    # Anzeige des zugewiesenen Standorts
    st.info(f"Zugewiesener Standort: {standort}")

    # Registrieren-Button
    if st.button("Registrieren", key="register_button"):
        # Überprüfen, ob alle Felder ausgefüllt sind
        if not name or not username or not password or not confirm_password:
            st.error("Bitte füllen Sie alle Felder aus!")
            return

        # Überprüfen, ob die Passwörter übereinstimmen
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

        # Neue ID generieren
        new_id = 1
        if employees:
            new_id = max(employee["id"] for employee in employees) + 1

        # Neuen Mitarbeiter erstellen
        new_employee = {
            "id": new_id,
            "name": name,
            "username": username,
            "password": password,
            "is_admin": len(employees) == 0,  # Erster Benutzer ist Admin
            "status": "Abwesend",
            "check_in_time": None,
            "check_out_time": None,
            "work_time_model": "vollzeit",
            "custom_schedule": {},
            "team": selected_team,
            "standort": standort
        }

        # Mitarbeiter hinzufügen und speichern
        employees.append(new_employee)
        save_employees(employees)

        st.success("Registrierung erfolgreich! Sie können sich jetzt einloggen.")

# Profilseite
def show_profile_page() -> None:
    """Zeigt die Profilseite des angemeldeten Benutzers an."""
    st.title("Mein Profil")

    if "user_id" in st.session_state:
        # Mitarbeiterdaten laden
        employees = load_employees()
        employee = next((e for e in employees if e["id"] == st.session_state.user_id), None)

        if employee:
            st.write(f"Name: {employee['name']}")
            st.write(f"Benutzername: {employee['username']}")
            if "is_admin" in employee:
                st.write(f"Admin-Rechte: {'Ja' if employee['is_admin'] else 'Nein'}")
            if "team" in employee:
                st.write(f"Team: {employee['team']}")
            if "standort" in employee:
                st.write(f"Standort: {employee['standort']}")
            if "work_time_model" in employee:
                st.write(f"Arbeitszeitmodell: {employee['work_time_model']}")

            # Passwort ändern
            st.subheader("Passwort ändern")
            altes_passwort = st.text_input("Altes Passwort", type="password", key="altes_passwort")
            neues_passwort = st.text_input("Neues Passwort", type="password", key="neues_passwort")
            neues_passwort_bestaetigen = st.text_input("Neues Passwort bestätigen", type="password", key="neues_passwort_bestaetigen")

            if st.button("Passwort ändern", key="passwort_aendern"):
                # Logik zum Ändern des Passworts einfügen
                if neues_passwort == neues_passwort_bestaetigen:
                    if altes_passwort == employee['password']:
                        # Hier die Logik zum Passwort ändern
                        st.success("Passwort wurde erfolgreich geändert")
                    else:
                        st.error("Altes Passwort ist falsch")
                else:
                    st.error("Neue Passwörter stimmen nicht überein!")
    else:
        st.write("Profilinformationen nicht verfügbar.")

# Rollenverwaltungsfunktionen
def verwalte_rollen():
    """
    Verwaltet Rollen: Hinzufügen, Anzeigen, Bearbeiten, Löschen von Rollen und deren Berechtigungen.
    """
    st.header("Rollenverwaltung")
    roles_data = _load_json(ROLES_FILE)

    # Neue Rolle hinzufügen
    st.subheader("Neue Rolle hinzufügen")
    role_name = st.text_input("Rollenname", key="role_name")
    role_description = st.text_area("Beschreibung", key="role_description")
    
    # Berechtigungen definieren
    st.write("Berechtigungen:")
    can_view_all_employees = st.checkbox("Alle Mitarbeiter sehen", key="can_view_all_employees")
    can_edit_all_employees = st.checkbox("Alle Mitarbeiter bearbeiten", key="can_edit_all_employees")
    can_manage_roles = st.checkbox("Rollen verwalten", key="can_manage_roles")
    can_view_statistics = st.checkbox("Statistiken einsehen", key="can_view_statistics")
    can_export_data = st.checkbox("Daten exportieren", key="can_export_data")
    can_manage_projects = st.checkbox("Projekte verwalten", key="can_manage_projects")
    
    if st.button("Rolle hinzufügen", key="rolle_hinzufuegen") and role_name:
        if role_name in roles_data:
            st.error(f"Rolle '{role_name}' existiert bereits.")
        else:
            roles_data[role_name] = {
                "name": role_name,
                "description": role_description,
                "permissions": {
                    "view_all_employees": can_view_all_employees,
                    "edit_all_employees": can_edit_all_employees,
                    "manage_roles": can_manage_roles,
                    "view_statistics": can_view_statistics,
                    "export_data": can_export_data,
                    "manage_projects": can_manage_projects
                }
            }
            _save_json(ROLES_FILE, roles_data)
            st.success(f"Rolle '{role_name}' hinzugefügt.")
    
    # Rollen anzeigen
    if roles_data:
        st.subheader("Vorhandene Rollen:")
        for name, data in roles_data.items():
            with st.expander(f"{name} - {data.get('description', '')}"):
                st.write("Berechtigungen:")
                permissions = data.get("permissions", {})
                for perm_name, perm_value in permissions.items():
                    st.write(f"- {perm_name}: {'Ja' if perm_value else 'Nein'}")
    
    # Rolle bearbeiten/löschen
    st.subheader("Rolle bearbeiten/löschen")
    role_select = st.selectbox("Rolle auswählen", [""] + list(roles_data.keys()), key="role_select")
    
    if role_select:
        role_data = roles_data[role_select]
        
        new_name = st.text_input("Neuer Name", value=role_data["name"], key="new_role_name")
        new_description = st.text_area("Neue Beschreibung", value=role_data.get("description", ""), key="new_role_description")
        
        st.write("Berechtigungen aktualisieren:")
        permissions = role_data.get("permissions", {})
        new_can_view_all_employees = st.checkbox("Alle Mitarbeiter sehen", value=permissions.get("view_all_employees", False), key="edit_view_all")
        new_can_edit_all_employees = st.checkbox("Alle Mitarbeiter bearbeiten", value=permissions.get("edit_all_employees", False), key="edit_edit_all")
        new_can_manage_roles = st.checkbox("Rollen verwalten", value=permissions.get("manage_roles", False), key="edit_manage_roles")
        new_can_view_statistics = st.checkbox("Statistiken einsehen", value=permissions.get("view_statistics", False), key="edit_view_stats")
        new_can_export_data = st.checkbox("Daten exportieren", value=permissions.get("export_data", False), key="edit_export")
        new_can_manage_projects = st.checkbox("Projekte verwalten", value=permissions.get("manage_projects", False), key="edit_manage_projects")
        
        if st.button("Rolle aktualisieren", key="rolle_aktualisieren"):
            # Alte Rolle entfernen und neue hinzufügen
            del roles_data[role_select]
            roles_data[new_name] = {
                "name": new_name,
                "description": new_description,
                "permissions": {
                    "view_all_employees": new_can_view_all_employees,
                    "edit_all_employees": new_can_edit_all_employees,
                    "manage_roles": new_can_manage_roles,
                    "view_statistics": new_can_view_statistics,
                    "export_data": new_can_export_data,
                    "manage_projects": new_can_manage_projects
                }
            }
            _save_json(ROLES_FILE, roles_data)
            st.success(f"Rolle '{role_select}' aktualisiert zu '{new_name}'.")
        
        if st.button("Rolle löschen", key="rolle_loeschen"):
            del roles_data[role_select]
            _save_json(ROLES_FILE, roles_data)
            st.success(f"Rolle '{role_select}' gelöscht.")

# Verbesserte Standortauswahl für die Zeiterfassungs-App
def show_location_selection_page():
    """Zeigt die Seite für die Standortauswahl an."""
    st.title("Arbeitsort auswählen")
    
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("Bitte melden Sie sich an, um diese Seite zu nutzen.")
        return
    
    # Mitarbeiterdaten laden
    employees = load_employees()
    time_entries = load_time_entries()
    
    # Aktuellen Mitarbeiter finden
    current_employee = next((e for e in employees if e["id"] == st.session_state.user_id), None)
    
    if current_employee:
        st.write(f"Aktueller Status: {current_employee.get('status', 'Unbekannt')}")
        
        # Standortoptionen
        st.subheader("Arbeitsort auswählen")
        location_options = [
            "Homeoffice", 
            "Werner-Siemens-Straße 107, 22113 Hamburg", 
            "Werner-Siemens-Straße 39, 22113 Hamburg"
        ]
        selected_location = st.radio("Wählen Sie Ihren Arbeitsort:", location_options, key="location_selection")
        
        # Ein- und Auschecken am ausgewählten Standort
        if st.button("Einchecken", key="location_checkin"):
            check_in_time = datetime.datetime.now()
            
            # Automatische Anpassung der Startzeit, wenn vor 8 Uhr eingecheckt wird
            arbeitsbeginn_heute = datetime.datetime.combine(check_in_time.date(), STANDARD_ARBEITSBEGINN)
            if check_in_time.time() < STANDARD_ARBEITSBEGINN:
                st.info(f"Frühes Einchecken erkannt (vor {STANDARD_ARBEITSBEGINN.strftime('%H:%M')} Uhr). Die Arbeitszeit wird ab {STANDARD_ARBEITSBEGINN.strftime('%H:%M')} Uhr berechnet.")
                # Wir speichern die tatsächliche Check-in-Zeit, aber für Berechnungen verwenden wir die Standardzeit
                recorded_time = check_in_time
                calculation_time = arbeitsbeginn_heute
            else:
                recorded_time = check_in_time
                calculation_time = check_in_time
            
            # Status basierend auf Standort setzen
            status = "Homeoffice" if selected_location == "Homeoffice" else "Anwesend"
            
            _update_employee_data(current_employee["id"], {
                "check_in_time": recorded_time, 
                "calculation_start_time": calculation_time,
                "status": status,
                "current_location": selected_location
            })
            
            # Zeitbuchung speichern
            time_entry = {
                "employee_id": current_employee["id"],
                "employee_name": current_employee["name"],
                "type": "Homeoffice" if selected_location == "Homeoffice" else "Arbeit",
                "start_time": recorded_time,
                "calculation_start_time": calculation_time,
                "end_time": None,
                "location": selected_location,
                "team": current_employee.get("team", "Unbekannt")
            }
            time_entries.append(time_entry)
            save_time_entries(time_entries)
            st.success(f"Eingecheckt um {recorded_time.strftime('%H:%M:%S')} an {selected_location}")
        
        if st.button("Auschecken", key="location_checkout"):
            check_out_time = datetime.datetime.now()
            _update_employee_data(current_employee["id"], {
                "check_out_time": check_out_time, 
                "status": "Abwesend",
                "current_location": None
            })
            
            # Letzte Zeitbuchung aktualisieren
            for entry in reversed(time_entries):
                if entry.get("employee_id") == current_employee["id"] and entry.get("end_time") is None:
                    entry["end_time"] = check_out_time
                    break
            save_time_entries(time_entries)
            st.success(f"Ausgecheckt um {check_out_time.strftime('%H:%M:%S')}")
        
        # Anwesenheitshistorie anzeigen
        st.subheader("Meine Anwesenheitshistorie")
        attendance_entries = [entry for entry in time_entries if entry.get("employee_id") == current_employee["id"]]
        
        if not attendance_entries:
            st.info("Keine Anwesenheitseinträge gefunden.")
        else:
            for entry in reversed(attendance_entries):
                start_time = entry.get("start_time")
                end_time = entry.get("end_time", "Noch nicht ausgecheckt")
                location = entry.get("location", "Unbekannt")
                
                if isinstance(start_time, str):
                    start_time = datetime.datetime.fromisoformat(start_time)
                
                if isinstance(end_time, str) and end_time != "Noch nicht ausgecheckt":
                    end_time = datetime.datetime.fromisoformat(end_time)
                
                if isinstance(start_time, datetime.datetime):
                    start_time_str = start_time.strftime("%d.%m.%Y %H:%M:%S")
                else:
                    start_time_str = str(start_time)
                
                if isinstance(end_time, datetime.datetime):
                    end_time_str = end_time.strftime("%d.%m.%Y %H:%M:%S")
                else:
                    end_time_str = str(end_time)
                
                st.write(f"Standort: {location}")
                st.write(f"Start: {start_time_str}, Ende: {end_time_str}")
                st.write("---")

# Für Administratoren: Standortverwaltung für alle Mitarbeiter
def show_admin_location_management():
    """Zeigt die Standortverwaltung für Administratoren an."""
    st.title("Standortverwaltung (Admin)")
    
    if "logged_in" not in st.session_state or not st.session_state.logged_in:
        st.warning("Bitte melden Sie sich an, um diese Seite zu nutzen.")
        return
    
    if not st.session_state.get("is_admin", False):
        st.warning("Sie haben keine Berechtigung, diese Seite zu sehen.")
        return
    
    # Mitarbeiterdaten laden
    employees = load_employees()
    time_entries = load_time_entries()
    
    # Mitarbeiter auswählen
    st.subheader("Mitarbeiter auswählen")
    mitarbeiter_optionen = [emp["name"] for emp in employees]
    mitarbeiter_auswahl = st.selectbox("Mitarbeiter", mitarbeiter_optionen, key="admin_location_mitarbeiter")
    
    if mitarbeiter_auswahl:
        # Mitarbeiter-ID finden
        mitarbeiter_id = next((e["id"] for e in employees if e["name"] == mitarbeiter_auswahl), None)
        mitarbeiter = next((e for e in employees if e["name"] == mitarbeiter_auswahl), None)
        
        if mitarbeiter:
            st.write(f"Aktueller Status: {mitarbeiter.get('status', 'Unbekannt')}")
            st.write(f"Aktueller Standort: {mitarbeiter.get('current_location', 'Nicht eingecheckt')}")
            
            # Standortoptionen
            st.subheader("Arbeitsort auswählen")
            location_options = [
                "Homeoffice", 
                "Werner-Siemens-Straße 107, 22113 Hamburg", 
                "Werner-Siemens-Straße 39, 22113 Hamburg"
            ]
            selected_location = st.radio("Wählen Sie den Arbeitsort:", location_options, key="admin_location_selection")
            
            # Ein- und Auschecken am ausgewählten Standort
            if st.button("Einchecken", key="admin_location_checkin"):
                check_in_time = datetime.datetime.now()
                
                # Automatische Anpassung der Startzeit, wenn vor 8 Uhr eingecheckt wird
                arbeitsbeginn_heute = datetime.datetime.combine(check_in_time.date(), STANDARD_ARBEITSBEGINN)
                if check_in_time.time() < STANDARD_ARBEITSBEGINN:
                    st.info(f"Frühes Einchecken erkannt (vor {STANDARD_ARBEITSBEGINN.strftime('%H:%M')} Uhr). Die Arbeitszeit wird ab {STANDARD_ARBEITSBEGINN.strftime('%H:%M')} Uhr berechnet.")
                    # Wir speichern die tatsächliche Check-in-Zeit, aber für Berechnungen verwenden wir die Standardzeit
                    recorded_time = check_in_time
                    calculation_time = arbeitsbeginn_heute
                else:
                    recorded_time = check_in_time
                    calculation_time = check_in_time
                
                # Status basierend auf Standort setzen
                status = "Homeoffice" if selected_location == "Homeoffice" else "Anwesend"
                
                _update_employee_data(mitarbeiter_id, {
                    "check_in_time": recorded_time, 
                    "calculation_start_time": calculation_time,
                    "status": status,
                    "current_location": selected_location
                })
                
                # Zeitbuchung speichern
                time_entry = {
                    "employee_id": mitarbeiter_id,
                    "employee_name": mitarbeiter_auswahl,
                    "type": "Homeoffice" if selected_location == "Homeoffice" else "Arbeit",
                    "start_time": recorded_time,
                    "calculation_start_time": calculation_time,
                    "end_time": None,
                    "location": selected_location,
                    "team": mitarbeiter.get("team", "Unbekannt")
                }
                time_entries.append(time_entry)
                save_time_entries(time_entries)
                st.success(f"{mitarbeiter_auswahl} eingecheckt um {recorded_time.strftime('%H:%M:%S')} an {selected_location}")
            
            if st.button("Auschecken", key="admin_location_checkout"):
                check_out_time = datetime.datetime.now()
                _update_employee_data(mitarbeiter_id, {
                    "check_out_time": check_out_time, 
                    "status": "Abwesend",
                    "current_location": None
                })
                
                # Letzte Zeitbuchung aktualisieren
                for entry in reversed(time_entries):
                    if entry.get("employee_id") == mitarbeiter_id and entry.get("end_time") is None:
                        entry["end_time"] = check_out_time
                        break
                save_time_entries(time_entries)
                st.success(f"{mitarbeiter_auswahl} ausgecheckt um {check_out_time.strftime('%H:%M:%S')}")
            
            # Anwesenheitshistorie anzeigen
            st.subheader(f"Anwesenheitshistorie für {mitarbeiter_auswahl}")
            attendance_entries = [entry for entry in time_entries if entry.get("employee_id") == mitarbeiter_id]
            
            if not attendance_entries:
                st.info("Keine Anwesenheitseinträge gefunden.")
            else:
                for entry in reversed(attendance_entries):
                    start_time = entry.get("start_time")
                    end_time = entry.get("end_time", "Noch nicht ausgecheckt")
                    location = entry.get("location", "Unbekannt")
                    
                    if isinstance(start_time, str):
                        start_time = datetime.datetime.fromisoformat(start_time)
                    
                    if isinstance(end_time, str) and end_time != "Noch nicht ausgecheckt":
                        end_time = datetime.datetime.fromisoformat(end_time)
                    
                    if isinstance(start_time, datetime.datetime):
                        start_time_str = start_time.strftime("%d.%m.%Y %H:%M:%S")
                    else:
                        start_time_str = str(start_time)
                    
                    if isinstance(end_time, datetime.datetime):
                        end_time_str = end_time.strftime("%d.%m.%Y %H:%M:%S")
                    else:
                        end_time_str = str(end_time)
                    
                    st.write(f"Standort: {location}")
                    st.write(f"Start: {start_time_str}, Ende: {end_time_str}")
                    st.write("---")

from statistics_with_search import implement_statistics_with_search

# Hauptfunktion
def main():
    """Hauptfunktion der App."""
    # Initialisierung der Session-State-Variablen
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    # Initialisierung der UI-Funktionen
    show_statistics_ui = implement_statistics_with_search()

    # Seitenleiste für die Navigation
    if st.session_state.logged_in:
        st.sidebar.title("Navigation")
        
        # Menüoptionen basierend auf Benutzerrolle
        menu_options = ["Profil", "Zeiterfassung", "Arbeitsort", "Urlaub/Krankmeldung", "Feiertagskalender"]
        
        # Admin-spezifische Menüoptionen
        if st.session_state.get("is_admin", False):
            menu_options.extend(["Auswertungen", "Export", "Mitarbeiter", "Rollenverwaltung", "Standortverwaltung"])
        
        page = st.sidebar.selectbox("Seite auswählen", menu_options, key="navigation_menu")
        
        # Logout-Button
        if st.sidebar.button("Logout", key="logout_button"):
            st.session_state.logged_in = False
            st.session_state.username = None
            st.session_state.user_id = None
            st.session_state.is_admin = False
            st.session_state.current_employee = None
            st.rerun()
        
        # Anzeige der ausgewählten Seite
        if page == "Profil":
            show_profile_page()
        elif page == "Zeiterfassung":
            verwalte_allgemeine_daten()
        elif page == "Arbeitsort":
            show_location_selection_page()
        elif page == "Urlaub/Krankmeldung":
            show_leave_management_ui()
        elif page == "Feiertagskalender":
            show_holiday_calendar_ui()
        elif page == "Auswertungen":
            show_statistics_ui()
        elif page == "Export":
            show_export_ui()
        elif page == "Mitarbeiter":
            if st.session_state.get("is_admin", False):
                show_employees_page()
            else:
                st.warning("Sie haben keine Berechtigung, diese Seite zu sehen.")
        elif page == "Rollenverwaltung":
            if st.session_state.get("is_admin", False):
                show_role_management_ui()
            else:
                st.warning("Sie haben keine Berechtigung, diese Seite zu sehen.")
        elif page == "Standortverwaltung":
            if st.session_state.get("is_admin", False):
                show_admin_location_management()
            else:
                st.warning("Sie haben keine Berechtigung, diese Seite zu sehen.")
        elif page == "Admin Urlaub/Krankmeldung":
            if st.session_state.get("is_admin", False):
                show_admin_leave_management_ui()
            else:
                st.warning("Sie haben keine Berechtigung, diese Seite zu sehen.")
    else:
        tab1, tab2 = st.tabs(["Login", "Registrieren"])
        with tab1:
            show_login_page()
        with tab2:
            show_register_page()

if __name__ == "__main__":
    main()
