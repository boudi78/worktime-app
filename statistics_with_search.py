import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
import sys
sys.path.append('/home/ubuntu')
from datetime_utils import parse_datetime_string

def implement_statistics_with_search():
    """
    Implementiert eine Statistik-Tabelle mit Suchfunktion
    """
    def load_data_for_statistics():
        """Lädt alle relevanten Daten für die Statistiken"""
        data_dir = "data"
        data = {}
        
        # Mitarbeiterdaten laden
        employees_path = os.path.join(data_dir, "employees.json")
        if os.path.exists(employees_path):
            with open(employees_path, "r") as f:
                data["employees"] = json.load(f)
        else:
            data["employees"] = []
        
        # Zeiteinträge laden
        time_entries_path = os.path.join(data_dir, "time_entries.json")
        if os.path.exists(time_entries_path):
            with open(time_entries_path, "r") as f:
                data["time_entries"] = json.load(f)
        else:
            data["time_entries"] = []
        
        # Projekte laden
        projects_path = os.path.join(data_dir, "projects.json")
        if os.path.exists(projects_path):
            with open(projects_path, "r") as f:
                data["projects"] = json.load(f)
        else:
            data["projects"] = []
        
        # Urlaubs- und Krankheitsdaten laden
        leave_data_path = os.path.join(data_dir, "leave_data.json")
        if os.path.exists(leave_data_path):
            with open(leave_data_path, "r") as f:
                data["leave_data"] = json.load(f)
        else:
            data["leave_data"] = {"vacation": {}, "sick_leave": {}}
        
        return data
    
    def show_statistics_ui():
        st.title("Statistiken und Auswertungen")
        
        # Prüfen, ob der Benutzer angemeldet ist
        if not st.session_state.get("logged_in", False):
            st.warning("Bitte melden Sie sich an, um diese Funktion zu nutzen.")
            return
        
        # Daten laden
        data = load_data_for_statistics()
        
        # Benutzer-ID
        user_id = st.session_state.get("user_id")
        is_admin = st.session_state.get("is_admin", False)
        
        # Tabs für verschiedene Statistiken
        tabs = ["Arbeitszeit", "Projekte"]
        
        if is_admin:
            tabs.extend(["Mitarbeiterübersicht", "Urlaub & Krankheit"])
        
        selected_tab = st.selectbox("Statistik-Kategorie auswählen", tabs)
        
        if selected_tab == "Arbeitszeit":
            st.subheader("Arbeitszeitstatistik")
            
            # Zeitraum auswählen
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Startdatum", value=datetime.now() - timedelta(days=30))
            with col2:
                end_date = st.date_input("Enddatum", value=datetime.now())
            
            # Zeiteinträge filtern
            if is_admin:
                # Admin kann alle oder bestimmte Mitarbeiter auswählen
                employee_names = ["Alle Mitarbeiter"]
                employee_ids = ["all"]
                
                for emp in data["employees"]:
                    employee_names.append(emp["name"])
                    employee_ids.append(emp["id"])
                
                selected_index = st.selectbox("Mitarbeiter auswählen", range(len(employee_names)), format_func=lambda x: employee_names[x])
                selected_employee_id = employee_ids[selected_index]
                
                if selected_employee_id == "all":
                    filtered_entries = data["time_entries"]
                else:
                    filtered_entries = [entry for entry in data["time_entries"] if entry.get("user_id") == selected_employee_id]
            else:
                # Normale Benutzer sehen nur ihre eigenen Einträge
                filtered_entries = [entry for entry in data["time_entries"] if entry.get("user_id") == user_id]
            
            # Nach Datum filtern - FIXED to handle both datetime formats
            filtered_entries = [
                entry for entry in filtered_entries
                if entry.get("start_time") and parse_datetime_string(entry.get("start_time")).date() >= start_date
                and parse_datetime_string(entry.get("start_time")).date() <= end_date
            ]
            
            # Suchfunktion
            search_term = st.text_input("Suche (Projekt, Datum, etc.)", "")
            if search_term:
                filtered_entries = [
                    entry for entry in filtered_entries
                    if search_term.lower() in str(entry).lower()
                ]
            
            # Daten für Statistik vorbereiten
            if filtered_entries:
                # Tabellendaten
                table_data = []
                for entry in filtered_entries:
                    # Mitarbeitername finden
                    employee_name = "Unbekannt"
                    for emp in data["employees"]:
                        if emp["id"] == entry.get("user_id"):
                            employee_name = emp["name"]
                            break
                    
                    # Datum extrahieren - FIXED to handle both datetime formats
                    start_time = parse_datetime_string(entry.get("start_time"))
                    date_str = start_time.strftime("%Y-%m-%d") if start_time else ""
                    
                    table_data.append({
                        "Datum": date_str,
                        "Mitarbeiter": employee_name,
                        "Startzeit": entry.get("start_time", ""),
                        "Endzeit": entry.get("end_time", ""),
                        "Dauer": entry.get("duration_formatted", ""),
                        "Dauer (Std)": round(entry.get("duration_seconds", 0) / 3600, 2),
                        "Projekt": entry.get("project", ""),
                        "Homeoffice": "Ja" if entry.get("homeoffice", False) else "Nein"
                    })
                
                # DataFrame erstellen
                df = pd.DataFrame(table_data)
                
                # Tabelle anzeigen
                st.subheader("Detaillierte Zeiteinträge")
                st.dataframe(df, use_container_width=True)
                
                # Zusammenfassung
                st.subheader("Zusammenfassung")
                total_hours = df["Dauer (Std)"].sum()
                avg_hours_per_day = total_hours / len(df["Datum"].unique()) if len(df["Datum"].unique()) > 0 else 0
                
                col1, col2, col3 = st.columns(3)
                with col1:
                    st.metric("Gesamtstunden", f"{total_hours:.2f} h")
                with col2:
                    st.metric("Einträge", len(df))
                with col3:
                    st.metric("Durchschnitt pro Tag", f"{avg_hours_per_day:.2f} h")
                
                # Diagramme
                st.subheader("Visualisierungen")
                
                # Diagrammtyp auswählen
                chart_type = st.selectbox("Diagrammtyp", ["Arbeitszeit pro Tag", "Arbeitszeit pro Projekt", "Homeoffice vs. Büro"])
                
                if chart_type == "Arbeitszeit pro Tag":
                    # Arbeitszeit pro Tag
                    daily_hours = df.groupby("Datum")["Dauer (Std)"].sum().reset_index()
                    
                    fig = px.bar(
                        daily_hours, 
                        x="Datum", 
                        y="Dauer (Std)",
                        title="Arbeitszeit pro Tag",
                        labels={"Dauer (Std)": "Stunden", "Datum": "Datum"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                elif chart_type == "Arbeitszeit pro Projekt":
                    # Arbeitszeit pro Projekt
                    project_hours = df.groupby("Projekt")["Dauer (Std)"].sum().reset_index()
                    
                    fig = px.pie(
                        project_hours, 
                        values="Dauer (Std)", 
                        names="Projekt",
                        title="Arbeitszeit pro Projekt"
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                elif chart_type == "Homeoffice vs. Büro":
                    # Homeoffice vs. Büro
                    homeoffice_hours = df.groupby("Homeoffice")["Dauer (Std)"].sum().reset_index()
                    
                    fig = px.pie(
                        homeoffice_hours, 
                        values="Dauer (Std)", 
                        names="Homeoffice",
                        title="Homeoffice vs. Büro"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Keine Zeiteinträge im ausgewählten Zeitraum gefunden.")
        
        elif selected_tab == "Projekte":
            st.subheader("Projektstatistik")
            
            # Projekte laden
            projects = data["projects"]
            
            if projects:
                # Projektdaten für Tabelle vorbereiten
                project_data = []
                for project in projects:
                    # Zeiteinträge für dieses Projekt finden
                    project_entries = [
                        entry for entry in data["time_entries"]
                        if entry.get("project") == project["name"]
                    ]
                    
                    # Gesamtstunden berechnen
                    total_hours = sum(entry.get("duration_seconds", 0) / 3600 for entry in project_entries)
                    
                    project_data.append({
                        "Projekt": project["name"],
                        "Beschreibung": project["description"],
                        "Budget (Std)": project["budget_hours"],
                        "Verbrauchte Zeit (Std)": round(total_hours, 2),
                        "Verbleibend (Std)": round(project["budget_hours"] - total_hours, 2) if project["budget_hours"] > 0 else "Unbegrenzt",
                        "Auslastung (%)": round((total_hours / project["budget_hours"]) * 100, 2) if project["budget_hours"] > 0 else 0
                    })
                
                # DataFrame erstellen
                df = pd.DataFrame(project_data)
                
                # Tabelle anzeigen
                st.subheader("Projektübersicht")
                st.dataframe(df, use_container_width=True)
                
                # Diagramme
                st.subheader("Visualisierungen")
                
                # Diagrammtyp auswählen
                chart_type = st.selectbox("Diagrammtyp", ["Projektauslastung", "Verbrauchte Zeit pro Projekt"])
                
                if chart_type == "Projektauslastung":
                    # Projektauslastung
                    fig = px.bar(
                        df, 
                        x="Projekt", 
                        y="Auslastung (%)",
                        title="Projektauslastung",
                        labels={"Auslastung (%)": "Auslastung (%)", "Projekt": "Projekt"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                elif chart_type == "Verbrauchte Zeit pro Projekt":
                    # Verbrauchte Zeit pro Projekt
                    fig = px.pie(
                        df, 
                        values="Verbrauchte Zeit (Std)", 
                        names="Projekt",
                        title="Verbrauchte Zeit pro Projekt"
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Keine Projekte gefunden.")
        
        elif selected_tab == "Mitarbeiterübersicht" and is_admin:
            st.subheader("Mitarbeiterübersicht")
            
            # Mitarbeiterdaten für Tabelle vorbereiten
            employee_data = []
            for emp in data["employees"]:
                # Zeiteinträge für diesen Mitarbeiter finden
                employee_entries = [
                    entry for entry in data["time_entries"]
                    if entry.get("user_id") == emp["id"]
                ]
                
                # Gesamtstunden berechnen
                total_hours = sum(entry.get("duration_seconds", 0) / 3600 for entry in employee_entries)
                
                # Letzte Aktivität finden
                last_activity = None
                for entry in employee_entries:
                    entry_time = parse_datetime_string(entry.get("start_time"))
                    if entry_time and (last_activity is None or entry_time > last_activity):
                        last_activity = entry_time
                
                employee_data.append({
                    "Name": emp["name"],
                    "Status": emp.get("status", "Unbekannt"),
                    "Team": emp.get("team", ""),
                    "Arbeitszeitmodell": emp.get("work_time_model", "vollzeit"),
                    "Gesamtstunden": round(total_hours, 2),
                    "Letzte Aktivität": last_activity.strftime("%Y-%m-%d %H:%M") if last_activity else "Keine"
                })
            
            # DataFrame erstellen
            df = pd.DataFrame(employee_data)
            
            # Tabelle anzeigen
            st.subheader("Mitarbeiterübersicht")
            st.dataframe(df, use_container_width=True)
            
            # Diagramme
            st.subheader("Visualisierungen")
            
            # Diagrammtyp auswählen
            chart_type = st.selectbox("Diagrammtyp", ["Arbeitsstunden pro Mitarbeiter", "Mitarbeiter pro Team", "Arbeitszeitmodelle"])
            
            if chart_type == "Arbeitsstunden pro Mitarbeiter":
                # Arbeitsstunden pro Mitarbeiter
                fig = px.bar(
                    df, 
                    x="Name", 
                    y="Gesamtstunden",
                    title="Arbeitsstunden pro Mitarbeiter",
                    labels={"Gesamtstunden": "Stunden", "Name": "Mitarbeiter"}
                )
                st.plotly_chart(fig, use_container_width=True)
            
            elif chart_type == "Mitarbeiter pro Team":
                # Mitarbeiter pro Team
                team_counts = df["Team"].value_counts().reset_index()
                team_counts.columns = ["Team", "Anzahl"]
                
                fig = px.pie(
                    team_counts, 
                    values="Anzahl", 
                    names="Team",
                    title="Mitarbeiter pro Team"
                )
                st.plotly_chart(fig, use_container_width=True)
            
            elif chart_type == "Arbeitszeitmodelle":
                # Arbeitszeitmodelle
                model_counts = df["Arbeitszeitmodell"].value_counts().reset_index()
                model_counts.columns = ["Modell", "Anzahl"]
                
                fig = px.pie(
                    model_counts, 
                    values="Anzahl", 
                    names="Modell",
                    title="Verteilung der Arbeitszeitmodelle"
                )
                st.plotly_chart(fig, use_container_width=True)
        
        elif selected_tab == "Urlaub & Krankheit" and is_admin:
            st.subheader("Urlaub & Krankheit")
            
            # Urlaubs- und Krankheitsdaten laden
            leave_data = data["leave_data"]
            
            # Tabs für Urlaub und Krankheit
            leave_tabs = ["Urlaub", "Krankheit"]
            selected_leave_tab = st.selectbox("Kategorie auswählen", leave_tabs)
            
            if selected_leave_tab == "Urlaub":
                st.subheader("Urlaubsübersicht")
                
                # Urlaubsdaten für Tabelle vorbereiten
                vacation_data = []
                for emp_id, vacation_info in leave_data.get("vacation", {}).items():
                    # Mitarbeitername finden
                    employee_name = "Unbekannt"
                    for emp in data["employees"]:
                        if str(emp["id"]) == str(emp_id):
                            employee_name = emp["name"]
                            break
                    
                    for vacation in vacation_info.get("entries", []):
                        vacation_data.append({
                            "Mitarbeiter": employee_name,
                            "Von": vacation.get("start_date", ""),
                            "Bis": vacation.get("end_date", ""),
                            "Tage": vacation.get("days", 0),
                            "Status": vacation.get("status", "Beantragt")
                        })
                
                if vacation_data:
                    # DataFrame erstellen
                    df = pd.DataFrame(vacation_data)
                    
                    # Tabelle anzeigen
                    st.dataframe(df, use_container_width=True)
                    
                    # Diagramme
                    st.subheader("Visualisierungen")
                    
                    # Urlaubstage pro Mitarbeiter
                    vacation_by_employee = df.groupby("Mitarbeiter")["Tage"].sum().reset_index()
                    
                    fig = px.bar(
                        vacation_by_employee, 
                        x="Mitarbeiter", 
                        y="Tage",
                        title="Urlaubstage pro Mitarbeiter",
                        labels={"Tage": "Tage", "Mitarbeiter": "Mitarbeiter"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Keine Urlaubsdaten gefunden.")
            
            elif selected_leave_tab == "Krankheit":
                st.subheader("Krankheitsübersicht")
                
                # Krankheitsdaten für Tabelle vorbereiten
                sick_leave_data = []
                for emp_id, sick_leave_info in leave_data.get("sick_leave", {}).items():
                    # Mitarbeitername finden
                    employee_name = "Unbekannt"
                    for emp in data["employees"]:
                        if str(emp["id"]) == str(emp_id):
                            employee_name = emp["name"]
                            break
                    
                    for sick_leave in sick_leave_info.get("entries", []):
                        sick_leave_data.append({
                            "Mitarbeiter": employee_name,
                            "Von": sick_leave.get("start_date", ""),
                            "Bis": sick_leave.get("end_date", ""),
                            "Tage": sick_leave.get("days", 0)
                        })
                
                if sick_leave_data:
                    # DataFrame erstellen
                    df = pd.DataFrame(sick_leave_data)
                    
                    # Tabelle anzeigen
                    st.dataframe(df, use_container_width=True)
                    
                    # Diagramme
                    st.subheader("Visualisierungen")
                    
                    # Krankheitstage pro Mitarbeiter
                    sick_leave_by_employee = df.groupby("Mitarbeiter")["Tage"].sum().reset_index()
                    
                    fig = px.bar(
                        sick_leave_by_employee, 
                        x="Mitarbeiter", 
                        y="Tage",
                        title="Krankheitstage pro Mitarbeiter",
                        labels={"Tage": "Tage", "Mitarbeiter": "Mitarbeiter"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Keine Krankheitsdaten gefunden.")
    
    return show_statistics_ui
