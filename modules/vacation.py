import streamlit as st
from datetime import date
import json
import os
from modules.utils import calculate_remaining_vacation
from modules.utils import load_vacation_requests
from modules.utils import load_employees
from modules.notifications import create_vacation_notification

# Datei für Urlaubsanträge
VACATION_FILE = "data/vacation_requests.json"

def save_vacation(entry):
    """Speichert einen Urlaubsantrag in der Datei."""
    if not os.path.exists(VACATION_FILE):
        with open(VACATION_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

    with open(VACATION_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    data.append(entry)

    with open(VACATION_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def display_vacation_page():
    st.title("🟡 Urlaubsantrag")

    # Urlaubskonto anzeigen
    user_id = st.session_state.user["id"]
    remaining_days = calculate_remaining_vacation(user_id)
    
    # Mitarbeiterdaten laden
    employees = load_employees()
    employee = next((emp for emp in employees if emp["id"] == user_id), None)
    if not employee:
        st.error(f"Mitarbeiter mit ID {user_id} nicht gefunden.")
        return
        
    # Urlaubsanspruch bestimmen
    if employee.get("role") == "buero":
        vacation_days_entitled = 27
    else:
        vacation_days_entitled = 26
        
    st.markdown(f"Verbleibende Urlaubstage: {remaining_days} / {vacation_days_entitled}")

    st.markdown("---")

    # Urlaubsantragsformular
    start_datum = st.date_input("Startdatum", date.today())
    end_datum = st.date_input("Enddatum", date.today())
    grund = st.text_area("Grund für den Urlaubsantrag")

    if st.button("Urlaubsantrag stellen"):
        vacation_entry = {
            "type": "vacation",
            "user_id": st.session_state.user["id"],
            "employee": st.session_state.user["name"],
            "start_date": str(start_datum),
            "end_date": str(end_datum),
            "note": grund,
            "status": "pending"
        }

        save_vacation(vacation_entry)
        
        # Benachrichtigung erstellen
        create_vacation_notification(
            employee_name=st.session_state.user["name"],
            start_date=str(start_datum),
            end_date=str(end_datum)
        )

        st.success(f"✅ Urlaubsantrag vom {start_datum} bis {end_datum} eingereicht!")
