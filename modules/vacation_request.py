# modules/vacation_request.py

import streamlit as st
import pandas as pd
from modules.utils import load_employees, load_vacation_requests, load_sick_leaves, calculate_absence_statistics

def show_absence_statistics():
    st.title("📊 Abwesenheitsstatistik")

    # Load data
    employees = load_employees()
    vacation_requests = load_vacation_requests()
    sick_leaves = load_sick_leaves()

    # Calculate statistics
    df = calculate_absence_statistics(employees, vacation_requests, sick_leaves)

    # Display table
    st.subheader("Urlaub & Kranktage pro Monat und Mitarbeiter")
    st.dataframe(df, use_container_width=True)

    # Download as CSV
    csv = df.to_csv(index=False).encode('utf-8')
    st.download_button(
        label="📥 CSV herunterladen",
        data=csv,
        file_name="abwesenheitsstatistik.csv",
        mime="text/csv"
    )
