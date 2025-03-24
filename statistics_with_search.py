import streamlit as st
import pandas as pd
import datetime
from typing import Dict, List, Any, Callable
from data_persistence import load_time_entries, load_employees

def show_statistics_with_search():
    """Main statistics display function"""
    st.title("Statistiken und Auswertungen")
    
    # Load data
    time_entries = load_time_entries()
    employees = load_employees()
    
    if not time_entries:
        st.warning("Keine Zeitdaten vorhanden für die Auswertung.")
        return
        
    # Create DataFrame from entries
    entries_data = []
    for entry in time_entries:
        start_time = entry.get("start_time")
        end_time = entry.get("end_time")
        
        # Convert string times to datetime
        if isinstance(start_time, str):
            try:
                start_time = datetime.datetime.fromisoformat(start_time)
            except ValueError:
                start_time = None
                
        if isinstance(end_time, str) and end_time != "Noch nicht ausgecheckt":
            try:
                end_time = datetime.datetime.fromisoformat(end_time)
            except ValueError:
                end_time = None
        
        # Calculate duration
        duration = (end_time - start_time).total_seconds() / 3600 if start_time and end_time else None
        
        entries_data.append({
            "employee_id": entry.get("employee_id"),
            "employee_name": entry.get("employee_name", "Unbekannt"),
            "type": entry.get("type", "Arbeit"),
            "location": entry.get("location", "Unbekannt"),
            "team": entry.get("team", "Unbekannt"),
            "start_time": start_time,
            "end_time": end_time,
            "duration": duration
        })
    
    df = pd.DataFrame(entries_data)
    
    # Search and filter UI
    st.subheader("Suche und Filter")
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input(
            "Von Datum",
            value=datetime.date.today() - datetime.timedelta(days=30),
            key="stats_start_date_unique"
        )
    with col2:
        end_date = st.date_input(
            "Bis Datum", 
            value=datetime.date.today(),
            key="stats_end_date_unique"
        )
    
    # Filters with unique keys
    employee_filter = st.selectbox(
        "Mitarbeiter", 
        ["Alle"] + sorted(df["employee_name"].unique()),
        key="stats_employee_filter_unique"
    )
    team_filter = st.selectbox(
        "Team",
        ["Alle"] + sorted(df["team"].unique()),
        key="stats_team_filter_unique"
    )
    location_filter = st.selectbox(
        "Standort",
        ["Alle"] + sorted(df["location"].unique()),
        key="stats_location_filter_unique"
    )
    
    # Apply filters
    filtered_df = df[
        (df["start_time"].dt.date >= start_date) &
        (df["start_time"].dt.date <= end_date)
    ]
    if employee_filter != "Alle":
        filtered_df = filtered_df[filtered_df["employee_name"] == employee_filter]
    if team_filter != "Alle":
        filtered_df = filtered_df[filtered_df["team"] == team_filter]
    if location_filter != "Alle":
        filtered_df = filtered_df[filtered_df["location"] == location_filter]
    
    # Display results
    st.subheader("Ergebnisse")
    if filtered_df.empty:
        st.info("Keine Daten für die gewählten Filter gefunden.")
    else:
        st.write(f"Anzahl Einträge: {len(filtered_df)}")
        total_hours = filtered_df["duration"].sum()
        st.write(f"Gesamtstunden: {total_hours:.2f}")
        
        # Visualizations
        if employee_filter == "Alle":
            st.bar_chart(filtered_df.groupby("employee_name")["duration"].sum())
        if team_filter == "Alle":
            st.bar_chart(filtered_df.groupby("team")["duration"].sum())
        
        with st.expander("Details anzeigen"):
            st.dataframe(filtered_df)

# For backward compatibility
implement_statistics_with_search = lambda: show_statistics_with_search
