import streamlit as st
import pandas as pd
import json
import os
import csv
import io
import base64
from datetime import datetime, timedelta
import sys
sys.path.append(os.path.abspath(os.path.dirname(__file__)))
from datetime_utils import parse_datetime_string

def implement_export_functionality():
    """
    Implementiert Export-Funktionen für verschiedene Daten der App
    """
    def load_data_for_export():
        """Lädt alle relevanten Daten für den Export"""
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
    
    def get_download_link(df, filename, link_text):
        """Erstellt einen Download-Link für ein DataFrame"""
        csv = df.to_csv(index=False)
        b64 = base64.b64encode(csv.encode()).decode()
        href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{link_text}</a>'
        return href
    
    def get_json_download_link(data, filename, link_text):
        """Erstellt einen Download-Link für JSON-Daten"""
        json_str = json.dumps(data, indent=2)
        b64 = base64.b64encode(json_str.encode()).decode()
        href = f'<a href="data:file/json;base64,{b64}" download="{filename}">{link_text}</a>'
        return href
    
    def show_export_ui():
        st.title("Daten exportieren")
        
        # Prüfen, ob der Benutzer angemeldet ist
        if not st.session_state.get("logged_in", False):
            st.warning("Bitte melden Sie sich an, um diese Funktion zu nutzen.")
            return
        
        # Prüfen, ob der Benutzer Admin ist (für bestimmte Exporte)
        is_admin = st.session_state.get("is_admin", False)
        
        # Daten laden
        data = load_data_for_export()
        
        # Benutzer-ID
        user_id = st.session_state.get("user_id")
        
        # Tabs für verschiedene Export-Optionen
        tabs = ["Zeiterfassung"]
        
        if is_admin:
            tabs.extend(["Mitarbeiter", "Projekte", "Urlaub & Krankheit", "Vollständiger Export"])
        
        selected_tab = st.selectbox("Export-Kategorie auswählen", tabs)
        
        if selected_tab == "Zeiterfassung":
            st.subheader("Zeiterfassungsdaten exportieren")
            
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
            
            # Daten für Export vorbereiten
            if filtered_entries:
                export_data = []
                for entry in filtered_entries:
                    # Mitarbeitername finden
                    employee_name = "Unbekannt"
                    for emp in data["employees"]:
                        if emp["id"] == entry.get("user_id"):
                            employee_name = emp["name"]
                            break
                    
                    export_data.append({
                        "Mitarbeiter": employee_name,
                        "Startzeit": entry.get("start_time", ""),
                        "Endzeit": entry.get("end_time", ""),
                        "Dauer": entry.get("duration_formatted", ""),
                        "Projekt": entry.get("project", ""),
                        "Homeoffice": "Ja" if entry.get("homeoffice", False) else "Nein"
                    })
                
                # DataFrame erstellen
                df = pd.DataFrame(export_data)
                
                # Vorschau anzeigen
                st.subheader("Vorschau")
                st.dataframe(df.head(10) if len(df) > 10 else df)
                
                # Export-Optionen
                st.subheader("Export-Optionen")
                export_format = st.radio("Format auswählen", ["CSV", "Excel", "JSON"])
                
                if export_format == "CSV":
                    # CSV-Export
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Als CSV exportieren",
                        data=csv,
                        file_name="zeiterfassung_export.csv",
                        mime="text/csv"
                    )
                elif export_format == "Excel":
                    # Excel-Export
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df.to_excel(writer, sheet_name='Zeiterfassung', index=False)
                    
                    excel_data = output.getvalue()
                    st.download_button(
                        label="Als Excel exportieren",
                        data=excel_data,
                        file_name="zeiterfassung_export.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                elif export_format == "JSON":
                    # JSON-Export
                    json_str = json.dumps(filtered_entries, indent=2)
                    st.download_button(
                        label="Als JSON exportieren",
                        data=json_str,
                        file_name="zeiterfassung_export.json",
                        mime="application/json"
                    )
            else:
                st.info("Keine Zeiteinträge im ausgewählten Zeitraum gefunden.")
        
        elif selected_tab == "Mitarbeiter" and is_admin:
            st.subheader("Mitarbeiterdaten exportieren")
            
            # Mitarbeiterdaten für Export vorbereiten
            if data["employees"]:
                export_data = []
                for emp in data["employees"]:
                    export_data.append({
                        "ID": emp["id"],
                        "Name": emp["name"],
                        "Benutzername": emp["username"],
                        "Admin": "Ja" if emp.get("is_admin", False) else "Nein",
                        "Status": emp.get("status", ""),
                        "Arbeitszeitmodell": emp.get("work_time_model", "vollzeit")
                    })
                
                # DataFrame erstellen
                df = pd.DataFrame(export_data)
                
                # Vorschau anzeigen
                st.subheader("Vorschau")
                st.dataframe(df)
                
                # Export-Optionen
                st.subheader("Export-Optionen")
                export_format = st.radio("Format auswählen", ["CSV", "Excel", "JSON"], key="emp_format")
                
                if export_format == "CSV":
                    # CSV-Export
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Als CSV exportieren",
                        data=csv,
                        file_name="mitarbeiter_export.csv",
                        mime="text/csv"
                    )
                elif export_format == "Excel":
                    # Excel-Export
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df.to_excel(writer, sheet_name='Mitarbeiter', index=False)
                    
                    excel_data = output.getvalue()
                    st.download_button(
                        label="Als Excel exportieren",
                        data=excel_data,
                        file_name="mitarbeiter_export.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                elif export_format == "JSON":
                    # JSON-Export
                    json_str = json.dumps(data["employees"], indent=2)
                    st.download_button(
                        label="Als JSON exportieren",
                        data=json_str,
                        file_name="mitarbeiter_export.json",
                        mime="application/json"
                    )
            else:
                st.info("Keine Mitarbeiterdaten gefunden.")
        
        elif selected_tab == "Projekte" and is_admin:
            st.subheader("Projektdaten exportieren")
            
            # Projektdaten für Export vorbereiten
            if data["projects"]:
                export_data = []
                for project in data["projects"]:
                    # Zeiteinträge für dieses Projekt finden
                    project_entries = [
                        entry for entry in data["time_entries"]
                        if entry.get("project") == project["name"]
                    ]
                    
                    # Gesamtstunden berechnen
                    total_hours = sum(entry.get("duration_seconds", 0) / 3600 for entry in project_entries)
                    
                    export_data.append({
                        "ID": project["id"],
                        "Name": project["name"],
                        "Beschreibung": project["description"],
                        "Budget (Std)": project["budget_hours"],
                        "Verbrauchte Zeit (Std)": round(total_hours, 2),
                        "Verbleibend (Std)": round(project["budget_hours"] - total_hours, 2) if project["budget_hours"] > 0 else "Unbegrenzt"
                    })
                
                # DataFrame erstellen
                df = pd.DataFrame(export_data)
                
                # Vorschau anzeigen
                st.subheader("Vorschau")
                st.dataframe(df)
                
                # Export-Optionen
                st.subheader("Export-Optionen")
                export_format = st.radio("Format auswählen", ["CSV", "Excel", "JSON"], key="proj_format")
                
                if export_format == "CSV":
                    # CSV-Export
                    csv = df.to_csv(index=False)
                    st.download_button(
                        label="Als CSV exportieren",
                        data=csv,
                        file_name="projekte_export.csv",
                        mime="text/csv"
                    )
                elif export_format == "Excel":
                    # Excel-Export
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        df.to_excel(writer, sheet_name='Projekte', index=False)
                    
                    excel_data = output.getvalue()
                    st.download_button(
                        label="Als Excel exportieren",
                        data=excel_data,
                        file_name="projekte_export.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                elif export_format == "JSON":
                    # JSON-Export
                    json_str = json.dumps(data["projects"], indent=2)
                    st.download_button(
                        label="Als JSON exportieren",
                        data=json_str,
                        file_name="projekte_export.json",
                        mime="application/json"
                    )
            else:
                st.info("Keine Projektdaten gefunden.")
        
        elif selected_tab == "Urlaub & Krankheit" and is_admin:
            st.subheader("Urlaubs- und Krankheitsdaten exportieren")
            
            # Urlaubs- und Krankheitsdaten laden
            leave_data = data["leave_data"]
            
            # Tabs für Urlaub und Krankheit
            leave_tabs = ["Urlaub", "Krankheit"]
            selected_leave_tab = st.selectbox("Kategorie auswählen", leave_tabs)
            
            if selected_leave_tab == "Urlaub":
                # Urlaubsdaten für Export vorbereiten
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
                    
                    # Vorschau anzeigen
                    st.subheader("Vorschau")
                    st.dataframe(df)
                    
                    # Export-Optionen
                    st.subheader("Export-Optionen")
                    export_format = st.radio("Format auswählen", ["CSV", "Excel", "JSON"], key="vac_format")
                    
                    if export_format == "CSV":
                        # CSV-Export
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Als CSV exportieren",
                            data=csv,
                            file_name="urlaub_export.csv",
                            mime="text/csv"
                        )
                    elif export_format == "Excel":
                        # Excel-Export
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            df.to_excel(writer, sheet_name='Urlaub', index=False)
                        
                        excel_data = output.getvalue()
                        st.download_button(
                            label="Als Excel exportieren",
                            data=excel_data,
                            file_name="urlaub_export.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    elif export_format == "JSON":
                        # JSON-Export
                        json_str = json.dumps(leave_data["vacation"], indent=2)
                        st.download_button(
                            label="Als JSON exportieren",
                            data=json_str,
                            file_name="urlaub_export.json",
                            mime="application/json"
                        )
                else:
                    st.info("Keine Urlaubsdaten gefunden.")
            
            elif selected_leave_tab == "Krankheit":
                # Krankheitsdaten für Export vorbereiten
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
                    
                    # Vorschau anzeigen
                    st.subheader("Vorschau")
                    st.dataframe(df)
                    
                    # Export-Optionen
                    st.subheader("Export-Optionen")
                    export_format = st.radio("Format auswählen", ["CSV", "Excel", "JSON"], key="sick_format")
                    
                    if export_format == "CSV":
                        # CSV-Export
                        csv = df.to_csv(index=False)
                        st.download_button(
                            label="Als CSV exportieren",
                            data=csv,
                            file_name="krankheit_export.csv",
                            mime="text/csv"
                        )
                    elif export_format == "Excel":
                        # Excel-Export
                        output = io.BytesIO()
                        with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                            df.to_excel(writer, sheet_name='Krankheit', index=False)
                        
                        excel_data = output.getvalue()
                        st.download_button(
                            label="Als Excel exportieren",
                            data=excel_data,
                            file_name="krankheit_export.xlsx",
                            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                        )
                    elif export_format == "JSON":
                        # JSON-Export
                        json_str = json.dumps(leave_data["sick_leave"], indent=2)
                        st.download_button(
                            label="Als JSON exportieren",
                            data=json_str,
                            file_name="krankheit_export.json",
                            mime="application/json"
                        )
                else:
                    st.info("Keine Krankheitsdaten gefunden.")
        
        elif selected_tab == "Vollständiger Export" and is_admin:
            st.subheader("Vollständigen Datenexport erstellen")
            
            st.write("Diese Funktion erstellt einen vollständigen Export aller Daten der Anwendung.")
            st.warning("Achtung: Der Export enthält sensible Daten wie Benutzernamen und Passwörter. Bitte sorgfältig behandeln!")
            
            if st.button("Vollständigen Export erstellen"):
                # JSON-Export aller Daten
                json_str = json.dumps(data, indent=2)
                st.download_button(
                    label="Vollständigen Export herunterladen",
                    data=json_str,
                    file_name="vollstaendiger_export.json",
                    mime="application/json"
                )
    
    return show_export_ui
