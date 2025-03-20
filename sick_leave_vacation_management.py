import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import calendar

# Import der Datenpersistenz-Funktionen
from data_persistence import save_all_data, load_employees

def implement_sick_leave_vacation_management():
    """
    Implementiert die Krankmeldungs- und Urlaubsverwaltung
    """
    def save_leave_data(leave_data):
        """Speichert Urlaubs- und Krankheitsdaten in einer JSON-Datei"""
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            
        file_path = os.path.join(data_dir, "leave_data.json")
        
        with open(file_path, "w") as f:
            json.dump(leave_data, f)
    
    def load_leave_data():
        """Lädt Urlaubs- und Krankheitsdaten aus einer JSON-Datei"""
        data_dir = "data"
        file_path = os.path.join(data_dir, "leave_data.json")
        
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
        else:
            return {
                "vacation": {},
                "sick_leave": {}
            }
    
    def calculate_vacation_days(employee_id):
        """Berechnet die verbleibenden Urlaubstage für einen Mitarbeiter"""
        leave_data = load_leave_data()
        
        # Standardurlaubstage pro Jahr
        standard_vacation_days = 30
        
        # Mitarbeiterdaten laden
        employees = load_employees()
        employee = next((emp for emp in employees if emp["id"] == employee_id), None)
        
        if not employee:
            return 0, 0
        
        # Urlaubsdaten für den Mitarbeiter initialisieren, falls nicht vorhanden
        if str(employee_id) not in leave_data["vacation"]:
            leave_data["vacation"][str(employee_id)] = {
                "total_days": standard_vacation_days,
                "used_days": 0,
                "approved_requests": [],
                "pending_requests": []
            }
            save_leave_data(leave_data)
        
        # Verbleibende Urlaubstage berechnen
        total_days = leave_data["vacation"][str(employee_id)]["total_days"]
        used_days = leave_data["vacation"][str(employee_id)]["used_days"]
        remaining_days = total_days - used_days
        
        return remaining_days, total_days
    
    def show_leave_management_ui():
        st.title("Urlaubs- und Krankmeldungsverwaltung")
        
        # Benutzer-ID abrufen
        user_id = st.session_state.get("user_id")
        if not user_id:
            st.warning("Bitte melden Sie sich an, um diese Funktion zu nutzen.")
            return
        
        # Tabs für Urlaub und Krankmeldung
        tab1, tab2, tab3 = st.tabs(["Urlaubsantrag", "Krankmeldung", "Übersicht"])
        
        with tab1:
            st.subheader("Urlaubsantrag stellen")
            
            # Verbleibende Urlaubstage anzeigen
            remaining_days, total_days = calculate_vacation_days(user_id)
            st.write(f"Verbleibende Urlaubstage: {remaining_days} von {total_days}")
            
            # Urlaubszeitraum auswählen
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Erster Urlaubstag", min_value=datetime.now().date())
            with col2:
                end_date = st.date_input("Letzter Urlaubstag", min_value=start_date)
            
            # Urlaubstage berechnen (ohne Wochenenden)
            if start_date and end_date:
                vacation_days = 0
                current_date = start_date
                while current_date <= end_date:
                    # Wochenenden ausschließen (5 = Samstag, 6 = Sonntag)
                    if current_date.weekday() < 5:
                        vacation_days += 1
                    current_date += timedelta(days=1)
                
                st.write(f"Anzahl der Arbeitstage: {vacation_days}")
            
            # Urlaubsgrund
            vacation_reason = st.text_area("Grund (optional)")
            
            # Urlaubsantrag absenden
            if st.button("Urlaubsantrag absenden"):
                if vacation_days > remaining_days:
                    st.error(f"Sie haben nicht genügend Urlaubstage übrig. Verbleibend: {remaining_days}, Beantragt: {vacation_days}")
                else:
                    # Urlaubsdaten laden
                    leave_data = load_leave_data()
                    
                    # Neuen Urlaubsantrag erstellen
                    new_request = {
                        "id": len(leave_data["vacation"].get(str(user_id), {}).get("pending_requests", [])) + 
                              len(leave_data["vacation"].get(str(user_id), {}).get("approved_requests", [])) + 1,
                        "start_date": start_date.strftime("%Y-%m-%d"),
                        "end_date": end_date.strftime("%Y-%m-%d"),
                        "days": vacation_days,
                        "reason": vacation_reason,
                        "status": "pending",
                        "request_date": datetime.now().strftime("%Y-%m-%d")
                    }
                    
                    # Mitarbeiter in Urlaubsdaten initialisieren, falls nicht vorhanden
                    if str(user_id) not in leave_data["vacation"]:
                        leave_data["vacation"][str(user_id)] = {
                            "total_days": 30,  # Standardurlaubstage
                            "used_days": 0,
                            "approved_requests": [],
                            "pending_requests": []
                        }
                    
                    # Urlaubsantrag hinzufügen
                    leave_data["vacation"][str(user_id)]["pending_requests"].append(new_request)
                    
                    # Urlaubsdaten speichern
                    save_leave_data(leave_data)
                    
                    st.success("Urlaubsantrag erfolgreich eingereicht!")
        
        with tab2:
            st.subheader("Krankmeldung einreichen")
            
            # Krankheitszeitraum auswählen
            col1, col2 = st.columns(2)
            with col1:
                sick_start_date = st.date_input("Erster Krankheitstag", key="sick_start", min_value=datetime.now().date() - timedelta(days=30))
            with col2:
                sick_end_date = st.date_input("Letzter Krankheitstag (falls bekannt)", key="sick_end", min_value=sick_start_date)
            
            # Krankheitstage berechnen
            if sick_start_date and sick_end_date:
                sick_days = (sick_end_date - sick_start_date).days + 1
                st.write(f"Anzahl der Krankheitstage: {sick_days}")
            
            # Arztbesuch
            has_doctor_note = st.checkbox("Ärztliche Bescheinigung vorhanden")
            
            # Krankheitsgrund
            sick_reason = st.text_area("Grund (optional)", key="sick_reason")
            
            # Krankmeldung absenden
            if st.button("Krankmeldung einreichen"):
                # Urlaubsdaten laden
                leave_data = load_leave_data()
                
                # Neue Krankmeldung erstellen
                new_sick_leave = {
                    "id": len(leave_data["sick_leave"].get(str(user_id), [])) + 1,
                    "start_date": sick_start_date.strftime("%Y-%m-%d"),
                    "end_date": sick_end_date.strftime("%Y-%m-%d"),
                    "days": sick_days,
                    "has_doctor_note": has_doctor_note,
                    "reason": sick_reason,
                    "report_date": datetime.now().strftime("%Y-%m-%d")
                }
                
                # Mitarbeiter in Krankheitsdaten initialisieren, falls nicht vorhanden
                if str(user_id) not in leave_data["sick_leave"]:
                    leave_data["sick_leave"][str(user_id)] = []
                
                # Krankmeldung hinzufügen
                leave_data["sick_leave"][str(user_id)].append(new_sick_leave)
                
                # Urlaubsdaten speichern
                save_leave_data(leave_data)
                
                st.success("Krankmeldung erfolgreich eingereicht!")
        
        with tab3:
            st.subheader("Übersicht")
            
            # Urlaubsdaten laden
            leave_data = load_leave_data()
            
            # Urlaubsanträge anzeigen
            st.write("### Urlaubsanträge")
            
            if str(user_id) in leave_data["vacation"]:
                # Ausstehende Anträge
                pending_requests = leave_data["vacation"][str(user_id)].get("pending_requests", [])
                if pending_requests:
                    st.write("#### Ausstehende Anträge")
                    for request in pending_requests:
                        with st.expander(f"{request['start_date']} bis {request['end_date']} ({request['days']} Tage)"):
                            st.write(f"Status: {request['status']}")
                            st.write(f"Beantragt am: {request['request_date']}")
                            if request.get("reason"):
                                st.write(f"Grund: {request['reason']}")
                
                # Genehmigte Anträge
                approved_requests = leave_data["vacation"][str(user_id)].get("approved_requests", [])
                if approved_requests:
                    st.write("#### Genehmigte Anträge")
                    for request in sorted(approved_requests, key=lambda x: x['start_date'], reverse=True):
                        with st.expander(f"{request['start_date']} bis {request['end_date']} ({request['days']} Tage)"):
                            st.write(f"Status: {request['status']}")
                            st.write(f"Beantragt am: {request['request_date']}")
                            st.write(f"Genehmigt am: {request.get('approval_date', 'Unbekannt')}")
                            if request.get("reason"):
                                st.write(f"Grund: {request['reason']}")
            else:
                st.info("Keine Urlaubsanträge vorhanden.")
            
            # Krankmeldungen anzeigen
            st.write("### Krankmeldungen")
            
            if str(user_id) in leave_data["sick_leave"]:
                sick_leaves = leave_data["sick_leave"][str(user_id)]
                if sick_leaves:
                    for sick_leave in sorted(sick_leaves, key=lambda x: x['start_date'], reverse=True):
                        with st.expander(f"{sick_leave['start_date']} bis {sick_leave['end_date']} ({sick_leave['days']} Tage)"):
                            st.write(f"Gemeldet am: {sick_leave['report_date']}")
                            st.write(f"Ärztliche Bescheinigung: {'Ja' if sick_leave['has_doctor_note'] else 'Nein'}")
                            if sick_leave.get("reason"):
                                st.write(f"Grund: {sick_leave['reason']}")
            else:
                st.info("Keine Krankmeldungen vorhanden.")
    
    def show_admin_leave_management_ui():
        st.title("Urlaubs- und Krankmeldungsverwaltung (Admin)")
        
        # Prüfen, ob der Benutzer Admin ist
        if not st.session_state.get("is_admin", False):
            st.warning("Sie haben keine Berechtigung, diese Seite zu sehen.")
            return
        
        # Urlaubsdaten laden
        leave_data = load_leave_data()
        
        # Mitarbeiterdaten laden
        employees = load_employees()
        
        # Tabs für Urlaubsanträge und Krankmeldungen
        tab1, tab2 = st.tabs(["Urlaubsanträge", "Krankmeldungen"])
        
        with tab1:
            st.subheader("Urlaubsanträge verwalten")
            
            # Ausstehende Urlaubsanträge sammeln
            pending_requests = []
            for user_id, vacation_data in leave_data.get("vacation", {}).items():
                for request in vacation_data.get("pending_requests", []):
                    # Mitarbeitername finden
                    employee = next((emp for emp in employees if str(emp["id"]) == user_id), None)
                    if employee:
                        request["employee_name"] = employee["name"]
                        request["employee_id"] = user_id
                        pending_requests.append(request)
            
            # Ausstehende Anträge anzeigen
            if pending_requests:
                st.write("#### Ausstehende Anträge")
                for request in sorted(pending_requests, key=lambda x: x['start_date']):
                    with st.expander(f"{request['employee_name']}: {request['start_date']} bis {request['end_date']} ({request['days']} Tage)"):
                        st.write(f"Beantragt am: {request['request_date']}")
                        if request.get("reason"):
                            st.write(f"Grund: {request['reason']}")
                        
                        # Genehmigen/Ablehnen-Buttons
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Genehmigen", key=f"approve_{request['employee_id']}_{request['id']}"):
                                # Urlaubsantrag genehmigen
                                user_id = request["employee_id"]
                                request_id = request["id"]
                                
                                # Antrag aus pending_requests entfernen
                                leave_data["vacation"][user_id]["pending_requests"] = [
                                    req for req in leave_data["vacation"][user_id]["pending_requests"]
                                    if req["id"] != request_id
                                ]
                                
                                # Antrag zu approved_requests hinzufügen
                                request["status"] = "approved"
                                request["approval_date"] = datetime.now().strftime("%Y-%m-%d")
                                leave_data["vacation"][user_id]["approved_requests"].append(request)
                                
                                # Verwendete Urlaubstage aktualisieren
                                leave_data["vacation"][user_id]["used_days"] += request["days"]
                                
                                # Urlaubsdaten speichern
                                save_leave_data(leave_data)
                                
                                st.success(f"Urlaubsantrag für {request['employee_name']} genehmigt!")
                                st.rerun()
                        with col2:
                            if st.button("Ablehnen", key=f"reject_{request['employee_id']}_{request['id']}"):
                                # Urlaubsantrag ablehnen
                                user_id = request["employee_id"]
                                request_id = request["id"]
                                
                                # Antrag aus pending_requests entfernen
                                leave_data["vacation"][user_id]["pending_requests"] = [
                                    req for req in leave_data["vacation"][user_id]["pending_requests"]
                                    if req["id"] != request_id
                                ]
                                
                                # Urlaubsdaten speichern
                                save_leave_data(leave_data)
                                
                                st.success(f"Urlaubsantrag für {request['employee_name']} abgelehnt!")
                                st.rerun()
            else:
                st.info("Keine ausstehenden Urlaubsanträge vorhanden.")
            
            # Urlaubsübersicht für alle Mitarbeiter
            st.write("#### Urlaubsübersicht")
            
            # Daten für die Übersicht sammeln
            overview_data = []
            for employee in employees:
                user_id = str(employee["id"])
                if user_id in leave_data.get("vacation", {}):
                    vacation_data = leave_data["vacation"][user_id]
                    total_days = vacation_data.get("total_days", 30)
                    used_days = vacation_data.get("used_days", 0)
                    remaining_days = total_days - used_days
                    
                    overview_data.append({
                        "Mitarbeiter": employee["name"],
                        "Gesamt": total_days,
                        "Verwendet": used_days,
                        "Verbleibend": remaining_days
                    })
            
            # Übersicht als Tabelle anzeigen
            if overview_data:
                overview_df = pd.DataFrame(overview_data)
                st.dataframe(overview_df)
            else:
                st.info("Keine Urlaubsdaten vorhanden.")
        
        with tab2:
            st.subheader("Krankmeldungen einsehen")
            
            # Krankmeldungen sammeln
            all_sick_leaves = []
            for user_id, sick_leaves in leave_data.get("sick_leave", {}).items():
                for sick_leave in sick_leaves:
                    # Mitarbeitername finden
                    employee = next((emp for emp in employees if str(emp["id"]) == user_id), None)
                    if employee:
                        sick_leave["employee_name"] = employee["name"]
                        all_sick_leaves.append(sick_leave)
            
            # Krankmeldungen anzeigen
            if all_sick_leaves:
                # Nach Datum sortieren (neueste zuerst)
                all_sick_leaves.sort(key=lambda x: x['start_date'], reverse=True)
                
                for sick_leave in all_sick_leaves:
                    with st.expander(f"{sick_leave['employee_name']}: {sick_leave['start_date']} bis {sick_leave['end_date']} ({sick_leave['days']} Tage)"):
                        st.write(f"Gemeldet am: {sick_leave['report_date']}")
                        st.write(f"Ärztliche Bescheinigung: {'Ja' if sick_leave['has_doctor_note'] else 'Nein'}")
                        if sick_leave.get("reason"):
                            st.write(f"Grund: {sick_leave['reason']}")
            else:
                st.info("Keine Krankmeldungen vorhanden.")
    
    # Rückgabe der UI-Funktionen
    return show_leave_management_ui, show_admin_leave_management_ui

# Exportiere die Funktionen
__all__ = ['implement_sick_leave_vacation_management']
