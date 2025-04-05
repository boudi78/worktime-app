import streamlit as st
import pandas as pd
import numpy as np
import os
import json
from datetime import datetime, timedelta
import plotly.express as px
import plotly.graph_objects as go
from modules.utils import load_employees, load_time_entries, load_sick_leaves, load_vacation_requests

def show_stats():
    """
    Zeigt Statistiken zu Arbeitszeiten, Überstunden und Abwesenheiten an.
    """
    st.title("📊 Statistiken & Auswertungen")
    
    # Lade Daten
    employees = load_employees()
    time_entries = load_time_entries()
    sick_leaves = load_sick_leaves()
    vacation_requests = load_vacation_requests()
    
    if not employees or not time_entries:
        st.error("Keine Daten verfügbar, um die Statistiken anzuzeigen.")
        return
    
    # Erstelle ein Mapping von Benutzer-IDs zu Namen für einfacheren Zugriff
    user_map = {emp["id"]: emp["name"] for emp in employees}
    
    # Tabs für verschiedene Statistiken
    tab1, tab2, tab3, tab4 = st.tabs(["Arbeitszeit", "Überstunden", "Abwesenheiten", "Mitarbeiterübersicht"])
    
    with tab1:
        show_work_time_stats(time_entries, user_map)
    
    with tab2:
        show_overtime_stats(time_entries, user_map)
    
    with tab3:
        show_absence_stats(sick_leaves, vacation_requests, user_map)
    
    with tab4:
        show_employee_overview(employees, time_entries, sick_leaves, vacation_requests)

def show_work_time_stats(time_entries, user_map):
    """
    Zeigt Statistiken zu Arbeitszeiten an.
    """
    st.subheader("Arbeitszeitanalyse")
    
    # Zeitraum-Filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Startdatum", 
                                  value=datetime.now() - timedelta(days=30),
                                  key="work_time_start_date")
    with col2:
        end_date = st.date_input("Enddatum", 
                                value=datetime.now(),
                                key="work_time_end_date")
    
    # Konvertiere Datumsangaben in Strings für den Vergleich
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    # Filtere Zeiteinträge nach Zeitraum
    filtered_entries = []
    for entry in time_entries:
        try:
            entry_date = entry["check_in"].split(" ")[0]  # Extrahiere nur das Datum
            if start_date_str <= entry_date <= end_date_str:
                filtered_entries.append(entry)
        except (KeyError, IndexError):
            continue
    
    if not filtered_entries:
        st.warning(f"Keine Zeiteinträge im Zeitraum {start_date_str} bis {end_date_str} gefunden.")
        return
    
    # Berechne Arbeitszeit pro Mitarbeiter
    work_time_data = {}
    for entry in filtered_entries:
        user_id = entry.get("user_id")
        if not user_id or user_id not in user_map:
            continue
            
        if user_id not in work_time_data:
            work_time_data[user_id] = {
                "name": user_map[user_id],
                "total_hours": 0,
                "entries_count": 0
            }
        
        # Berechne Stunden aus duration_hours oder check_in/check_out
        hours = 0
        if "duration_hours" in entry and entry["duration_hours"] is not None:
            hours = float(entry["duration_hours"])
        elif "check_in" in entry and "check_out" in entry:
            try:
                check_in = datetime.strptime(entry["check_in"], "%Y-%m-%d %H:%M:%S")
                check_out = datetime.strptime(entry["check_out"], "%Y-%m-%d %H:%M:%S")
                hours = (check_out - check_in).total_seconds() / 3600
            except (ValueError, TypeError):
                hours = 0
        
        work_time_data[user_id]["total_hours"] += hours
        work_time_data[user_id]["entries_count"] += 1
    
    # Erstelle DataFrame für die Anzeige
    if work_time_data:
        df = pd.DataFrame([
            {
                "Mitarbeiter": data["name"],
                "Gesamtarbeitszeit (Std)": round(data["total_hours"], 2),
                "Anzahl Einträge": data["entries_count"],
                "Durchschnitt pro Eintrag (Std)": round(data["total_hours"] / data["entries_count"], 2) if data["entries_count"] > 0 else 0
            }
            for user_id, data in work_time_data.items()
        ])
        
        # Zeige Tabelle
        st.dataframe(df, use_container_width=True)
        
        # Erstelle Balkendiagramm für Gesamtarbeitszeit
        fig = px.bar(
            df, 
            x="Mitarbeiter", 
            y="Gesamtarbeitszeit (Std)",
            title="Gesamtarbeitszeit pro Mitarbeiter",
            color="Gesamtarbeitszeit (Std)",
            color_continuous_scale="Viridis"
        )
        st.plotly_chart(fig, use_container_width=True)
    else:
        st.info("Keine auswertbaren Arbeitszeitdaten gefunden.")

def show_overtime_stats(time_entries, user_map):
    """
    Zeigt Statistiken zu Überstunden an.
    """
    st.subheader("Überstundenanalyse")
    
    # Zeitraum-Filter
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Startdatum", 
                                  value=datetime.now() - timedelta(days=30),
                                  key="overtime_start_date")
    with col2:
        end_date = st.date_input("Enddatum", 
                                value=datetime.now(),
                                key="overtime_end_date")
    
    # Konvertiere Datumsangaben in Strings für den Vergleich
    start_date_str = start_date.strftime("%Y-%m-%d")
    end_date_str = end_date.strftime("%Y-%m-%d")
    
    # Filtere Zeiteinträge nach Zeitraum
    filtered_entries = []
    for entry in time_entries:
        try:
            entry_date = entry["check_in"].split(" ")[0]  # Extrahiere nur das Datum
            if start_date_str <= entry_date <= end_date_str:
                filtered_entries.append(entry)
        except (KeyError, IndexError):
            continue
    
    if not filtered_entries:
        st.warning(f"Keine Zeiteinträge im Zeitraum {start_date_str} bis {end_date_str} gefunden.")
        return
    
    # Berechne Überstunden pro Mitarbeiter
    overtime_data = {}
    for entry in filtered_entries:
        user_id = entry.get("user_id")
        if not user_id or user_id not in user_map:
            continue
            
        if user_id not in overtime_data:
            overtime_data[user_id] = {
                "name": user_map[user_id],
                "overtime_count": 0,
                "regular_count": 0,
                "total_entries": 0
            }
        
        # Prüfe, ob Überstunden vorliegen
        has_overtime = False
        if "overtime" in entry:
            has_overtime = entry["overtime"]
        elif "duration_hours" in entry and entry["duration_hours"] is not None:
            has_overtime = float(entry["duration_hours"]) > 8
        elif "check_in" in entry and "check_out" in entry:
            try:
                check_in = datetime.strptime(entry["check_in"], "%Y-%m-%d %H:%M:%S")
                check_out = datetime.strptime(entry["check_out"], "%Y-%m-%d %H:%M:%S")
                hours = (check_out - check_in).total_seconds() / 3600
                has_overtime = hours > 8
            except (ValueError, TypeError):
                has_overtime = False
        
        if has_overtime:
            overtime_data[user_id]["overtime_count"] += 1
        else:
            overtime_data[user_id]["regular_count"] += 1
            
        overtime_data[user_id]["total_entries"] += 1
    
    # Erstelle DataFrame für die Anzeige
    if overtime_data:
        df = pd.DataFrame([
            {
                "Mitarbeiter": data["name"],
                "Überstunden (Tage)": data["overtime_count"],
                "Reguläre Tage": data["regular_count"],
                "Gesamt Einträge": data["total_entries"],
                "Überstunden (%)": round(data["overtime_count"] / data["total_entries"] * 100, 1) if data["total_entries"] > 0 else 0
            }
            for user_id, data in overtime_data.items()
        ])
        
        # Zeige Tabelle
        st.dataframe(df, use_container_width=True)
        
        # Erstelle Balkendiagramm für Überstunden vs. reguläre Tage
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df["Mitarbeiter"],
            y=df["Überstunden (Tage)"],
            name="Überstunden",
            marker_color="red"
        ))
        fig.add_trace(go.Bar(
            x=df["Mitarbeiter"],
            y=df["Reguläre Tage"],
            name="Reguläre Tage",
            marker_color="green"
        ))
        fig.update_layout(
            title="Überstunden vs. Reguläre Arbeitstage",
            xaxis_title="Mitarbeiter",
            yaxis_title="Anzahl Tage",
            barmode="stack"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Erstelle Kreisdiagramm für Überstundenanteil
        fig2 = px.pie(
            df, 
            values="Überstunden (%)", 
            names="Mitarbeiter",
            title="Anteil der Überstunden pro Mitarbeiter (%)",
            color_discrete_sequence=px.colors.sequential.Viridis
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Keine auswertbaren Überstundendaten gefunden.")

def show_absence_stats(sick_leaves, vacation_requests, user_map):
    """
    Zeigt Statistiken zu Abwesenheiten (Krankheit und Urlaub) an.
    """
    st.subheader("Abwesenheitsanalyse")
    
    # Prüfe, ob Daten vorhanden sind
    if not sick_leaves and not vacation_requests:
        st.warning("Keine Abwesenheitsdaten (Krankheit oder Urlaub) gefunden.")
        return
    
    # Berechne Abwesenheitstage pro Mitarbeiter
    absence_data = {}
    
    # Verarbeite Krankheitsdaten
    for sick_leave in sick_leaves:
        # Bestimme die Benutzer-ID
        user_id = None
        if "user_id" in sick_leave:
            user_id = sick_leave["user_id"]
        elif "employee" in sick_leave and sick_leave["employee"] in user_map.values():
            # Finde die ID anhand des Namens
            for id, name in user_map.items():
                if name == sick_leave["employee"]:
                    user_id = id
                    break
        
        if not user_id or user_id not in user_map:
            continue
            
        if user_id not in absence_data:
            absence_data[user_id] = {
                "name": user_map[user_id],
                "sick_days": 0,
                "vacation_days": 0
            }
        
        # Berechne Krankheitstage
        try:
            # Bestimme Start- und Enddatum
            start_key = "start_date" if "start_date" in sick_leave else "date"
            end_key = "end_date" if "end_date" in sick_leave else "end"
            
            if start_key in sick_leave and end_key in sick_leave:
                start_date = datetime.strptime(sick_leave[start_key], "%Y-%m-%d").date()
                end_date = datetime.strptime(sick_leave[end_key], "%Y-%m-%d").date()
                days = (end_date - start_date).days + 1  # +1 um den letzten Tag einzuschließen
                absence_data[user_id]["sick_days"] += days
        except (ValueError, KeyError, TypeError):
            # Wenn Datumsberechnung fehlschlägt, zähle einen Tag
            absence_data[user_id]["sick_days"] += 1
    
    # Verarbeite Urlaubsdaten
    for vacation in vacation_requests:
        # Bestimme die Benutzer-ID
        user_id = None
        if "user_id" in vacation:
            user_id = vacation["user_id"]
        elif "employee" in vacation and vacation["employee"] in user_map.values():
            # Finde die ID anhand des Namens
            for id, name in user_map.items():
                if name == vacation["employee"]:
                    user_id = id
                    break
        
        if not user_id or user_id not in user_map:
            continue
            
        if user_id not in absence_data:
            absence_data[user_id] = {
                "name": user_map[user_id],
                "sick_days": 0,
                "vacation_days": 0
            }
        
        # Prüfe, ob der Urlaub genehmigt wurde
        status = vacation.get("status", "approved")  # Standardmäßig als genehmigt betrachten, wenn kein Status angegeben
        if status != "approved":
            continue
        
        # Berechne Urlaubstage
        try:
            # Bestimme Start- und Enddatum
            start_key = "start_date" if "start_date" in vacation else "date"
            end_key = "end_date" if "end_date" in vacation else "end"
            
            if start_key in vacation and end_key in vacation:
                start_date = datetime.strptime(vacation[start_key], "%Y-%m-%d").date()
                end_date = datetime.strptime(vacation[end_key], "%Y-%m-%d").date()
                days = (end_date - start_date).days + 1  # +1 um den letzten Tag einzuschließen
                absence_data[user_id]["vacation_days"] += days
        except (ValueError, KeyError, TypeError):
            # Wenn Datumsberechnung fehlschlägt, zähle einen Tag
            absence_data[user_id]["vacation_days"] += 1
    
    # Erstelle DataFrame für die Anzeige
    if absence_data:
        df = pd.DataFrame([
            {
                "Mitarbeiter": data["name"],
                "Krankheitstage": data["sick_days"],
                "Urlaubstage": data["vacation_days"],
                "Gesamte Abwesenheit": data["sick_days"] + data["vacation_days"]
            }
            for user_id, data in absence_data.items()
        ])
        
        # Zeige Tabelle
        st.dataframe(df, use_container_width=True)
        
        # Erstelle Balkendiagramm für Abwesenheiten
        fig = go.Figure()
        fig.add_trace(go.Bar(
            x=df["Mitarbeiter"],
            y=df["Krankheitstage"],
            name="Krankheit",
            marker_color="red"
        ))
        fig.add_trace(go.Bar(
            x=df["Mitarbeiter"],
            y=df["Urlaubstage"],
            name="Urlaub",
            marker_color="blue"
        ))
        fig.update_layout(
            title="Abwesenheitstage pro Mitarbeiter",
            xaxis_title="Mitarbeiter",
            yaxis_title="Anzahl Tage",
            barmode="group"
        )
        st.plotly_chart(fig, use_container_width=True)
        
        # Erstelle Kreisdiagramm für Gesamtabwesenheit
        fig2 = px.pie(
            df, 
            values="Gesamte Abwesenheit", 
            names="Mitarbeiter",
            title="Anteil der Gesamtabwesenheit pro Mitarbeiter",
            color_discrete_sequence=px.colors.sequential.Viridis
        )
        st.plotly_chart(fig2, use_container_width=True)
    else:
        st.info("Keine auswertbaren Abwesenheitsdaten gefunden.")

def show_employee_overview(employees, time_entries, sick_leaves, vacation_requests):
    """
    Zeigt eine Übersicht aller Mitarbeiter mit ihren wichtigsten Kennzahlen.
    """
    st.subheader("Mitarbeiterübersicht")
    
    # Erstelle ein Mapping von Benutzer-IDs zu Namen für einfacheren Zugriff
    user_map = {emp["id"]: emp["name"] for emp in employees}
    
    # Initialisiere Daten für jeden Mitarbeiter
    employee_data = {}
    for emp in employees:
        employee_data[emp["id"]] = {
            "name": emp["name"],
            "role": emp.get("role", "Mitarbeiter"),
            "total_hours": 0,
            "overtime_count": 0,
            "sick_days": 0,
            "vacation_days": 0,
            "entries_count": 0
        }
    
    # Verarbeite Zeiteinträge
    for entry in time_entries:
        user_id = entry.get("user_id")
        if not user_id or user_id not in employee_data:
            continue
        
        # Zähle Einträge
        employee_data[user_id]["entries_count"] += 1
        
        # Berechne Stunden
        hours = 0
        if "duration_hours" in entry and entry["duration_hours"] is not None:
            hours = float(entry["duration_hours"])
        elif "check_in" in entry and "check_out" in entry:
            try:
                check_in = datetime.strptime(entry["check_in"], "%Y-%m-%d %H:%M:%S")
                check_out = datetime.strptime(entry["check_out"], "%Y-%m-%d %H:%M:%S")
                hours = (check_out - check_in).total_seconds() / 3600
            except (ValueError, TypeError):
                hours = 0
        
        employee_data[user_id]["total_hours"] += hours
        
        # Prüfe Überstunden
        has_overtime = False
        if "overtime" in entry:
            has_overtime = entry["overtime"]
        elif hours > 8:
            has_overtime = True
            
        if has_overtime:
            employee_data[user_id]["overtime_count"] += 1
    
    # Verarbeite Krankheitsdaten
    for sick_leave in sick_leaves:
        # Bestimme die Benutzer-ID
        user_id = None
        if "user_id" in sick_leave:
            user_id = sick_leave["user_id"]
        elif "employee" in sick_leave and sick_leave["employee"] in user_map.values():
            # Finde die ID anhand des Namens
            for id, name in user_map.items():
                if name == sick_leave["employee"]:
                    user_id = id
                    break
        
        if not user_id or user_id not in employee_data:
            continue
        
        # Berechne Krankheitstage
        try:
            # Bestimme Start- und Enddatum
            start_key = "start_date" if "start_date" in sick_leave else "date"
            end_key = "end_date" if "end_date" in sick_leave else "end"
            
            if start_key in sick_leave and end_key in sick_leave:
                start_date = datetime.strptime(sick_leave[start_key], "%Y-%m-%d").date()
                end_date = datetime.strptime(sick_leave[end_key], "%Y-%m-%d").date()
                days = (end_date - start_date).days + 1  # +1 um den letzten Tag einzuschließen
                employee_data[user_id]["sick_days"] += days
        except (ValueError, KeyError, TypeError):
            # Wenn Datumsberechnung fehlschlägt, zähle einen Tag
            employee_data[user_id]["sick_days"] += 1
    
    # Verarbeite Urlaubsdaten
    for vacation in vacation_requests:
        # Bestimme die Benutzer-ID
        user_id = None
        if "user_id" in vacation:
            user_id = vacation["user_id"]
        elif "employee" in vacation and vacation["employee"] in user_map.values():
            # Finde die ID anhand des Namens
            for id, name in user_map.items():
                if name == vacation["employee"]:
                    user_id = id
                    break
        
        if not user_id or user_id not in employee_data:
            continue
        
        # Prüfe, ob der Urlaub genehmigt wurde
        status = vacation.get("status", "approved")  # Standardmäßig als genehmigt betrachten, wenn kein Status angegeben
        if status != "approved":
            continue
        
        # Berechne Urlaubstage
        try:
            # Bestimme Start- und Enddatum
            start_key = "start_date" if "start_date" in vacation else "date"
            end_key = "end_date" if "end_date" in vacation else "end"
            
            if start_key in vacation and end_key in vacation:
                start_date = datetime.strptime(vacation[start_key], "%Y-%m-%d").date()
                end_date = datetime.strptime(vacation[end_key], "%Y-%m-%d").date()
                days = (end_date - start_date).days + 1  # +1 um den letzten Tag einzuschließen
                employee_data[user_id]["vacation_days"] += days
        except (ValueError, KeyError, TypeError):
            # Wenn Datumsberechnung fehlschlägt, zähle einen Tag
            employee_data[user_id]["vacation_days"] += 1
    
    # Erstelle DataFrame für die Anzeige
    df = pd.DataFrame([
        {
            "Mitarbeiter": data["name"],
            "Rolle": data["role"],
            "Gesamtarbeitszeit (Std)": round(data["total_hours"], 2),
            "Überstunden (Tage)": data["overtime_count"],
            "Krankheitstage": data["sick_days"],
            "Urlaubstage": data["vacation_days"],
            "Einträge": data["entries_count"]
        }
        for user_id, data in employee_data.items()
    ])
    
    # Zeige Tabelle
    st.dataframe(df, use_container_width=True)
    
    # Erstelle Radar-Chart für Mitarbeitervergleich
    if len(df) > 1:  # Nur anzeigen, wenn mehr als ein Mitarbeiter vorhanden ist
        # Normalisiere die Daten für das Radar-Chart
        radar_df = df.copy()
        columns_to_normalize = ["Gesamtarbeitszeit (Std)", "Überstunden (Tage)", "Krankheitstage", "Urlaubstage", "Einträge"]
        
        for col in columns_to_normalize:
            max_val = radar_df[col].max()
            if max_val > 0:  # Vermeide Division durch Null
                radar_df[col] = radar_df[col] / max_val
        
        # Erstelle Radar-Chart
        fig = go.Figure()
        
        for i, row in radar_df.iterrows():
            fig.add_trace(go.Scatterpolar(
                r=[row["Gesamtarbeitszeit (Std)"], row["Überstunden (Tage)"], 
                   row["Krankheitstage"], row["Urlaubstage"], row["Einträge"]],
                theta=["Arbeitszeit", "Überstunden", "Krankheit", "Urlaub", "Einträge"],
                fill='toself',
                name=row["Mitarbeiter"]
            ))
        
        fig.update_layout(
            polar=dict(
                radialaxis=dict(
                    visible=True,
                    range=[0, 1]
                )),
            showlegend=True,
            title="Mitarbeitervergleich (normalisiert)"
        )
        
        st.plotly_chart(fig, use_container_width=True)
