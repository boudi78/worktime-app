import streamlit as st
import pandas as pd
import json
import os

# Nur für Heroku: config.toml automatisch erzeugen
if not os.path.exists('.streamlit'):
    os.makedirs('.streamlit')

with open('.streamlit/config.toml', 'w') as f:
    f.write("""
[server]
headless = true
port = $PORT
enableCORS = false
""")

from datetime import datetime
from modules.utils import LOCATION_CODES, load_employees, load_time_entries, load_vacation_requests, load_sick_leaves, save_time_entry
from modules.login import show_login
from modules.calendar import show_calendar
from modules.admin_page import show as show_admin

# Konfiguration
st.set_page_config(
    page_title="Worktime App",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialisierung der Session State
if "current_page" not in st.session_state:
    st.session_state.current_page = "Login"

if "checkin_time" not in st.session_state:
    st.session_state.checkin_time = None

if "location" not in st.session_state:
    st.session_state.location = None

if "user" not in st.session_state:
    st.session_state.user = None

# Seitenwechsel-Funktion
def set_page(page_name):
    st.session_state.current_page = page_name
    st.rerun()

# Login-Seite
if st.session_state.current_page == "Login":
    show_login()
    # Keine Sidebar anzeigen bei Login
    st.stop()

# Sidebar mit Navigation
with st.sidebar:
    # Logo und Firmenname anzeigen
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("grafik.png", width=50)
    with col2:
        st.write("### Team-sped")
        st.write("Seehafenspedition GmbH")
    
    st.title("Worktime App")
    # Überprüfe, ob user in session_state existiert und nicht None ist
    if "user" in st.session_state and st.session_state.user is not None:
        st.write(f"Angemeldet als {st.session_state.user['name']} ({st.session_state.user['role']})")
    else:
        st.write("Nicht angemeldet")
    
    # Navigationsmenü
    st.subheader("Navigation")
    
    if st.button("🏠 Startseite"):
        set_page("Home")
    
    if st.button("⏱️ Ein-/Auschecken"):
        set_page("Check-in/Check-out")
    
    if st.button("📅 Kalender"):
        set_page("Calendar")
    
    if st.button("📊 Statistiken"):
        set_page("Stats")
    
    if st.button("🟡 Urlaub"):
        set_page("Vacation")
    
    if st.button("🔴 Krankmeldung"):
        set_page("Sick Leave")
    
    if st.button("🔔 Benachrichtigungen"):
        set_page("Notifications")
    
    if st.button("🔑 Passwort ändern"):
        set_page("Change Password")
    
    # Überprüfe, ob user in session_state existiert und nicht None ist, bevor auf role zugegriffen wird
    if "user" in st.session_state and st.session_state.user is not None and st.session_state.user.get("role") == "Admin":
        if st.button("⚙️ Administration"):
            set_page("Admin")
    
    if st.button("🚪 Abmelden"):
        st.session_state.user = None
        st.session_state.current_page = "Login"
        st.rerun()

# Hauptinhalt basierend auf ausgewählter Seite
current_page = st.session_state.current_page

if current_page == "Home":
    st.title("🏠 Startseite")
    st.write("Willkommen bei der Worktime App!")
    
    # Aktuelle Zeit anzeigen
    st.subheader("Aktuelle Zeit")
    st.write(datetime.now().strftime("%d.%m.%Y %H:%M:%S"))
    
    # Status anzeigen
    if st.session_state.checkin_time:
        st.success(f"Sie sind seit {st.session_state.checkin_time.strftime('%H:%M:%S')} eingecheckt.")
    else:
        st.info("Sie sind derzeit nicht eingecheckt.")

elif current_page == "Check-in/Check-out":
    st.title("⏱️ Ein-/Auschecken")
    
    # Arbeitsort auswählen - HIER DIE NEUEN STANDORTE VERWENDEN
    location = st.selectbox(
        "Arbeitsort auswählen",
        list(LOCATION_CODES.keys())  # Verwendet die Standorte aus utils.py
    )
    location_code = LOCATION_CODES[location]
    
    st.markdown("---")
    
    # Check-in Logik
    if st.session_state.checkin_time is None:
        if st.button("✅ Jetzt einchecken"):
            st.session_state.checkin_time = datetime.now()
            st.session_state.location = location_code
            st.success(f"Eingecheckt um {st.session_state.checkin_time.strftime('%H:%M:%S')} ({location})")
            st.rerun()
    else:
        st.info(f"Eingecheckt um: {st.session_state.checkin_time.strftime('%H:%M:%S')} ({st.session_state.location})")
        
        note = st.text_area("📝 Kommentar (optional)")
        
        if st.button("🚪 Auschecken"):
            checkout_time = datetime.now()
            duration = checkout_time - st.session_state.checkin_time
            hours = round(duration.total_seconds() / 3600, 2)
            
            st.success(f"Ausgecheckt um {checkout_time.strftime('%H:%M:%S')}")
            st.info(f"Arbeitszeit: {hours} Stunden\nKommentar: {note if note else '–'}")
            
            # Overtime Calculation
            checkin_datetime = st.session_state.checkin_time
            is_weekend = checkin_datetime.weekday() >= 5  # Saturday=5, Sunday=6
            is_overtime = is_weekend or hours > 8
            
            # Save Time Entry - mit Überprüfung, ob user existiert
            if "user" in st.session_state and st.session_state.user is not None:
                entry = {
                    "user_id": st.session_state.user.get("id", "unknown"),
                    "check_in": st.session_state.checkin_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "check_out": checkout_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "duration_hours": hours,
                    "location": st.session_state.location,
                    "note": note,
                    "overtime": is_overtime
                }
                save_time_entry(entry)
            else:
                st.warning("Benutzer nicht angemeldet. Zeiteintrag konnte nicht gespeichert werden.")
            
            # Reset
            st.session_state.checkin_time = None
            st.session_state.location = None
            st.rerun()

elif current_page == "Calendar":
    # Verwende die Kalenderfunktion aus dem Modul
    show_calendar()

elif current_page == "Stats":
    st.title("📊 Statistiken")
    
    # Tabs für verschiedene Statistiken
    tabs = ["Arbeitszeit", "Überstunden", "Abwesenheiten", "Mitarbeiterübersicht"]
    
    # Füge Admin-Tab hinzu, wenn Benutzer Admin ist
    if "user" in st.session_state and st.session_state.user is not None and st.session_state.user.get("role") == "Admin":
        tabs.append("Mitarbeitersuche")
    
    selected_tab = st.tabs(tabs)
    
    # Tab 1: Arbeitszeit
    with selected_tab[0]:
        st.subheader("Arbeitszeitanalyse")
        st.write("Hier werden Arbeitszeitstatistiken angezeigt.")
        
        # Beispieldaten
        data = {
            "Mitarbeiter": ["Admin User", "Test User 1", "Test User 2"],
            "Arbeitsstunden": [40, 35, 42]
        }
        df = pd.DataFrame(data)
        
        # Balkendiagramm
        st.bar_chart(df.set_index("Mitarbeiter"))
        
        # Tabelle
        st.dataframe(df)
    
    # Tab 2: Überstunden
    with selected_tab[1]:
        st.subheader("Überstundenanalyse")
        st.write("Hier werden Überstundenstatistiken angezeigt.")
        
        # Beispieldaten
        data = {
            "Mitarbeiter": ["Admin User", "Test User 1", "Test User 2"],
            "Reguläre Stunden": [40, 35, 38],
            "Überstunden": [2, 0, 4]
        }
        df = pd.DataFrame(data)
        
        # Tabelle
        st.dataframe(df)
    
    # Tab 3: Abwesenheiten
    with selected_tab[2]:
        st.subheader("Abwesenheitsanalyse")
        st.write("Hier werden Urlaubs- und Krankheitsstatistiken angezeigt.")
        
        # Beispieldaten
        data = {
            "Mitarbeiter": ["Admin User", "Test User 1", "Test User 2"],
            "Urlaubstage": [5, 10, 3],
            "Kranktage": [2, 1, 0]
        }
        df = pd.DataFrame(data)
        
        # Tabelle
        st.dataframe(df)
    
    # Tab 4: Mitarbeiterübersicht
    with selected_tab[3]:
        st.subheader("Mitarbeiterübersicht")
        
        # Mitarbeiter auswählen
        employee_names = ["Admin User", "Test User 1", "Test User 2"]
        selected_employee = st.selectbox("Mitarbeiter auswählen", employee_names)
        
        # Beispieldaten
        if selected_employee == "Admin User":
            data = {
                "Datum": ["2025-04-01", "2025-04-02", "2025-04-03"],
                "Stunden": [8.5, 7.5, 8.0],
                "Standort": ["Werner Siemens Strasse 107", "Werner Siemens Strasse 39", "Home Office"]
            }
        else:
            data = {
                "Datum": ["2025-04-01", "2025-04-02", "2025-04-03"],
                "Stunden": [8.0, 8.0, 7.5],
                "Standort": ["Werner Siemens Strasse 107", "Werner Siemens Strasse 107", "Home Office"]
            }
        
        df = pd.DataFrame(data)
        st.dataframe(df)
    
    # Tab 5: Mitarbeitersuche (nur für Admins)
    if "user" in st.session_state and st.session_state.user is not None and st.session_state.user.get("role") == "Admin" and len(selected_tab) > 4:
        with selected_tab[4]:
            st.subheader("Mitarbeitersuche")
            
            # Suchfeld
            search_term = st.text_input("Suche nach Mitarbeitern")
            
            if search_term:
                # Beispieldaten
                data = {
                    "Name": ["Admin User", "Test User 1", "Test User 2"],
                    "E-Mail": ["admin@example.com", "user1@example.com", "user2@example.com"],
                    "Standort": ["Werner Siemens Strasse 107", "Werner Siemens Strasse 39", "Home Office"]
                }
                df = pd.DataFrame(data)
                
                # Filtern
                filtered_df = df[df["Name"].str.contains(search_term, case=False) | 
                                df["E-Mail"].str.contains(search_term, case=False)]
                
                if not filtered_df.empty:
                    st.dataframe(filtered_df)
                else:
                    st.info("Keine Ergebnisse gefunden.")

elif current_page == "Vacation":
    st.title("🟡 Urlaub")
    
    # Tabs für Urlaubsanträge und Übersicht
    tab1, tab2 = st.tabs(["Urlaubsantrag stellen", "Urlaubsübersicht"])
    
    with tab1:
        st.subheader("Neuen Urlaubsantrag stellen")
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Startdatum")
        with col2:
            end_date = st.date_input("Enddatum")
        
        reason = st.text_area("Grund (optional)")
        
        if st.button("Urlaubsantrag einreichen"):
            if start_date > end_date:
                st.error("Das Startdatum muss vor dem Enddatum liegen.")
            else:
                st.success("Urlaubsantrag eingereicht!")
                # Hier würde der Antrag gespeichert werden
    
    with tab2:
        st.subheader("Ihre Urlaubsanträge")
        
        # Beispieldaten
        data = {
            "Startdatum": ["2025-05-01", "2025-08-15"],
            "Enddatum": ["2025-05-10", "2025-08-30"],
            "Status": ["Genehmigt", "Ausstehend"]
        }
        df = pd.DataFrame(data)
        
        # Tabelle
        st.dataframe(df)
        
        # Urlaubskontingent
        st.subheader("Urlaubskontingent")
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Gesamtanspruch", "30 Tage")
        with col2:
            st.metric("Genommen", "10 Tage")
        with col3:
            st.metric("Verbleibend", "20 Tage")

elif current_page == "Sick Leave":
    st.title("🔴 Krankmeldung")
    
    # Tabs für Krankmeldung und Übersicht
    tab1, tab2 = st.tabs(["Krankmeldung einreichen", "Krankmeldungsübersicht"])
    
    with tab1:
        st.subheader("Neue Krankmeldung einreichen")
        
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Startdatum")
        with col2:
            end_date = st.date_input("Voraussichtliches Enddatum")
        
        reason = st.text_area("Grund (optional)")
        
        if st.button("Krankmeldung einreichen"):
            if start_date > end_date:
                st.error("Das Startdatum muss vor dem Enddatum liegen.")
            else:
                st.success("Krankmeldung eingereicht!")
                # Hier würde die Krankmeldung gespeichert werden
    
    with tab2:
        st.subheader("Ihre Krankmeldungen")
        
        # Beispieldaten
        data = {
            "Startdatum": ["2025-03-10", "2025-01-05"],
            "Enddatum": ["2025-03-12", "2025-01-07"],
            "Grund": ["Erkältung", "Grippe"]
        }
        df = pd.DataFrame(data)
        
        # Tabelle
        st.dataframe(df)

elif current_page == "Notifications":
    st.title("🔔 Benachrichtigungen")
    
    # Beispiel-Benachrichtigungen
    st.info("Ihr Urlaubsantrag vom 15.08.2025 bis 30.08.2025 wurde genehmigt.")
    st.warning("Bitte reichen Sie Ihre Stundenzettel für März 2025 ein.")
    st.success("Willkommen zurück! Wir hoffen, Sie hatten einen erholsamen Urlaub.")

elif current_page == "Change Password":
    st.title("🔑 Passwort ändern")
    
    current_password = st.text_input("Aktuelles Passwort", type="password")
    new_password = st.text_input("Neues Passwort", type="password")
    confirm_password = st.text_input("Neues Passwort bestätigen", type="password")
    
    if st.button("Passwort ändern"):
        if new_password != confirm_password:
            st.error("Die Passwörter stimmen nicht überein.")
        else:
            st.success("Passwort erfolgreich geändert!")

elif current_page == "Admin":
    # Verwende die Admin-Funktion aus dem Modul
    show_admin()
