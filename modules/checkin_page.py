# checkin_page.py
import streamlit as st
import uuid
from datetime import datetime
from modules.utils import save_time_entry, LOCATION_CODES

def show_checkin_checkout():
    st.title("⏱️ Check-In / Check-Out")

    # Arbeitsort Auswahl
    location = st.selectbox(
        "Arbeitsort auswählen",
        list(LOCATION_CODES.keys()),  # Use keys from the dict
        key="work_location",
    )
    location_code = LOCATION_CODES[location] # More direct code

    st.markdown("---")

    # Check-in Logik
    if st.session_state.get("checkin_time") is None:  # Use .get() to avoid AttributeErrors
        if st.button("✅ Jetzt einchecken"):
            st.session_state.checkin_time = datetime.now()
            st.session_state.location = location_code
            st.success(
                f"Eingecheckt um {st.session_state.checkin_time.strftime('%H:%M:%S')} ({location})"
            )
            st.rerun() # Add this line here
    else:
        st.info(
            f"Eingecheckt um: {st.session_state.checkin_time.strftime('%H:%M:%S')} ({st.session_state.location})"
        )

        note = st.text_area("📝 Kommentar (optional)")

        if st.button("🚪 Auschecken"):
            checkout_time = datetime.now()
            duration = checkout_time - st.session_state.checkin_time
            hours = round(duration.total_seconds() / 3600, 2)

            st.success(f"Ausgecheckt um {checkout_time.strftime('%H:%M:%S')}")
            st.info(f"Arbeitszeit: {hours} Stunden\nKommentar: {note if note else '–'}")

            # Overtime Calculation
            checkin_datetime = st.session_state.checkin_time
            is_weekend = checkin_datetime.weekday() >= 5  # Saturday=5, Sunday=6
            is_overtime = is_weekend or hours > 8

            # Save Time Entry (Moved inside the if block)
            if st.session_state.get("user") is not None:  # Check if user is logged in
                entry = {
                    "id": str(uuid.uuid4()),
                    "user_id": st.session_state.user["id"],
                    "check_in": st.session_state.checkin_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "check_out": checkout_time.strftime("%Y-%m-%d %H:%M:%S"),
                    "duration_hours": hours,
                    "location": st.session_state.location,
                    "note": note,
                    "overtime": is_overtime,  # Add overtime flag
                }
                save_time_entry(entry)
                st.success("Time entry saved!") #optional confirmation
            else:
                st.warning("User not logged in. Time entry not saved.")

            # Reset
            st.session_state.checkin_time = None
            st.session_state.location = None
            st.rerun() #add this line here
