import streamlit as st
import pandas as pd
import json
import os
from datetime import datetime, timedelta
import calendar

def implement_holiday_calendar():
    """
    Implementiert einen Feiertagskalender für Hamburg
    """
    def save_holiday_data(holiday_data):
        """Speichert Feiertagsdaten in einer JSON-Datei"""
        data_dir = "data"
        if not os.path.exists(data_dir):
            os.makedirs(data_dir)
            
        file_path = os.path.join(data_dir, "holidays.json")
        
        with open(file_path, "w") as f:
            json.dump(holiday_data, f)
    
    def load_holiday_data():
        """Lädt Feiertagsdaten aus einer JSON-Datei"""
        data_dir = "data"
        file_path = os.path.join(data_dir, "holidays.json")
        
        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                return json.load(f)
        else:
            # Standardfeiertage in Hamburg für 2025
            hamburg_holidays_2025 = {
                "2025-01-01": "Neujahr",
                "2025-04-18": "Karfreitag",
                "2025-04-21": "Ostermontag",
                "2025-05-01": "Tag der Arbeit",
                "2025-05-29": "Christi Himmelfahrt",
                "2025-06-09": "Pfingstmontag",
                "2025-10-03": "Tag der Deutschen Einheit",
                "2025-12-25": "1. Weihnachtstag",
                "2025-12-26": "2. Weihnachtstag"
            }
            
            # Standardfeiertage in Hamburg für 2026
            hamburg_holidays_2026 = {
                "2026-01-01": "Neujahr",
                "2026-04-03": "Karfreitag",
                "2026-04-06": "Ostermontag",
                "2026-05-01": "Tag der Arbeit",
                "2026-05-14": "Christi Himmelfahrt",
                "2026-05-25": "Pfingstmontag",
                "2026-10-03": "Tag der Deutschen Einheit",
                "2026-12-25": "1. Weihnachtstag",
                "2026-12-26": "2. Weihnachtstag"
            }
            
            # Beide Jahre kombinieren
            holidays = {
                "2025": hamburg_holidays_2025,
                "2026": hamburg_holidays_2026
            }
            
            save_holiday_data(holidays)
            return holidays
    
    def is_holiday(date):
        """Prüft, ob ein Datum ein Feiertag in Hamburg ist"""
        holiday_data = load_holiday_data()
        year = date.strftime("%Y")
        date_str = date.strftime("%Y-%m-%d")
        
        if year in holiday_data and date_str in holiday_data[year]:
            return True, holiday_data[year][date_str]
        
        return False, None
    
    def show_holiday_calendar_ui():
        st.title("Feiertagskalender Hamburg")
        
        # Jahr auswählen
        current_year = datetime.now().year
        selected_year = st.selectbox("Jahr auswählen", [current_year, current_year + 1], 
                                   format_func=lambda x: str(x))
        
        # Feiertagsdaten laden
        holiday_data = load_holiday_data()
        
        # Feiertage für das ausgewählte Jahr anzeigen
        if str(selected_year) in holiday_data:
            st.subheader(f"Feiertage in Hamburg {selected_year}")
            
            # Feiertage nach Datum sortieren
            sorted_holidays = sorted(holiday_data[str(selected_year)].items())
            
            # Daten für die Tabelle vorbereiten
            holiday_table_data = []
            for date_str, name in sorted_holidays:
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                weekday = date_obj.strftime("%A")
                formatted_date = date_obj.strftime("%d.%m.%Y")
                
                holiday_table_data.append({
                    "Datum": formatted_date,
                    "Wochentag": weekday,
                    "Feiertag": name
                })
            
            # Tabelle anzeigen
            if holiday_table_data:
                holiday_df = pd.DataFrame(holiday_table_data)
                st.dataframe(holiday_df, use_container_width=True)
            else:
                st.info(f"Keine Feiertage für {selected_year} definiert.")
        else:
            st.info(f"Keine Feiertagsdaten für {selected_year} vorhanden.")
        
        # Kalenderansicht
        st.subheader("Kalenderansicht")
        
        # Monat auswählen
        month = st.selectbox("Monat auswählen", range(1, 13), 
                           format_func=lambda x: calendar.month_name[x])
        
        # Kalender erstellen
        cal = calendar.monthcalendar(selected_year, month)
        
        # Wochentage
        weekdays = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
        
        # HTML für den Kalender
        calendar_html = f"""
        <style>
        .calendar {{
            width: 100%;
            border-collapse: collapse;
        }}
        .calendar th, .calendar td {{
            border: 1px solid #ddd;
            padding: 8px;
            text-align: center;
        }}
        .calendar th {{
            background-color: #f2f2f2;
        }}
        .weekend {{
            background-color: #f9f9f9;
        }}
        .holiday {{
            background-color: #ffcccc;
            font-weight: bold;
        }}
        .today {{
            border: 2px solid #4CAF50;
        }}
        </style>
        <table class="calendar">
        <tr>
        """
        
        # Wochentage hinzufügen
        for weekday in weekdays:
            calendar_html += f"<th>{weekday}</th>"
        
        calendar_html += "</tr>"
        
        # Heutiges Datum
        today = datetime.now().date()
        
        # Tage hinzufügen
        for week in cal:
            calendar_html += "<tr>"
            for day in week:
                if day == 0:
                    # Leere Zelle
                    calendar_html += "<td></td>"
                else:
                    # Datum erstellen
                    date_obj = datetime(selected_year, month, day).date()
                    date_str = date_obj.strftime("%Y-%m-%d")
                    
                    # CSS-Klassen bestimmen
                    classes = []
                    
                    # Wochenende
                    if date_obj.weekday() >= 5:  # 5 = Samstag, 6 = Sonntag
                        classes.append("weekend")
                    
                    # Feiertag
                    is_holiday_day, holiday_name = is_holiday(date_obj)
                    if is_holiday_day:
                        classes.append("holiday")
                        tooltip = f'title="{holiday_name}"'
                    else:
                        tooltip = ""
                    
                    # Heute
                    if date_obj == today:
                        classes.append("today")
                    
                    # Zelle erstellen
                    class_str = ' class="' + ' '.join(classes) + '"' if classes else ''
                    calendar_html += f'<td {class_str} {tooltip}>{day}</td>'
            
            calendar_html += "</tr>"
        
        calendar_html += "</table>"
        
        # Kalender anzeigen
        st.markdown(calendar_html, unsafe_allow_html=True)
        
        # Legende
        st.markdown("""
        **Legende:**
        - Rot: Feiertag (mit Mauszeiger über Datum fahren für Details)
        - Grau: Wochenende
        - Grüner Rahmen: Heute
        """)
    
    # Rückgabe der UI-Funktion
    return show_holiday_calendar_ui

# Exportiere die Funktionen
__all__ = ['implement_holiday_calendar']
