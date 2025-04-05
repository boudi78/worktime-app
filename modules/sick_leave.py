import streamlit as st
from datetime import date
import json, os
from modules.notifications import create_sick_leave_notification

SICK_FILE = "data/sick_leaves.json"

def save_sick_leave(entry):
    if not os.path.exists(SICK_FILE):
        with open(SICK_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

    with open(SICK_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    data.append(entry)

    with open(SICK_FILE, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

def show_sick_leave():
    st.title("🔴 Krankmeldung")

    start_datum = st.date_input("Startdatum", date.today())
    end_datum = st.date_input("Enddatum", date.today())
    grund = st.text_area("Grund der Krankmeldung")

    if st.button("Krankmeldung einreichen"):
        sick_entry = {
            "type": "sick_leave",
            "employee": st.session_state.user["name"],
            "user_id": st.session_state.user["id"],
            "date": str(start_datum),
            "end": str(end_datum),
            "note": grund
        }
        
        save_sick_leave(sick_entry)
        
        # Benachrichtigung erstellen
        create_sick_leave_notification(
            employee_name=st.session_state.user["name"],
            start_date=str(start_datum),
            end_date=str(end_datum)
        )
        
        st.success(f"✅ Krankmeldung vom {start_datum} bis {end_datum} eingereicht!")
