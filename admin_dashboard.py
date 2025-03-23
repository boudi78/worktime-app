menu_items = ["Urlaub & Krankheit", "Feiertagskalender", "Export", "Rollenverwaltung"]
import streamlit as st
import pandas as pd

# Admin-Dashboard für Team-Übersicht
st.title("Admin-Dashboard")

if st.session_state.get("is_admin", False):
    st.write("Willkommen im Admin-Dashboard! Hier siehst du die Team-Übersicht.")

    # Dummy-Daten (normalerweise aus Datenbank oder JSON)
    data = {
        "Team": ["Team 1", "Team 2", "Team 3"],
        "Arbeitsstunden": [120, 95, 80],
        "Lager Nutzung": [30, 25, 0]  # Team 3 nutzt kein Lager
    }

    df = pd.DataFrame(data)

    st.subheader("Team-Übersicht")
    st.bar_chart(df.set_index("Team"))

    st.subheader("Lager-Auswertung")
    st.bar_chart(df[["Team", "Lager Nutzung"]].set_index("Team"))

else:
    st.warning("Du hast keine Berechtigung, das Admin-Dashboard zu sehen.")
