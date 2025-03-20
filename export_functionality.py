import streamlit as st
import pandas as pd
import json
import os
import csv
import io
import base64
from datetime import datetime, timedelta

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
            
            # Nach Datum filtern
            filtered_entries = [
                entry for entry in filtered_entries
                if entry.get("start_time") and datetime.strptime(entry.get("start_time"), "%Y-%m-%d %H:%M:%S").date() >= start_date
                and datetime.strptime(entry.get("start_time"), "%Y-%m-%d %H:%M:%S").date() <= end_date
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
                    # JSON-Export (ohne Passwörter)
                    safe_employees = []
                    for emp in data["employees"]:
                        emp_copy = emp.copy()
                        if "password" in emp_copy:
                            del emp_copy["password"]
                        safe_employees.append(emp_copy)
                    
                    json_str = json.dumps(safe_employees, indent=2)
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
                    export_data.append({
                        "ID": project["id"],
                        "Name": project["name"],
                        "Beschreibung": project["description"],
                        "Budget (Stunden)": project["budget_hours"],
                        "Verbrauchte Stunden": project["used_hours"]
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
            
            # Urlaubs- und Krankheitsdaten für Export vorbereiten
            if data["leave_data"]:
                # Urlaubsanträge
                vacation_data = []
                for user_id, vacation_info in data["leave_data"].get("vacation", {}).items():
                    # Mitarbeitername finden
                    employee_name = "Unbekannt"
                    for emp in data["employees"]:
                        if str(emp["id"]) == user_id:
                            employee_name = emp["name"]
                            break
                    
                    # Genehmigte Anträge
                    for request in vacation_info.get("approved_requests", []):
                        vacation_data.append({
                            "Mitarbeiter": employee_name,
                            "Startdatum": request.get("start_date", ""),
                            "Enddatum": request.get("end_date", ""),
                            "Tage": request.get("days", 0),
                            "Status": "Genehmigt",
                            "Antragsdatum": request.get("request_date", ""),
                            "Genehmigungsdatum": request.get("approval_date", ""),
                            "Grund": request.get("reason", "")
                        })
                    
                    # Ausstehende Anträge
                    for request in vacation_info.get("pending_requests", []):
                        vacation_data.append({
                            "Mitarbeiter": employee_name,
                            "Startdatum": request.get("start_date", ""),
                            "Enddatum": request.get("end_date", ""),
                            "Tage": request.get("days", 0),
                            "Status": "Ausstehend",
                            "Antragsdatum": request.get("request_date", ""),
                            "Genehmigungsdatum": "",
                            "Grund": request.get("reason", "")
                        })
                
                # Krankmeldungen
                sick_leave_data = []
                for user_id, sick_leaves in data["leave_data"].get("sick_leave", {}).items():
                    # Mitarbeitername finden
                    employee_name = "Unbekannt"
                    for emp in data["employees"]:
                        if str(emp["id"]) == user_id:
                            employee_name = emp["name"]
                            break
                    
                    for sick_leave in sick_leaves:
                        sick_leave_data.append({
                            "Mitarbeiter": employee_name,
                            "Startdatum": sick_leave.get("start_date", ""),
                            "Enddatum": sick_leave.get("end_date", ""),
                            "Tage": sick_leave.get("days", 0),
                            "Ärztliche Bescheinigung": "Ja" if sick_leave.get("has_doctor_note", False) else "Nein",
                            "Meldedatum": sick_leave.get("report_date", ""),
                            "Grund": sick_leave.get("reason", "")
                        })
                
                # DataFrames erstellen
                vacation_df = pd.DataFrame(vacation_data)
                sick_leave_df = pd.DataFrame(sick_leave_data)
                
                # Vorschau anzeigen
                st.subheader("Urlaubsanträge")
                if not vacation_df.empty:
                    st.dataframe(vacation_df.head(10) if len(vacation_df) > 10 else vacation_df)
                else:
                    st.info("Keine Urlaubsanträge gefunden.")
                
                st.subheader("Krankmeldungen")
                if not sick_leave_df.empty:
                    st.dataframe(sick_leave_df.head(10) if len(sick_leave_df) > 10 else sick_leave_df)
                else:
                    st.info("Keine Krankmeldungen gefunden.")
                
                # Export-Optionen
                st.subheader("Export-Optionen")
                export_format = st.radio("Format auswählen", ["CSV", "Excel", "JSON"], key="leave_format")
                
                if export_format == "CSV":
                    # CSV-Export
                    col1, col2 = st.columns(2)
                    with col1:
                        if not vacation_df.empty:
                            csv = vacation_df.to_csv(index=False)
                            st.download_button(
                                label="Urlaubsanträge als CSV exportieren",
                                data=csv,
                                file_name="urlaub_export.csv",
                                mime="text/csv"
                            )
                    with col2:
                        if not sick_leave_df.empty:
                            csv = sick_leave_df.to_csv(index=False)
                            st.download_button(
                                label="Krankmeldungen als CSV exportieren",
                                data=csv,
                                file_name="krankheit_export.csv",
                                mime="text/csv"
                            )
                
                elif export_format == "Excel":
                    # Excel-Export
                    output = io.BytesIO()
                    with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                        if not vacation_df.empty:
                            vacation_df.to_excel(writer, sheet_name='Urlaub', index=False)
                        if not sick_leave_df.empty:
                            sick_leave_df.to_excel(writer, sheet_name='Krankheit', index=False)
                    
                    excel_data = output.getvalue()
                    st.download_button(
                        label="Als Excel exportieren",
                        data=excel_data,
                        file_name="urlaub_krankheit_export.xlsx",
                        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                    )
                
                elif export_format == "JSON":
                    # JSON-Export
                    json_str = json.dumps(data["leave_data"], indent=2)
                    st.download_button(
                        label="Als JSON exportieren",
                        data=json_str,
                        file_name="urlaub_krankheit_export.json",
                        mime="application/json"
                    )
            else:
                st.info("Keine Urlaubs- und Krankheitsdaten gefunden.")
        
        elif selected_tab == "Vollständiger Export" and is_admin:
            st.subheader("Vollständigen Datenexport erstellen")
            
            st.warning("Diese Funktion exportiert alle Daten der Anwendung. Bitte stellen Sie sicher, dass Sie die Daten sicher aufbewahren.")
            
            # Export-Optionen
            export_format = st.radio("Format auswählen", ["JSON", "Excel"], key="full_format")
            
            if export_format == "JSON":
                # JSON-Export
                # Passwörter aus dem Export entfernen
                safe_data = data.copy()
                for emp in safe_data["employees"]:
                    if "password" in emp:
                        del emp["password"]
                
                json_str = json.dumps(safe_data, indent=2)
                st.download_button(
                    label="Vollständigen Export als JSON herunterladen",
                    data=json_str,
                    file_name="zeiterfassung_vollexport.json",
                    mime="application/json"
                )
            
            elif export_format == "Excel":
                # Excel-Export
                output = io.BytesIO()
                with pd.ExcelWriter(output, engine='xlsxwriter') as writer:
                    # Mitarbeiter
                    if data["employees"]:
                        emp_data = []
                        for emp in data["employees"]:
                            emp_copy = emp.copy()
                            if "password" in emp_copy:
                                del emp_copy["password"]
                            emp_data.append(emp_copy)
                        
                        emp_df = pd.DataFrame(emp_data)
                        emp_df.to_excel(writer, sheet_name='Mitarbeiter', index=False)
                    
                    # Zeiteinträge
                    if data["time_entries"]:
                        time_df = pd.DataFrame(data["time_entries"])
                        time_df.to_excel(writer, sheet_name='Zeiteinträge', index=False)
                    
                    # Projekte
                    if data["projects"]:
                        proj_df = pd.DataFrame(data["projects"])
                        proj_df.to_excel(writer, sheet_name='Projekte', index=False)
                    
                    # Urlaub und Krankheit
                    if data["leave_data"]:
                        # Zu komplex für direktes DataFrame, als JSON in Zelle
                        leave_df = pd.DataFrame([{"data": json.dumps(data["leave_data"])}])
                        leave_df.to_excel(writer, sheet_name='Urlaub_Krankheit', index=False)
                
                excel_data = output.getvalue()
                st.download_button(
                    label="Vollständigen Export als Excel herunterladen",
                    data=excel_data,
                    file_name="zeiterfassung_vollexport.xlsx",
                    mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
                )
    
    # Rückgabe der UI-Funktion
    return show_export_ui

# Exportiere die Funktionen
__all__ = ['implement_export_functionality']
