import streamlit as st
import pandas as pd
import os
import json
import uuid
import bcrypt
from datetime import datetime, timedelta
from modules.utils import load_employees, load_time_entries, load_vacation_requests, load_sick_leaves

# Dateipfade
DATA_DIR = "data"
EMPLOYEES_FILE = os.path.join(DATA_DIR, "employees.json")
VACATION_FILE = os.path.join(DATA_DIR, "vacation_requests.json")
SICK_FILE = os.path.join(DATA_DIR, "sick_leaves.json")

# Hilfsfunktionen
def save_employees(employees):
    """Speichert die Mitarbeiterdaten in der JSON-Datei."""
    os.makedirs(os.path.dirname(EMPLOYEES_FILE), exist_ok=True)
    with open(EMPLOYEES_FILE, "w", encoding="utf-8") as f:
        json.dump(employees, f, indent=4, ensure_ascii=False)

def hash_password(password):
    """Hasht ein Passwort mit bcrypt."""
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def show():
    st.title("⚙️ Administrationsbereich")
    
    # Tabs für verschiedene Administrationsbereiche
    tabs = st.tabs(["Mitarbeiterverwaltung", "Rollenverwaltung", "Urlaubsanträge", "Krankmeldungen", "Datenexport"])
    
    # Tab 1: Mitarbeiterverwaltung
    with tabs[0]:
        st.header("Mitarbeiterverwaltung")
        
        # Mitarbeiter laden
        employees = load_employees()
        
        # Mitarbeiter hinzufügen
        with st.expander("Neuen Mitarbeiter hinzufügen", expanded=False):
            col1, col2 = st.columns(2)
            
            with col1:
                new_name = st.text_input("Name", key="new_emp_name")
                new_email = st.text_input("E-Mail", key="new_emp_email")
                new_username = st.text_input("Benutzername", key="new_emp_username")
                new_password = st.text_input("Passwort", type="password", key="new_emp_password")
            
            with col2:
                new_role = st.selectbox("Rolle", ["Mitarbeiter", "Admin"], key="new_emp_role")
                new_location = st.selectbox("Standort", ["Werner Siemens Strasse 107", "Werner Siemens Strasse 39", "Home Office"], key="new_emp_location")
                new_team = st.text_input("Team", key="new_emp_team")
                new_phone = st.text_input("Telefon", key="new_emp_phone")
            
            if st.button("Mitarbeiter hinzufügen", key="add_emp_btn"):
                # Validierung
                if not new_name or not new_email or not new_username or not new_password:
                    st.error("Bitte füllen Sie alle Pflichtfelder aus.")
                else:
                    # Überprüfen, ob Benutzername oder E-Mail bereits existiert
                    if any(emp.get("username") == new_username for emp in employees):
                        st.error("Dieser Benutzername ist bereits vergeben.")
                    elif any(emp.get("email") == new_email for emp in employees):
                        st.error("Diese E-Mail-Adresse ist bereits registriert.")
                    else:
                        # Neuen Mitarbeiter erstellen
                        new_employee = {
                            "id": str(uuid.uuid4()),
                            "name": new_name,
                            "email": new_email,
                            "username": new_username,
                            "password": hash_password(new_password),
                            "role": new_role,
                            "location": new_location,
                            "team": new_team,
                            "phone": new_phone,
                            "created_at": datetime.now().isoformat()
                        }
                        
                        employees.append(new_employee)
                        save_employees(employees)
                        st.success(f"Mitarbeiter {new_name} wurde erfolgreich hinzugefügt.")
                        st.rerun()
        
        # Mitarbeiter bearbeiten und löschen
        st.subheader("Mitarbeiterliste")
        
        # Suchfilter
        search_query = st.text_input("Suche nach Namen oder E-Mail", key="emp_search")
        
        # Filtern der Mitarbeiter basierend auf der Suche
        if search_query:
            filtered_employees = [emp for emp in employees if 
                                 search_query.lower() in emp.get("name", "").lower() or 
                                 search_query.lower() in emp.get("email", "").lower()]
        else:
            filtered_employees = employees
        
        # Anzeigen der Mitarbeiterliste
        if not filtered_employees:
            st.info("Keine Mitarbeiter gefunden.")
        else:
            for emp in filtered_employees:
                with st.expander(f"{emp.get('name')} - {emp.get('email')} ({emp.get('role')})", expanded=False):
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        edit_name = st.text_input("Name", value=emp.get("name", ""), key=f"edit_name_{emp['id']}")
                        edit_email = st.text_input("E-Mail", value=emp.get("email", ""), key=f"edit_email_{emp['id']}")
                        edit_username = st.text_input("Benutzername", value=emp.get("username", ""), key=f"edit_username_{emp['id']}")
                        edit_password = st.text_input("Neues Passwort (leer lassen, um beizubehalten)", type="password", key=f"edit_password_{emp['id']}")
                    
                    with col2:
                        edit_role = st.selectbox("Rolle", ["Mitarbeiter", "Admin"], index=0 if emp.get("role") != "Admin" else 1, key=f"edit_role_{emp['id']}")
                        edit_location = st.selectbox("Standort", ["Werner Siemens Strasse 107", "Werner Siemens Strasse 39", "Home Office"], 
                                                   index=0 if emp.get("location") == "Werner Siemens Strasse 107" else 
                                                         1 if emp.get("location") == "Werner Siemens Strasse 39" else 2, 
                                                   key=f"edit_location_{emp['id']}")
                        edit_team = st.text_input("Team", value=emp.get("team", ""), key=f"edit_team_{emp['id']}")
                        edit_phone = st.text_input("Telefon", value=emp.get("phone", ""), key=f"edit_phone_{emp['id']}")
                    
                    col3, col4 = st.columns(2)
                    
                    with col3:
                        if st.button("Änderungen speichern", key=f"save_emp_{emp['id']}"):
                            # Aktualisiere Mitarbeiterdaten
                            for e in employees:
                                if e["id"] == emp["id"]:
                                    e["name"] = edit_name
                                    e["email"] = edit_email
                                    e["username"] = edit_username
                                    if edit_password:  # Nur aktualisieren, wenn ein neues Passwort eingegeben wurde
                                        e["password"] = hash_password(edit_password)
                                    e["role"] = edit_role
                                    e["location"] = edit_location
                                    e["team"] = edit_team
                                    e["phone"] = edit_phone
                                    e["updated_at"] = datetime.now().isoformat()
                                    break
                            
                            save_employees(employees)
                            st.success(f"Mitarbeiter {edit_name} wurde erfolgreich aktualisiert.")
                            st.rerun()
                    
                    with col4:
                        if st.button("Mitarbeiter löschen", key=f"delete_emp_{emp['id']}"):
                            # Bestätigungsdialog
                            if st.checkbox(f"Wirklich löschen? Diese Aktion kann nicht rückgängig gemacht werden.", key=f"confirm_delete_{emp['id']}"):
                                # Mitarbeiter aus der Liste entfernen
                                employees = [e for e in employees if e["id"] != emp["id"]]
                                save_employees(employees)
                                st.success(f"Mitarbeiter {emp.get('name')} wurde erfolgreich gelöscht.")
                                st.rerun()
    
    # Tab 2: Rollenverwaltung
    with tabs[1]:
        st.header("Rollenverwaltung")
        
        # Mitarbeiter laden
        employees = load_employees()
        
        # Rollen anzeigen und bearbeiten
        st.subheader("Rollenzuweisung")
        
        # Erstelle eine Tabelle mit Mitarbeitern und ihren Rollen
        role_data = []
        for emp in employees:
            role_data.append({
                "ID": emp.get("id"),
                "Name": emp.get("name", ""),
                "E-Mail": emp.get("email", ""),
                "Aktuelle Rolle": emp.get("role", "Mitarbeiter"),
            })
        
        role_df = pd.DataFrame(role_data)
        st.dataframe(role_df, use_container_width=True)
        
        # Rolle ändern
        st.subheader("Rolle ändern")
        
        col1, col2 = st.columns(2)
        
        with col1:
            selected_emp_id = st.selectbox("Mitarbeiter auswählen", 
                                         options=[emp["id"] for emp in employees],
                                         format_func=lambda x: next((emp["name"] for emp in employees if emp["id"] == x), ""))
        
        with col2:
            selected_role = st.selectbox("Neue Rolle", ["Mitarbeiter", "Admin"])
        
        if st.button("Rolle aktualisieren"):
            # Rolle des ausgewählten Mitarbeiters aktualisieren
            for emp in employees:
                if emp["id"] == selected_emp_id:
                    old_role = emp.get("role", "Mitarbeiter")
                    emp["role"] = selected_role
                    emp["updated_at"] = datetime.now().isoformat()
                    break
            
            save_employees(employees)
            st.success(f"Rolle von {next((emp['name'] for emp in employees if emp['id'] == selected_emp_id), '')} wurde von {old_role} zu {selected_role} geändert.")
    
    # Tab 3: Urlaubsanträge
    with tabs[2]:
        st.header("Urlaubsanträge verwalten")
        
        # Daten laden
        vacation_requests = load_vacation_requests()
        employees = load_employees()
        employee_map = {emp["id"]: emp["name"] for emp in employees}
        
        # Neue Anträge
        st.subheader("🔔 Neue Urlaubsanträge")
        
        pending = [req for req in vacation_requests if req.get("status") == "pending"]
        if pending:
            st.warning(f"⚠️ {len(pending)} offene Urlaubsanträge")
            for p in pending:
                name = employee_map.get(p["user_id"], "Unbekannt")
                with st.expander(f"{name}: {p['start_date']} bis {p['end_date']}", expanded=True):
                    st.write(f"**Mitarbeiter:** {name}")
                    st.write(f"**Zeitraum:** {p['start_date']} bis {p['end_date']}")
                    st.write(f"**Antrag-ID:** {p.get('id', 'N/A')}")
                    
                    col1, col2 = st.columns(2)
                    
                    with col1:
                        if st.button("✅ Genehmigen", key=f"approve_{p.get('id')}"):
                            # Antrag genehmigen
                            for req in vacation_requests:
                                if req.get("id") == p.get("id"):
                                    req["status"] = "approved"
                                    req["approved_at"] = datetime.now().isoformat()
                                    break
                            
                            # Speichern
                            with open(VACATION_FILE, "w", encoding="utf-8") as f:
                                json.dump(vacation_requests, f, indent=4, ensure_ascii=False)
                            
                            st.success(f"Urlaubsantrag von {name} wurde genehmigt.")
                            st.rerun()
                    
                    with col2:
                        if st.button("❌ Ablehnen", key=f"reject_{p.get('id')}"):
                            # Antrag ablehnen
                            for req in vacation_requests:
                                if req.get("id") == p.get("id"):
                                    req["status"] = "rejected"
                                    req["rejected_at"] = datetime.now().isoformat()
                                    break
                            
                            # Speichern
                            with open(VACATION_FILE, "w", encoding="utf-8") as f:
                                json.dump(vacation_requests, f, indent=4, ensure_ascii=False)
                            
                            st.info(f"Urlaubsantrag von {name} wurde abgelehnt.")
                            st.rerun()
        else:
            st.success("Keine neuen Anträge 🎉")
        
        # Alle Anträge
        st.subheader("Alle Urlaubsanträge")
        
        # Erstelle eine Tabelle mit allen Urlaubsanträgen
        vacation_data = []
        for req in vacation_requests:
            employee_name = employee_map.get(req.get("user_id"), "Unbekannt")
            vacation_data.append({
                "Mitarbeiter": employee_name,
                "Von": req.get("start_date", "N/A"),
                "Bis": req.get("end_date", "N/A"),
                "Status": req.get("status", "pending"),
                "ID": req.get("id", "N/A")
            })
        
        if vacation_data:
            vacation_df = pd.DataFrame(vacation_data)
            st.dataframe(vacation_df, use_container_width=True)
        else:
            st.info("Keine Urlaubsanträge vorhanden.")
    
    # Tab 4: Krankmeldungen
    with tabs[3]:
        st.header("Krankmeldungen verwalten")
        
        # Daten laden
        sick_leaves = load_sick_leaves()
        employees = load_employees()
        employee_map = {emp["id"]: emp["name"] for emp in employees}
        
        # Neue Krankmeldungen
        st.subheader("🔔 Neue Krankmeldungen")
        
        recent_sick_leaves = [sick for sick in sick_leaves if 
                             (datetime.now() - datetime.strptime(sick.get("created_at", "2025-01-01"), "%Y-%m-%d") 
                             if "created_at" in sick else timedelta(days=30)) < timedelta(days=7)]
        
        if recent_sick_leaves:
            st.warning(f"⚠️ {len(recent_sick_leaves)} neue Krankmeldungen")
            for sick in recent_sick_leaves:
                name = employee_map.get(sick.get("user_id"), "Unbekannt")
                with st.expander(f"{name}: {sick.get('start_date', 'N/A')} bis {sick.get('end_date', 'N/A')}", expanded=True):
                    st.write(f"**Mitarbeiter:** {name}")
                    st.write(f"**Zeitraum:** {sick.get('start_date', 'N/A')} bis {sick.get('end_date', 'N/A')}")
                    st.write(f"**Grund:** {sick.get('reason', 'Nicht angegeben')}")
                    st.write(f"**Krankmeldungs-ID:** {sick.get('id', 'N/A')}")
        else:
            st.success("Keine neuen Krankmeldungen 🎉")
        
        # Alle Krankmeldungen
        st.subheader("Alle Krankmeldungen")
        
        # Erstelle eine Tabelle mit allen Krankmeldungen
        sick_data = []
        for sick in sick_leaves:
            employee_name = employee_map.get(sick.get("user_id"), "Unbekannt")
            sick_data.append({
                "Mitarbeiter": employee_name,
                "Von": sick.get("start_date", "N/A"),
                "Bis": sick.get("end_date", "N/A"),
                "Grund": sick.get("reason", "Nicht angegeben"),
                "ID": sick.get("id", "N/A")
            })
        
        if sick_data:
            sick_df = pd.DataFrame(sick_data)
            st.dataframe(sick_df, use_container_width=True)
        else:
            st.info("Keine Krankmeldungen vorhanden.")
    
    # Tab 5: Datenexport
    with tabs[4]:
        st.header("Datenexport")
        
        # Exportoptionen
        export_type = st.selectbox("Daten exportieren", 
                                 ["Mitarbeiterdaten", "Urlaubsanträge", "Krankmeldungen", "Arbeitszeiterfassung", "Alle Daten"])
        
        if export_type == "Mitarbeiterdaten":
            # Mitarbeiterdaten exportieren
            employees = load_employees()
            
            # Sensible Daten entfernen
            export_employees = []
            for emp in employees:
                export_emp = emp.copy()
                if "password" in export_emp:
                    export_emp["password"] = "********"  # Passwort ausblenden
                export_employees.append(export_emp)
            
            if export_employees:
                df = pd.DataFrame(export_employees)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Mitarbeiterdaten exportieren (CSV)", 
                                 data=csv, 
                                 file_name="mitarbeiterdaten_export.csv", 
                                 mime="text/csv")
            else:
                st.info("Keine Mitarbeiterdaten zum Exportieren vorhanden.")
        
        elif export_type == "Urlaubsanträge":
            # Urlaubsanträge exportieren
            vacation_requests = load_vacation_requests()
            employees = load_employees()
            employee_map = {emp["id"]: emp["name"] for emp in employees}
            
            export_vacation = []
            for req in vacation_requests:
                export_req = {
                    "Mitarbeiter": employee_map.get(req.get("user_id"), "Unbekannt"),
                    "Von": req.get("start_date", "N/A"),
                    "Bis": req.get("end_date", "N/A"),
                    "Status": req.get("status", "pending"),
                    "ID": req.get("id", "N/A")
                }
                export_vacation.append(export_req)
            
            if export_vacation:
                df = pd.DataFrame(export_vacation)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Urlaubsanträge exportieren (CSV)", 
                                 data=csv, 
                                 file_name="urlaubsantraege_export.csv", 
                                 mime="text/csv")
            else:
                st.info("Keine Urlaubsanträge zum Exportieren vorhanden.")
        
        elif export_type == "Krankmeldungen":
            # Krankmeldungen exportieren
            sick_leaves = load_sick_leaves()
            employees = load_employees()
            employee_map = {emp["id"]: emp["name"] for emp in employees}
            
            export_sick = []
            for sick in sick_leaves:
                export_s = {
                    "Mitarbeiter": employee_map.get(sick.get("user_id"), "Unbekannt"),
                    "Von": sick.get("start_date", "N/A"),
                    "Bis": sick.get("end_date", "N/A"),
                    "Grund": sick.get("reason", "Nicht angegeben"),
                    "ID": sick.get("id", "N/A")
                }
                export_sick.append(export_s)
            
            if export_sick:
                df = pd.DataFrame(export_sick)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Krankmeldungen exportieren (CSV)", 
                                 data=csv, 
                                 file_name="krankmeldungen_export.csv", 
                                 mime="text/csv")
            else:
                st.info("Keine Krankmeldungen zum Exportieren vorhanden.")
        
        elif export_type == "Arbeitszeiterfassung":
            # Arbeitszeiterfassung exportieren
            time_entries = load_time_entries()
            employees = load_employees()
            employee_map = {emp["id"]: emp["name"] for emp in employees}
            
            export_time = []
            for entry in time_entries:
                export_e = {
                    "Mitarbeiter": employee_map.get(entry.get("user_id"), "Unbekannt"),
                    "Check-in": entry.get("check_in", "N/A"),
                    "Check-out": entry.get("check_out", "N/A"),
                    "Dauer (Stunden)": entry.get("duration_hours", "N/A"),
                    "Standort": entry.get("location", "N/A"),
                    "Überstunden": "Ja" if entry.get("overtime", False) else "Nein",
                    "Notiz": entry.get("note", "")
                }
                export_time.append(export_e)
            
            if export_time:
                df = pd.DataFrame(export_time)
                csv = df.to_csv(index=False).encode("utf-8")
                st.download_button("📥 Arbeitszeiterfassung exportieren (CSV)", 
                                 data=csv, 
                                 file_name="arbeitszeit_export.csv", 
                                 mime="text/csv")
            else:
                st.info("Keine Arbeitszeitdaten zum Exportieren vorhanden.")
        
        elif export_type == "Alle Daten":
            # Alle Daten als JSON exportieren
            employees = load_employees()
            vacation_requests = load_vacation_requests()
            sick_leaves = load_sick_leaves()
            time_entries = load_time_entries()
            
            # Sensible Daten entfernen
            export_employees = []
            for emp in employees:
                export_emp = emp.copy()
                if "password" in export_emp:
                    export_emp["password"] = "********"  # Passwort ausblenden
                export_employees.append(export_emp)
            
            all_data = {
                "employees": export_employees,
                "vacation_requests": vacation_requests,
                "sick_leaves": sick_leaves,
                "time_entries": time_entries
            }
            
            json_str = json.dumps(all_data, indent=4, ensure_ascii=False)
            st.download_button("📥 Alle Daten exportieren (JSON)", 
                             data=json_str, 
                             file_name="worktime_app_export.json", 
                             mime="application/json")
