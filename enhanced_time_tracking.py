import streamlit as st
import datetime
import time
import json
import os
from datetime import datetime, timedelta

# Funktionen für die verbesserte Zeiterfassung basierend auf der Recherche
# von Clockin, ZEP, Crewmeister, TimeTac, MOCO, Personizer und ZMI

def implement_stopwatch_functionality():
    """
    Implementiert eine Stoppuhr-Funktion für die genaue Zeiterfassung
    Inspiriert von MOCO und Clockin
    """
    def start_timer():
        if "timer_running" not in st.session_state:
            st.session_state.timer_running = False
        if "timer_start_time" not in st.session_state:
            st.session_state.timer_start_time = None
        if "timer_elapsed" not in st.session_state:
            st.session_state.timer_elapsed = 0
        if "timer_project" not in st.session_state:
            st.session_state.timer_project = None
            
        st.session_state.timer_running = True
        st.session_state.timer_start_time = datetime.now()
        
    def stop_timer():
        if st.session_state.timer_running:
            elapsed = datetime.now() - st.session_state.timer_start_time
            st.session_state.timer_elapsed += elapsed.total_seconds()
            st.session_state.timer_running = False
            
            # Zeiterfassung speichern
            if "time_entries" not in st.session_state:
                st.session_state.time_entries = []
                
            entry = {
                "user_id": st.session_state.get("user_id"),
                "project": st.session_state.timer_project,
                "start_time": st.session_state.timer_start_time.strftime("%Y-%m-%d %H:%M:%S"),
                "end_time": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                "duration_seconds": elapsed.total_seconds(),
                "duration_formatted": format_duration(elapsed.total_seconds()),
                "homeoffice": st.session_state.get("homeoffice_active", False)
            }
            
            st.session_state.time_entries.append(entry)
            save_time_entries()
            
            # Timer zurücksetzen
            st.session_state.timer_elapsed = 0
            st.session_state.timer_start_time = None
            st.session_state.timer_project = None
    
    def format_duration(seconds):
        hours, remainder = divmod(seconds, 3600)
        minutes, seconds = divmod(remainder, 60)
        return f"{int(hours):02d}:{int(minutes):02d}:{int(seconds):02d}"
    
    def get_current_timer_display():
        if st.session_state.timer_running:
            current_elapsed = datetime.now() - st.session_state.timer_start_time
            total_seconds = st.session_state.timer_elapsed + current_elapsed.total_seconds()
            return format_duration(total_seconds)
        else:
            return format_duration(st.session_state.timer_elapsed)
    
    def save_time_entries():
        """Speichert Zeiteinträge in einer JSON-Datei"""
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            
        file_path = os.path.join(data_dir, "time_entries.json")
        
        with open(file_path, "w") as f:
            json.dump(st.session_state.time_entries, f)
    
    def load_time_entries():
        """Lädt Zeiteinträge aus einer JSON-Datei"""
        data_dir = "data"
        file_path = os.path.join(data_dir, "time_entries.json")
        
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                st.session_state.time_entries = json.load(f)
        else:
            st.session_state.time_entries = []
    
    # Stoppuhr-UI
    def show_stopwatch_ui():
        st.subheader("Zeiterfassung mit Stoppuhr")
        
        # Initialisierung der Session-State-Variablen
        if "timer_running" not in st.session_state:
            st.session_state.timer_running = False
        if "timer_start_time" not in st.session_state:
            st.session_state.timer_start_time = None
        if "timer_elapsed" not in st.session_state:
            st.session_state.timer_elapsed = 0
        if "timer_project" not in st.session_state:
            st.session_state.timer_project = None
        if "time_entries" not in st.session_state:
            load_time_entries()
            
        # Projekt auswählen
        projects = ["Projekt A", "Projekt B", "Projekt C", "Internes", "Sonstiges"]
        selected_project = st.selectbox("Projekt auswählen", projects, key="project_select")
        
        # Homeoffice-Option
        homeoffice = st.checkbox("Im Homeoffice", key="homeoffice_checkbox")
        st.session_state.homeoffice_active = homeoffice
        
        # Timer-Anzeige
        timer_display = get_current_timer_display() if st.session_state.timer_running else "00:00:00"
        st.markdown(f"<h1 style='text-align: center;'>{timer_display}</h1>", unsafe_allow_html=True)
        
        # Start/Stop-Buttons
        col1, col2 = st.columns(2)
        with col1:
            if not st.session_state.timer_running:
                if st.button("Start", key="start_timer_button"):
                    st.session_state.timer_project = selected_project
                    start_timer()
                    st.experimental_rerun()
        with col2:
            if st.session_state.timer_running:
                if st.button("Stop", key="stop_timer_button"):
                    stop_timer()
                    st.experimental_rerun()
        
        # Letzte Einträge anzeigen
        st.subheader("Letzte Zeiteinträge")
        if st.session_state.time_entries:
            # Nur die Einträge des aktuellen Benutzers anzeigen
            user_entries = [entry for entry in st.session_state.time_entries 
                           if entry.get("user_id") == st.session_state.get("user_id")]
            
            # Sortieren nach Startzeit (neueste zuerst)
            user_entries.sort(key=lambda x: x["start_time"], reverse=True)
            
            # Die letzten 5 Einträge anzeigen
            for entry in user_entries[:5]:
                with st.expander(f"{entry['project']} - {entry['duration_formatted']}"):
                    st.write(f"Start: {entry['start_time']}")
                    st.write(f"Ende: {entry['end_time']}")
                    st.write(f"Dauer: {entry['duration_formatted']}")
                    st.write(f"Homeoffice: {'Ja' if entry.get('homeoffice', False) else 'Nein'}")
        else:
            st.info("Keine Zeiteinträge vorhanden")
    
    return show_stopwatch_ui

def implement_project_time_tracking():
    """
    Implementiert die Projektzeiterfassung
    Inspiriert von ZEP und MOCO
    """
    def save_projects():
        """Speichert Projekte in einer JSON-Datei"""
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            
        file_path = os.path.join(data_dir, "projects.json")
        
        with open(file_path, "w") as f:
            json.dump(st.session_state.projects, f)
    
    def load_projects():
        """Lädt Projekte aus einer JSON-Datei"""
        data_dir = "data"
        file_path = os.path.join(data_dir, "projects.json")
        
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                st.session_state.projects = json.load(f)
        else:
            # Beispielprojekte
            st.session_state.projects = [
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
            save_projects()
    
    def update_project_hours():
        """Aktualisiert die verbrauchten Stunden für jedes Projekt"""
        if "time_entries" in st.session_state and "projects" in st.session_state:
            # Zurücksetzen der verbrauchten Stunden
            for project in st.session_state.projects:
                project["used_hours"] = 0
                
            # Berechnen der verbrauchten Stunden aus den Zeiteinträgen
            for entry in st.session_state.time_entries:
                project_name = entry.get("project")
                duration_hours = entry.get("duration_seconds", 0) / 3600
                
                for project in st.session_state.projects:
                    if project["name"] == project_name:
                        project["used_hours"] += duration_hours
                        break
            
            save_projects()
    
    def show_project_management_ui():
        st.subheader("Projektverwaltung")
        
        # Initialisierung
        if "projects" not in st.session_state:
            load_projects()
            
        # Aktualisieren der Projektstunden
        update_project_hours()
        
        # Tabs für Projektübersicht und Projektverwaltung
        tab1, tab2 = st.tabs(["Projektübersicht", "Neues Projekt"])
        
        with tab1:
            st.subheader("Projektübersicht")
            
            # Projekte anzeigen
            for project in st.session_state.projects:
                with st.expander(f"{project['name']} ({project['used_hours']:.1f}h / {project['budget_hours']}h)"):
                    st.write(f"Beschreibung: {project['description']}")
                    
                    # Fortschrittsbalken
                    if project['budget_hours'] > 0:
                        progress = min(project['used_hours'] / project['budget_hours'], 1.0)
                        st.progress(progress)
                        
                        # Warnung, wenn Budget fast aufgebraucht
                        if progress > 0.8 and progress < 1.0:
                            st.warning(f"Achtung: Bereits {progress*100:.1f}% des Budgets verbraucht!")
                        elif progress >= 1.0:
                            st.error("Budget überschritten!")
                    
                    # Zeiteinträge für dieses Projekt anzeigen
                    if "time_entries" in st.session_state:
                        project_entries = [entry for entry in st.session_state.time_entries 
                                         if entry.get("project") == project['name']]
                        
                        if project_entries:
                            st.write("Letzte Einträge:")
                            for entry in sorted(project_entries, key=lambda x: x["start_time"], reverse=True)[:3]:
                                st.write(f"- {entry['start_time']} ({entry['duration_formatted']})")
        
        with tab2:
            if st.session_state.get("is_admin", False):
                st.subheader("Neues Projekt anlegen")
                
                # Formular für neues Projekt
                with st.form("new_project_form"):
                    project_name = st.text_input("Projektname")
                    project_description = st.text_area("Beschreibung")
                    project_budget = st.number_input("Budget (Stunden)", min_value=0.0, step=0.5)
                    
                    submit_button = st.form_submit_button("Projekt anlegen")
                    
                    if submit_button:
                        if project_name:
                            # Neue Projekt-ID generieren
                            new_id = max([p["id"] for p in st.session_state.projects], default=0) + 1
                            
                            # Neues Projekt hinzufügen
                            new_project = {
                                "id": new_id,
                                "name": project_name,
                                "description": project_description,
                                "budget_hours": project_budget,
                                "used_hours": 0
                            }
                            
                            st.session_state.projects.append(new_project)
                            save_projects()
                            st.success(f"Projekt '{project_name}' erfolgreich angelegt!")
                        else:
                            st.error("Bitte geben Sie einen Projektnamen ein!")
            else:
                st.info("Nur Administratoren können neue Projekte anlegen.")
    
    return show_project_management_ui

def implement_homeoffice_tracking():
    """
    Implementiert die Homeoffice-Dokumentation
    Inspiriert von Personizer und TimeTac
    """
    def save_homeoffice_data():
        """Speichert Homeoffice-Daten in einer JSON-Datei"""
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            
        file_path = os.path.join(data_dir, "homeoffice_data.json")
        
        with open(file_path, "w") as f:
            json.dump(st.session_state.homeoffice_data, f)
    
    def load_homeoffice_data():
        """Lädt Homeoffice-Daten aus einer JSON-Datei"""
        data_dir = "data"
        file_path = os.path.join(data_dir, "homeoffice_data.json")
        
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                st.session_state.homeoffice_data = json.load(f)
        else:
            st.session_state.homeoffice_data = {}
    
    def calculate_homeoffice_stats():
        """Berechnet Homeoffice-Statistiken aus den Zeiteinträgen"""
        if "time_entries" in st.session_state:
            # Initialisierung der Homeoffice-Daten
            if "homeoffice_data" not in st.session_state:
                load_homeoffice_data()
                
            # Benutzer-ID abrufen
            user_id = st.session_state.get("user_id")
            if not user_id:
                return
                
            # Initialisierung der Benutzerdaten
            if user_id not in st.session_state.homeoffice_data:
                st.session_state.homeoffice_data[user_id] = {
                    "total_days": 0,
                    "total_hours": 0,
                    "monthly_data": {}
                }
                
            # Zurücksetzen der Gesamtwerte
            st.session_state.homeoffice_data[user_id]["total_days"] = 0
            st.session_state.homeoffice_data[user_id]["total_hours"] = 0
            st.session_state.homeoffice_data[user_id]["monthly_data"] = {}
            
            # Berechnen der Homeoffice-Tage und -Stunden
            homeoffice_days = set()
            
            for entry in st.session_state.time_entries:
                if entry.get("user_id") == user_id and entry.get("homeoffice", False):
                    # Datum extrahieren
                    date_str = entry.get("start_time", "").split()[0]
                    if date_str:
                        homeoffice_days.add(date_str)
                        
                    # Stunden berechnen
                    duration_hours = entry.get("duration_seconds", 0) / 3600
                    st.session_state.homeoffice_data[user_id]["total_hours"] += duration_hours
                    
                    # Monatsdaten aktualisieren
                    if date_str:
                        year_month = date_str[:7]  # YYYY-MM
                        if year_month not in st.session_state.homeoffice_data[user_id]["monthly_data"]:
                            st.session_state.homeoffice_data[user_id]["monthly_data"][year_month] = {
                                "days": set(),
                                "hours": 0
                            }
                        
                        st.session_state.homeoffice_data[user_id]["monthly_data"][year_month]["days"].add(date_str)
                        st.session_state.homeoffice_data[user_id]["monthly_data"][year_month]["hours"] += duration_hours
            
            # Gesamtzahl der Homeoffice-Tage aktualisieren
            st.session_state.homeoffice_data[user_id]["total_days"] = len(homeoffice_days)
            
            # Sets in Listen umwandeln für JSON-Serialisierung
            for year_month in st.session_state.homeoffice_data[user_id]["monthly_data"]:
                st.session_state.homeoffice_data[user_id]["monthly_data"][year_month]["days"] = list(
                    st.session_state.homeoffice_data[user_id]["monthly_data"][year_month]["days"]
                )
            
            save_homeoffice_data()
    
    def show_homeoffice_ui():
        st.subheader("Homeoffice-Dokumentation")
        
        # Homeoffice-Statistiken berechnen
        calculate_homeoffice_stats()
        
        # Benutzer-ID abrufen
        user_id = st.session_state.get("user_id")
        if not user_id:
            st.warning("Bitte melden Sie sich an, um Ihre Homeoffice-Daten zu sehen.")
            return
            
        # Homeoffice-Daten anzeigen
        if "homeoffice_data" in st.session_state and user_id in st.session_state.homeoffice_data:
            user_data = st.session_state.homeoffice_data[user_id]
            
            # Gesamtstatistik
            st.write(f"Gesamtzahl Homeoffice-Tage: {user_data['total_days']}")
            st.write(f"Gesamtstunden im Homeoffice: {user_data['total_hours']:.1f}h")
            
            # Monatsstatistik
            st.subheader("Monatsübersicht")
            
            if user_data["monthly_data"]:
                # Sortierte Liste der Monate (neueste zuerst)
                months = sorted(user_data["monthly_data"].keys(), reverse=True)
                
                for month in months:
                    month_data = user_data["monthly_data"][month]
                    month_name = datetime.strptime(month, "%Y-%m").strftime("%B %Y")
                    
                    with st.expander(f"{month_name} ({len(month_data['days'])} Tage, {month_data['hours']:.1f}h)"):
                        # Tage sortieren
                        days = sorted(month_data["days"])
                        
                        # Tage formatieren
                        formatted_days = [datetime.strptime(day, "%Y-%m-%d").strftime("%d.%m.%Y") for day in days]
                        
                        # Als Liste anzeigen
                        for day in formatted_days:
                            st.write(f"- {day}")
            else:
                st.info("Keine Homeoffice-Daten vorhanden.")
            
            # Homeoffice-Bescheinigung
            st.subheader("Homeoffice-Bescheinigung")
            
            # Monat auswählen
            if user_data["monthly_data"]:
                months = sorted(user_data["monthly_data"].keys(), reverse=True)
                selected_month = st.selectbox("Monat auswählen", months, format_func=lambda x: datetime.strptime(x, "%Y-%m").strftime("%B %Y"))
                
                if st.button("Bescheinigung erstellen"):
                    month_data = user_data["monthly_data"][selected_month]
                    month_name = datetime.strptime(selected_month, "%Y-%m").strftime("%B %Y")
                    
                    # Bescheinigung erstellen
                    st.success(f"Homeoffice-Bescheinigung für {month_name} erstellt!")
                    
                    # Bescheinigungstext
                    st.markdown("---")
                    st.markdown(f"## Homeoffice-Bescheinigung")
                    st.markdown(f"**Zeitraum:** {month_name}")
                    st.markdown(f"**Mitarbeiter:** {st.session_state.get('username', 'Unbekannt')}")
                    st.markdown(f"**Anzahl Homeoffice-Tage:** {len(month_data['days'])}")
                    st.markdown(f"**Gesamtstunden im Homeoffice:** {month_data['hours']:.1f}h")
                    
                    st.markdown("**Homeoffice-Tage:**")
                    days = sorted(month_data["days"])
                    formatted_days = [datetime.strptime(day, "%Y-%m-%d").strftime("%d.%m.%Y") for day in days]
                    for day in formatted_days:
                        st.markdown(f"- {day}")
                    
                    st.markdown("---")
                    st.markdown("Diese Bescheinigung wurde automatisch erstellt und ist ohne Unterschrift gültig.")
            else:
                st.info("Keine Daten für eine Bescheinigung vorhanden.")
    
    return show_homeoffice_ui

def implement_reporting_and_analytics():
    """
    Implementiert verbesserte Auswertungsmöglichkeiten
    Inspiriert von ZEP und TimeTac
    """
    def show_reporting_ui():
        st.subheader("Auswertungen und Berichte")
        
        # Prüfen, ob Zeiteinträge vorhanden sind
        if "time_entries" not in st.session_state or not st.session_state.time_entries:
            st.info("Keine Zeiteinträge für Auswertungen vorhanden.")
            return
            
        # Benutzer-ID abrufen
        user_id = st.session_state.get("user_id")
        
        # Tabs für verschiedene Auswertungen
        tab1, tab2, tab3 = st.tabs(["Zeitauswertung", "Projektauswertung", "Exportieren"])
        
        with tab1:
            st.subheader("Zeitauswertung")
            
            # Zeitraum auswählen
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Startdatum", value=datetime.now() - timedelta(days=30))
            with col2:
                end_date = st.date_input("Enddatum", value=datetime.now())
                
            # Zeiteinträge filtern
            filtered_entries = [
                entry for entry in st.session_state.time_entries
                if entry.get("user_id") == user_id
                and datetime.strptime(entry.get("start_time", ""), "%Y-%m-%d %H:%M:%S").date() >= start_date
                and datetime.strptime(entry.get("start_time", ""), "%Y-%m-%d %H:%M:%S").date() <= end_date
            ]
            
            if not filtered_entries:
                st.info("Keine Zeiteinträge im ausgewählten Zeitraum.")
                return
                
            # Gesamtstunden berechnen
            total_seconds = sum(entry.get("duration_seconds", 0) for entry in filtered_entries)
            total_hours = total_seconds / 3600
            
            st.write(f"Gesamtstunden im Zeitraum: {total_hours:.1f}h")
            
            # Stunden pro Tag berechnen
            days_data = {}
            for entry in filtered_entries:
                date_str = entry.get("start_time", "").split()[0]
                if date_str:
                    if date_str not in days_data:
                        days_data[date_str] = 0
                    days_data[date_str] += entry.get("duration_seconds", 0) / 3600
            
            # Tage sortieren
            sorted_days = sorted(days_data.keys())
            
            # Diagramm anzeigen
            if sorted_days:
                st.subheader("Stunden pro Tag")
                
                # Daten für das Diagramm vorbereiten
                chart_data = {
                    "Datum": sorted_days,
                    "Stunden": [days_data[day] for day in sorted_days]
                }
                
                # Diagramm anzeigen
                st.bar_chart(chart_data, x="Datum", y="Stunden")
            
            # Homeoffice vs. Büro
            homeoffice_hours = sum(entry.get("duration_seconds", 0) / 3600 
                                 for entry in filtered_entries if entry.get("homeoffice", False))
            office_hours = total_hours - homeoffice_hours
            
            st.subheader("Homeoffice vs. Büro")
            st.write(f"Homeoffice: {homeoffice_hours:.1f}h ({homeoffice_hours/total_hours*100:.1f}%)")
            st.write(f"Büro: {office_hours:.1f}h ({office_hours/total_hours*100:.1f}%)")
        
        with tab2:
            st.subheader("Projektauswertung")
            
            # Zeiteinträge nach Projekten gruppieren
            project_data = {}
            for entry in filtered_entries:
                project = entry.get("project", "Unbekannt")
                if project not in project_data:
                    project_data[project] = 0
                project_data[project] += entry.get("duration_seconds", 0) / 3600
            
            # Projekte nach Stunden sortieren (absteigend)
            sorted_projects = sorted(project_data.keys(), key=lambda x: project_data[x], reverse=True)
            
            # Diagramm anzeigen
            if sorted_projects:
                st.subheader("Stunden pro Projekt")
                
                # Daten für das Diagramm vorbereiten
                chart_data = {
                    "Projekt": sorted_projects,
                    "Stunden": [project_data[project] for project in sorted_projects]
                }
                
                # Diagramm anzeigen
                st.bar_chart(chart_data, x="Projekt", y="Stunden")
                
                # Detaillierte Projektdaten anzeigen
                for project in sorted_projects:
                    with st.expander(f"{project}: {project_data[project]:.1f}h"):
                        # Einträge für dieses Projekt
                        project_entries = [entry for entry in filtered_entries if entry.get("project") == project]
                        
                        # Nach Datum sortieren
                        project_entries.sort(key=lambda x: x.get("start_time", ""), reverse=True)
                        
                        # Einträge anzeigen
                        for entry in project_entries:
                            st.write(f"- {entry.get('start_time')}: {entry.get('duration_formatted')} " +
                                   f"({'Homeoffice' if entry.get('homeoffice', False) else 'Büro'})")
        
        with tab3:
            st.subheader("Daten exportieren")
            
            # Export-Format auswählen
            export_format = st.selectbox("Format", ["CSV", "JSON"])
            
            if st.button("Exportieren"):
                if export_format == "CSV":
                    # CSV-Daten vorbereiten
                    csv_data = "Datum,Startzeit,Endzeit,Dauer,Projekt,Homeoffice\n"
                    for entry in filtered_entries:
                        start_time = entry.get("start_time", "")
                        date = start_time.split()[0] if start_time else ""
                        start = start_time.split()[1] if start_time else ""
                        end = entry.get("end_time", "").split()[1] if entry.get("end_time", "") else ""
                        duration = entry.get("duration_formatted", "")
                        project = entry.get("project", "")
                        homeoffice = "Ja" if entry.get("homeoffice", False) else "Nein"
                        
                        csv_data += f"{date},{start},{end},{duration},{project},{homeoffice}\n"
                    
                    # CSV-Datei erstellen
                    data_dir = "data"
                    if not os.path.exists(data_dir):
                        os.makedirs(data_dir)
                        
                    file_path = os.path.join(data_dir, "zeiterfassung_export.csv")
                    
                    with open(file_path, "w") as f:
                        f.write(csv_data)
                    
                    st.success(f"Daten als CSV exportiert: {file_path}")
                    
                elif export_format == "JSON":
                    # JSON-Daten vorbereiten
                    json_data = filtered_entries
                    
                    # JSON-Datei erstellen
                    data_dir = "data"
                    if not os.path.exists(data_dir):
                        os.makedirs(data_dir)
                        
                    file_path = os.path.join(data_dir, "zeiterfassung_export.json")
                    
                    with open(file_path, "w") as f:
                        json.dump(json_data, f, indent=2)
                    
                    st.success(f"Daten als JSON exportiert: {file_path}")
    
    return show_reporting_ui

def integrate_time_tracking_improvements(app_with_persistence):
    """
    Integriert alle Zeiterfassungsverbesserungen in die App
    """
    # Importiere die App mit persistenter Datenspeicherung
    from app_with_persistence import show_main_page, show_login_page, show_register_page
    
    # Implementiere die Verbesserungen
    stopwatch_ui = implement_stopwatch_functionality()
    project_management_ui = implement_project_time_tracking()
    homeoffice_ui = implement_homeoffice_tracking()
    reporting_ui = implement_reporting_and_analytics()
    
    # Erweitere die Hauptseite um die neuen Funktionen
    def show_enhanced_main_page():
        st.sidebar.title("Navigation")
        page = st.sidebar.radio(
            "Seite auswählen",
            ["Dashboard", "Zeiterfassung", "Projekte", "Homeoffice", "Auswertungen", "Mitarbeiter", "Profil"]
        )
        
        if page == "Dashboard":
            show_main_page()
        elif page == "Zeiterfassung":
            stopwatch_ui()
        elif page == "Projekte":
            project_management_ui()
        elif page == "Homeoffice":
            homeoffice_ui()
        elif page == "Auswertungen":
            reporting_ui()
        elif page == "Mitarbeiter":
            if st.session_state.get("is_admin", False):
                show_employees_page()
            else:
                st.warning("Sie haben keine Berechtigung, diese Seite zu sehen.")
        elif page == "Profil":
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
            # Hauptseite mit erweiterten Funktionen anzeigen
            show_enhanced_main_page()
    
    return main

# Exportiere die Funktionen
__all__ = [
    'implement_stopwatch_functionality',
    'implement_project_time_tracking',
    'implement_homeoffice_tracking',
    'implement_reporting_and_analytics',
    'integrate_time_tracking_improvements'
]
