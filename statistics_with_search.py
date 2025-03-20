import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go

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
            
            # Nach Datum filtern
            filtered_entries = [
                entry for entry in filtered_entries
                if entry.get("start_time") and datetime.strptime(entry.get("start_time"), "%Y-%m-%d %H:%M:%S").date() >= start_date
                and datetime.strptime(entry.get("start_time"), "%Y-%m-%d %H:%M:%S").date() <= end_date
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
                    
                    # Datum extrahieren
                    start_time = datetime.strptime(entry.get("start_time"), "%Y-%m-%d %H:%M:%S")
                    date_str = start_time.strftime("%Y-%m-%d")
                    
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
                    total_hours = sum(entry.get("duration_seconds", 0) for entry in project_entries) / 3600
                    
                    # Mitarbeiter zählen
                    unique_employees = set(entry.get("user_id") for entry in project_entries)
                    
                    project_data.append({
                        "ID": project["id"],
                        "Name": project["name"],
                        "Beschreibung": project["description"],
                        "Budget (Std)": project["budget_hours"],
                        "Verbrauchte Std": round(total_hours, 2),
                        "Verbleibende Std": round(project["budget_hours"] - total_hours, 2),
                        "Fortschritt (%)": round((total_hours / project["budget_hours"]) * 100, 1) if project["budget_hours"] > 0 else 0,
                        "Beteiligte Mitarbeiter": len(unique_employees)
                    })
                
                # DataFrame erstellen
                project_df = pd.DataFrame(project_data)
                
                # Suchfunktion
                search_term = st.text_input("Projekt suchen", "")
                if search_term:
                    project_df = project_df[project_df["Name"].str.contains(search_term, case=False) | 
                                           project_df["Beschreibung"].str.contains(search_term, case=False)]
                
                # Tabelle anzeigen
                st.dataframe(project_df, use_container_width=True)
                
                # Diagramme
                st.subheader("Projektfortschritt")
                
                # Fortschrittsbalken für jedes Projekt
                for _, project in project_df.iterrows():
                    progress_pct = min(project["Fortschritt (%)"], 100) / 100
                    st.write(f"**{project['Name']}**")
                    
                    # Farbgebung basierend auf Fortschritt
                    color = "green"
                    if progress_pct > 0.9:
                        color = "red"
                    elif progress_pct > 0.7:
                        color = "orange"
                    
                    st.progress(progress_pct)
                    st.write(f"{project['Verbrauchte Std']} von {project['Budget (Std)']} Stunden ({project['Fortschritt (%)']}%)")
                
                # Gesamtübersicht als Diagramm
                st.subheader("Projektübersicht")
                
                fig = px.bar(
                    project_df,
                    x="Name",
                    y=["Verbrauchte Std", "Verbleibende Std"],
                    title="Projektbudget und -verbrauch",
                    labels={"value": "Stunden", "Name": "Projekt", "variable": "Kategorie"},
                    barmode="stack"
                )
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Keine Projektdaten gefunden.")
        
        elif selected_tab == "Mitarbeiterübersicht" and is_admin:
            st.subheader("Mitarbeiterübersicht")
            
            # Mitarbeiterdaten
            employees = data["employees"]
            
            if employees:
                # Mitarbeiterdaten für Tabelle vorbereiten
                employee_data = []
                for emp in employees:
                    # Zeiteinträge für diesen Mitarbeiter finden
                    emp_entries = [
                        entry for entry in data["time_entries"]
                        if entry.get("user_id") == emp["id"]
                    ]
                    
                    # Gesamtstunden berechnen
                    total_hours = sum(entry.get("duration_seconds", 0) for entry in emp_entries) / 3600
                    
                    # Urlaubsdaten
                    vacation_data = data["leave_data"].get("vacation", {}).get(str(emp["id"]), {})
                    total_vacation_days = vacation_data.get("total_days", 30)
                    used_vacation_days = vacation_data.get("used_days", 0)
                    
                    # Krankmeldungen
                    sick_leaves = data["leave_data"].get("sick_leave", {}).get(str(emp["id"]), [])
                    sick_days = sum(leave.get("days", 0) for leave in sick_leaves)
                    
                    employee_data.append({
                        "ID": emp["id"],
                        "Name": emp["name"],
                        "Benutzername": emp["username"],
                        "Status": emp.get("status", "Abwesend"),
                        "Admin": "Ja" if emp.get("is_admin", False) else "Nein",
                        "Arbeitszeitmodell": emp.get("work_time_model", "vollzeit"),
                        "Gesamtstunden": round(total_hours, 2),
                        "Urlaubstage (verbleibend)": total_vacation_days - used_vacation_days,
                        "Krankheitstage": sick_days
                    })
                
                # DataFrame erstellen
                employee_df = pd.DataFrame(employee_data)
                
                # Suchfunktion
                search_term = st.text_input("Mitarbeiter suchen", "")
                if search_term:
                    employee_df = employee_df[employee_df["Name"].str.contains(search_term, case=False) | 
                                             employee_df["Benutzername"].str.contains(search_term, case=False)]
                
                # Tabelle anzeigen
                st.dataframe(employee_df, use_container_width=True)
                
                # Diagramme
                st.subheader("Mitarbeitervisualisierungen")
                
                # Diagrammtyp auswählen
                chart_type = st.selectbox("Diagrammtyp", ["Arbeitsstunden pro Mitarbeiter", "Urlaubstage", "Krankheitstage"])
                
                if chart_type == "Arbeitsstunden pro Mitarbeiter":
                    # Arbeitsstunden pro Mitarbeiter
                    fig = px.bar(
                        employee_df,
                        x="Name",
                        y="Gesamtstunden",
                        title="Arbeitsstunden pro Mitarbeiter",
                        labels={"Gesamtstunden": "Stunden", "Name": "Mitarbeiter"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                elif chart_type == "Urlaubstage":
                    # Urlaubstage
                    fig = px.bar(
                        employee_df,
                        x="Name",
                        y="Urlaubstage (verbleibend)",
                        title="Verbleibende Urlaubstage pro Mitarbeiter",
                        labels={"Urlaubstage (verbleibend)": "Tage", "Name": "Mitarbeiter"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
                
                elif chart_type == "Krankheitstage":
                    # Krankheitstage
                    fig = px.bar(
                        employee_df,
                        x="Name",
                        y="Krankheitstage",
                        title="Krankheitstage pro Mitarbeiter",
                        labels={"Krankheitstage": "Tage", "Name": "Mitarbeiter"}
                    )
                    st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("Keine Mitarbeiterdaten gefunden.")
        
        elif selected_tab == "Urlaub & Krankheit" and is_admin:
            st.subheader("Urlaubs- und Krankheitsstatistik")
            
            # Urlaubsdaten
            vacation_data = data["leave_data"].get("vacation", {})
            sick_leave_data = data["leave_data"].get("sick_leave", {})
            
            if vacation_data or sick_leave_data:
                # Urlaubsanträge sammeln
                vacation_entries = []
                for user_id, user_vacation in vacation_data.items():
                    # Mitarbeitername finden
                    employee_name = "Unbekannt"
                    for emp in data["employees"]:
                        if str(emp["id"]) == user_id:
                            employee_name = emp["name"]
                            break
                    
                    # Genehmigte Anträge
                    for request in user_vacation.get("approved_requests", []):
                        vacation_entries.append({
                            "Mitarbeiter": employee_name,
                            "Typ": "Urlaub",
                            "Startdatum": request.get("start_date", ""),
                            "Enddatum": request.get("end_date", ""),
                            "Tage": request.get("days", 0),
                            "Status": "Genehmigt"
                        })
                    
                    # Ausstehende Anträge
                    for request in user_vacation.get("pending_requests", []):
                        vacation_entries.append({
                            "Mitarbeiter": employee_name,
                            "Typ": "Urlaub",
                            "Startdatum": request.get("start_date", ""),
                            "Enddatum": request.get("end_date", ""),
                            "Tage": request.get("days", 0),
                            "Status": "Ausstehend"
                        })
                
                # Krankmeldungen sammeln
                sick_entries = []
                for user_id, sick_leaves in sick_leave_data.items():
                    # Mitarbeitername finden
                    employee_name = "Unbekannt"
                    for emp in data["employees"]:
                        if str(emp["id"]) == user_id:
                            employee_name = emp["name"]
                            break
                    
                    for sick_leave in sick_leaves:
                        sick_entries.append({
                            "Mitarbeiter": employee_name,
                            "Typ": "Krankheit",
                            "Startdatum": sick_leave.get("start_date", ""),
                            "Enddatum": sick_leave.get("end_date", ""),
                            "Tage": sick_leave.get("days", 0),
                            "Status": "Gemeldet"
                        })
                
                # Alle Einträge kombinieren
                all_entries = vacation_entries + sick_entries
                
                if all_entries:
                    # DataFrame erstellen
                    df = pd.DataFrame(all_entries)
                    
                    # Suchfunktion
                    search_term = st.text_input("Suchen (Mitarbeiter, Datum, etc.)", "")
                    if search_term:
                        df = df[df.apply(lambda row: any(search_term.lower() in str(val).lower() for val in row), axis=1)]
                    
                    # Tabelle anzeigen
                    st.dataframe(df, use_container_width=True)
                    
                    # Zusammenfassung
                    st.subheader("Zusammenfassung")
                    
                    col1, col2, col3 = st.columns(3)
                    with col1:
                        total_vacation_days = sum(entry["Tage"] for entry in vacation_entries if entry["Status"] == "Genehmigt")
                        st.metric("Genehmigte Urlaubstage", total_vacation_days)
                    with col2:
                        pending_vacation_days = sum(entry["Tage"] for entry in vacation_entries if entry["Status"] == "Ausstehend")
                        st.metric("Ausstehende Urlaubstage", pending_vacation_days)
                    with col3:
                        total_sick_days = sum(entry["Tage"] for entry in sick_entries)
                        st.metric("Krankheitstage", total_sick_days)
                    
                    # Diagramme
                    st.subheader("Visualisierungen")
                    
                    # Diagrammtyp auswählen
                    chart_type = st.selectbox("Diagrammtyp", ["Urlaub vs. Krankheit", "Tage pro Mitarbeiter", "Zeitliche Verteilung"])
                    
                    if chart_type == "Urlaub vs. Krankheit":
                        # Urlaub vs. Krankheit
                        type_summary = df.groupby("Typ")["Tage"].sum().reset_index()
                        
                        fig = px.pie(
                            type_summary,
                            values="Tage",
                            names="Typ",
                            title="Verteilung: Urlaub vs. Krankheit"
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif chart_type == "Tage pro Mitarbeiter":
                        # Tage pro Mitarbeiter und Typ
                        employee_summary = df.groupby(["Mitarbeiter", "Typ"])["Tage"].sum().reset_index()
                        
                        fig = px.bar(
                            employee_summary,
                            x="Mitarbeiter",
                            y="Tage",
                            color="Typ",
                            title="Urlaubs- und Krankheitstage pro Mitarbeiter",
                            labels={"Tage": "Anzahl Tage", "Mitarbeiter": "Mitarbeiter"}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                    
                    elif chart_type == "Zeitliche Verteilung":
                        # Zeitliche Verteilung (vereinfacht)
                        # Hier könnte man eine komplexere Analyse mit tatsächlichen Kalendertagen machen
                        
                        # Wir verwenden hier nur die Startdaten als Annäherung
                        df["Monat"] = df["Startdatum"].apply(lambda x: x.split("-")[1] if isinstance(x, str) and len(x.split("-")) > 1 else "")
                        
                        month_mapping = {
                            "01": "Januar", "02": "Februar", "03": "März", "04": "April",
                            "05": "Mai", "06": "Juni", "07": "Juli", "08": "August",
                            "09": "September", "10": "Oktober", "11": "November", "12": "Dezember"
                        }
                        
                        df["Monat"] = df["Monat"].map(lambda x: month_mapping.get(x, x))
                        
                        # Nach Monat gruppieren
                        month_summary = df.groupby(["Monat", "Typ"])["Tage"].sum().reset_index()
                        
                        # Nur Einträge mit gültigen Monaten
                        month_summary = month_summary[month_summary["Monat"].isin(month_mapping.values())]
                        
                        # Sortieren nach Monatsreihenfolge
                        month_order = list(month_mapping.values())
                        month_summary["Monat_Sortierung"] = month_summary["Monat"].apply(lambda x: month_order.index(x) if x in month_order else -1)
                        month_summary = month_summary.sort_values("Monat_Sortierung")
                        
                        fig = px.line(
                            month_summary,
                            x="Monat",
                            y="Tage",
                            color="Typ",
                            title="Zeitliche Verteilung von Urlaub und Krankheit",
                            labels={"Tage": "Anzahl Tage", "Monat": "Monat"}
                        )
                        st.plotly_chart(fig, use_container_width=True)
                else:
                    st.info("Keine Urlaubs- oder Krankheitsdaten gefunden.")
            else:
                st.info("Keine Urlaubs- oder Krankheitsdaten gefunden.")
    
    # Rückgabe der UI-Funktion
    return show_statistics_ui

# Exportiere die Funktionen
__all__ = ['implement_statistics_with_search']
