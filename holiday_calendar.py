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
    
    def get_holidays_for_hamburg(year):
        """Gibt alle Feiertage für Hamburg für ein bestimmtes Jahr zurück"""
        holiday_data = load_holiday_data()
        year_str = str(year)
        
        if year_str in holiday_data:
            return holiday_data[year_str]
        else:
            return {}
    
    def show_holiday_calendar_ui():
        st.title("Feiertagskalender")
        
        # CSS für einen schöneren Kalender
        st.markdown("""
        <style>
        .calendar-container {
            margin: 20px 0;
            font-family: 'Arial', sans-serif;
        }
        .month-selector {
            margin-bottom: 20px;
        }
        .calendar-table {
            width: 100%;
            border-collapse: collapse;
            border-radius: 8px;
            overflow: hidden;
            box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        }
        .calendar-table th {
            background-color: #3366cc;
            color: white;
            padding: 12px;
            text-align: center;
            font-weight: bold;
        }
        .calendar-table td {
            padding: 10px;
            text-align: center;
            border: 1px solid #e0e0e0;
            background-color: #f9f9f9;
        }
        .calendar-table td.weekend {
            background-color: #f0f0f0;
        }
        .calendar-table td.holiday {
            background-color: #ffcccc;
            font-weight: bold;
            color: #cc0000;
        }
        .calendar-table td.today {
            border: 2px solid #4CAF50;
            font-weight: bold;
        }
        .calendar-table td:hover {
            background-color: #e6e6e6;
            cursor: pointer;
        }
        .legend {
            margin-top: 20px;
            padding: 15px;
            background-color: #f9f9f9;
            border-radius: 8px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
        }
        .legend-item {
            display: flex;
            align-items: center;
            margin-bottom: 10px;
        }
        .legend-color {
            width: 20px;
            height: 20px;
            margin-right: 10px;
            border-radius: 4px;
        }
        .holiday-color {
            background-color: #ffcccc;
        }
        .weekend-color {
            background-color: #f0f0f0;
        }
        .today-color {
            background-color: #f9f9f9;
            border: 2px solid #4CAF50;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Aktuelles Jahr und Monat
        current_year = datetime.now().year
        current_month = datetime.now().month
        current_day = datetime.now().day
        
        # Jahr auswählen
        col1, col2 = st.columns([1, 3])
        with col1:
            selected_year = st.selectbox("Jahr", [current_year, current_year + 1], index=0)
        
        # Monat auswählen mit schöneren Namen
        month_names = ["Januar", "Februar", "März", "April", "Mai", "Juni", 
                      "Juli", "August", "September", "Oktober", "November", "Dezember"]
        with col2:
            selected_month_index = st.selectbox("Monat", range(len(month_names)), 
                                              format_func=lambda i: month_names[i],
                                              index=current_month-1)
            selected_month = selected_month_index + 1
        
        # Feiertage für Hamburg laden
        holidays = get_holidays_for_hamburg(selected_year)
        
        # Kalender erstellen
        cal = calendar.monthcalendar(selected_year, selected_month)
        
        # Wochentage
        weekdays = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
        
        # HTML für den Kalender
        calendar_html = f"""
        <div class="calendar-container">
            <h2>{month_names[selected_month-1]} {selected_year}</h2>
            <table class="calendar-table">
                <tr>
        """
        
        # Wochentage hinzufügen
        for day in weekdays:
            calendar_html += f"<th>{day}</th>"
        
        calendar_html += "</tr>"
        
        # Tage hinzufügen
        for week in cal:
            calendar_html += "<tr>"
            for i, day in enumerate(week):
                if day == 0:
                    # Leere Zelle
                    calendar_html += "<td></td>"
                else:
                    # Datum im Format YYYY-MM-DD
                    date_str = f"{selected_year}-{selected_month:02d}-{day:02d}"
                    
                    # Prüfen, ob es ein Feiertag ist
                    holiday_name = None
                    for holiday_date, name in holidays.items():
                        if holiday_date == date_str:
                            holiday_name = name
                    
                    # CSS-Klassen bestimmen
                    classes = []
                    
                    # Wochenende (Samstag und Sonntag)
                    if i >= 5:  # Samstag und Sonntag
                        classes.append("weekend")
                    
                    # Feiertag
                    if holiday_name:
                        classes.append("holiday")
                        
                    # Heutiger Tag
                    is_today = (selected_year == current_year and 
                               selected_month == current_month and 
                               day == current_day)
                    if is_today:
                        classes.append("today")
                    
                    # Zelle mit entsprechenden Klassen erstellen
                    class_str = " ".join(classes)
                    title_attr = f'title="{holiday_name}"' if holiday_name else ""
                    
                    calendar_html += f'<td class="{class_str}" {title_attr}>{day}</td>'
            
            calendar_html += "</tr>"
        
        calendar_html += """
            </table>
            
            <div class="legend">
                <h3>Legende:</h3>
                <div class="legend-item">
                    <div class="legend-color holiday-color"></div>
                    <div>Feiertag (mit Mauszeiger über Datum fahren für Details)</div>
                </div>
                <div class="legend-item">
                    <div class="legend-color weekend-color"></div>
                    <div>Wochenende</div>
                </div>
                <div class="legend-item">
                    <div class="legend-color today-color"></div>
                    <div>Heute</div>
                </div>
            </div>
        </div>
        """
        
        # Kalender anzeigen
        st.markdown(calendar_html, unsafe_allow_html=True)
        
        # Liste der Feiertage für das ausgewählte Jahr anzeigen
        st.subheader(f"Feiertage in Hamburg {selected_year}")
        
        # Feiertage nach Datum sortieren
        sorted_holidays = sorted(holidays.items())
        
        # Feiertage in einer schönen Tabelle anzeigen
        if sorted_holidays:
            holiday_data = []
            for date_str, name in sorted_holidays:
                # Datum formatieren
                date_obj = datetime.strptime(date_str, "%Y-%m-%d")
                formatted_date = date_obj.strftime("%d.%m.%Y")
                
                # Wochentag bestimmen
                weekday = ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"][date_obj.weekday()]
                
                holiday_data.append({
                    "Datum": formatted_date,
                    "Wochentag": weekday,
                    "Feiertag": name
                })
            
            # DataFrame erstellen und anzeigen
            df = pd.DataFrame(holiday_data)
            st.dataframe(df, use_container_width=True, hide_index=True)
        else:
            st.info(f"Keine Feiertage für Hamburg im Jahr {selected_year} gefunden.")
    
    # Rückgabe der UI-Funktion
    return show_holiday_calendar_ui

# Exportiere die Funktionen
__all__ = ['implement_holiday_calendar']
