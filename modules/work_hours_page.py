# modules/work_hours_page.py
import streamlit as st
import pandas as pd

def work_hours_page():
    st.title("Arbeitszeiten")

    # Beispiel-Daten für Arbeitszeiten (normalerweise aus der DB oder einem anderen Datenspeicher)
    data = [
        {"name": "Max Mustermann", "datum": "2025-02-21", "arbeitszeit": "8h", "ueberstunden": "1h"},
        {"name": "Erika Musterfrau", "datum": "2025-02-21", "arbeitszeit": "7h", "ueberstunden": "0h"}
    ]

    # Zeige die Tabelle der Arbeitszeiten an
    df = pd.DataFrame(data)
    st.table(df)

    # CSV-Export-Funktion
    def export_csv(data):
        df = pd.DataFrame(data)  # DataFrame erstellen
        csv_data = df.to_csv(index=False)  # CSV-Datei ohne Index speichern
        st.download_button(
            label="CSV herunterladen",  # Button Text
            data=csv_data,  # CSV-Daten
            file_name="arbeitszeiten.csv",  # Dateiname
            mime="text/csv"  # MIME-Typ
        )

    # Füge den CSV-Export-Button hinzu
    export_csv(data)
