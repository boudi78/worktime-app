import streamlit as st
import datetime
import calendar
import pandas as pd
import numpy as np

def implement_holiday_calendar():
    """
    Implementiert einen verbesserten Feiertagskalender mit besserer visueller Darstellung.
    
    Returns:
        function: Eine Funktion, die den Feiertagskalender anzeigt.
    """
    
    def show_holiday_calendar_ui():
        st.title("Feiertagskalender")
        
        # CSS für den Kalender mit verbesserten Farben
        st.markdown("""
        <style>
        /* Allgemeine Kalender-Styles */
        .calendar-container {
            margin: 20px 0;
            font-family: Arial, sans-serif;
        }
        
        .calendar-table {
            width: 100%;
            border-collapse: collapse;
            margin-top: 20px;
            box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
        }
        
        .calendar-table th {
            background-color: #2c3e50;
            color: white;
            font-weight: bold;
            text-align: center;
            padding: 10px;
            border: 1px solid #ddd;
        }
        
        .calendar-table td {
            padding: 10px;
            text-align: center;
            border: 1px solid #ddd;
            background-color: #ecf0f1;
            color: #333;
            height: 60px;
            vertical-align: top;
            position: relative;
        }
        
        /* Spezifische Styles für verschiedene Tagestypen */
        .calendar-table td.holiday {
            background-color: #e74c3c !important;
            font-weight: bold;
            color: white !important;
        }
        
        .calendar-table td.weekend {
            background-color: #bdc3c7 !important;
        }
        
        .calendar-table td.today {
            border: 3px solid #27ae60 !important;
            font-weight: bold;
            background-color: #d5f5e3 !important;
        }
        </style>
        """, unsafe_allow_html=True)
        
        # Jahr und Monat Auswahl
        col1, col2 = st.columns(2)
        
        with col1:
            year = st.selectbox("Jahr", range(2020, 2030), index=5, key="holiday_year_select")  # 2025 als Standard
        
        with col2:
            months = ["Januar", "Februar", "März", "April", "Mai", "Juni", 
                     "Juli", "August", "September", "Oktober", "November", "Dezember"]
            month = st.selectbox("Monat", months, index=datetime.datetime.now().month - 1, key="holiday_month_select")
        
        # Monatsnummer ermitteln
        month_num = months.index(month) + 1
        
        # Feiertage in Deutschland (Hamburg) für das ausgewählte Jahr
        holidays = get_german_holidays(year)
        
        # Kalender anzeigen
        display_calendar(year, month_num, holidays)
        
        # Legende mit Streamlit-Elementen anzeigen (nicht mit HTML/CSS)
        st.subheader("Legende:")
        
        # Verwende Streamlit-Spalten für die Legende
        col1, col2, col3, col4 = st.columns(4)
        
        with col1:
            st.markdown('<div style="width:24px;height:24px;background-color:#e74c3c;margin-bottom:10px;"></div>', unsafe_allow_html=True)
            st.write("Feiertag")
            
        with col2:
            st.markdown('<div style="width:24px;height:24px;background-color:#bdc3c7;margin-bottom:10px;"></div>', unsafe_allow_html=True)
            st.write("Wochenende")
            
        with col3:
            st.markdown('<div style="width:24px;height:24px;background-color:#d5f5e3;border:3px solid #27ae60;margin-bottom:10px;"></div>', unsafe_allow_html=True)
            st.write("Heute")
            
        with col4:
            st.markdown('<div style="width:24px;height:24px;background-color:#ecf0f1;margin-bottom:10px;"></div>', unsafe_allow_html=True)
            st.write("Werktag")
        
        # Tabelle mit allen Feiertagen des Jahres
        st.subheader(f"Feiertage in Hamburg {year}")
        
        # Feiertage in DataFrame konvertieren für bessere Darstellung
        holidays_df = pd.DataFrame(
            [(date.strftime("%d.%m.%Y"), calendar.day_name[date.weekday()], name) 
             for date, name in holidays.items()],
            columns=["Datum", "Wochentag", "Feiertag"]
        )
        
        # Verwende die Standard-Streamlit-Tabelle
        st.table(holidays_df)
    
    def get_german_holidays(year):
        """
        Gibt die deutschen Feiertage für das angegebene Jahr zurück.
        
        Args:
            year (int): Das Jahr, für das die Feiertage zurückgegeben werden sollen.
            
        Returns:
            dict: Ein Dictionary mit Datum als Schlüssel und Feiertagsname als Wert.
        """
        holidays = {}
        
        # Feste Feiertage
        holidays[datetime.date(year, 1, 1)] = "Neujahr"
        holidays[datetime.date(year, 5, 1)] = "Tag der Arbeit"
        holidays[datetime.date(year, 10, 3)] = "Tag der Deutschen Einheit"
        holidays[datetime.date(year, 12, 25)] = "1. Weihnachtstag"
        holidays[datetime.date(year, 12, 26)] = "2. Weihnachtstag"
        
        # Bewegliche Feiertage basierend auf Ostern
        easter = calculate_easter(year)
        holidays[easter] = "Ostersonntag"
        holidays[easter + datetime.timedelta(days=-2)] = "Karfreitag"
        holidays[easter + datetime.timedelta(days=1)] = "Ostermontag"
        holidays[easter + datetime.timedelta(days=39)] = "Christi Himmelfahrt"
        holidays[easter + datetime.timedelta(days=49)] = "Pfingstsonntag"
        holidays[easter + datetime.timedelta(days=50)] = "Pfingstmontag"
        
        # Reformationstag (nur in einigen Bundesländern, inkl. Hamburg)
        holidays[datetime.date(year, 10, 31)] = "Reformationstag"
        
        return holidays
    
    def calculate_easter(year):
        """
        Berechnet das Datum des Ostersonntags für ein gegebenes Jahr.
        Basierend auf dem Gauss-Algorithmus.
        
        Args:
            year (int): Das Jahr, für das Ostern berechnet werden soll.
            
        Returns:
            datetime.date: Das Datum des Ostersonntags.
        """
        a = year % 19
        b = year // 100
        c = year % 100
        d = b // 4
        e = b % 4
        f = (b + 8) // 25
        g = (b - f + 1) // 3
        h = (19 * a + b - d - g + 15) % 30
        i = c // 4
        k = c % 4
        l = (32 + 2 * e + 2 * i - h - k) % 7
        m = (a + 11 * h + 22 * l) // 451
        month = (h + l - 7 * m + 114) // 31
        day = ((h + l - 7 * m + 114) % 31) + 1
        
        return datetime.date(year, month, day)
    
    def display_calendar(year, month, holidays):
        """
        Zeigt einen Kalender für den angegebenen Monat und das Jahr an.
        
        Args:
            year (int): Das Jahr.
            month (int): Der Monat (1-12).
            holidays (dict): Ein Dictionary mit Feiertagen.
        """
        # Monatsnamen und Wochentagsnamen
        month_name = calendar.month_name[month]
        weekday_names = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
        
        # Kalender erstellen
        cal = calendar.monthcalendar(year, month)
        
        # Heutiges Datum
        today = datetime.date.today()
        
        # HTML für den Kalender
        html = f"""
        <div class="calendar-container">
            <h2>{month_name} {year}</h2>
            <table class="calendar-table">
                <tr>
        """
        
        # Wochentagsüberschriften
        for weekday in weekday_names:
            html += f"<th>{weekday}</th>"
        
        html += "</tr>"
        
        # Tage im Kalender
        for week in cal:
            html += "<tr>"
            for day in week:
                if day == 0:
                    # Leere Zelle für Tage außerhalb des Monats
                    html += "<td style='background-color: #f8f9fa;'></td>"
                else:
                    date = datetime.date(year, month, day)
                    
                    # CSS-Klassen für verschiedene Tagestypen
                    classes = []
                    
                    # Prüfen, ob es ein Feiertag ist
                    holiday_name = holidays.get(date, "")
                    if holiday_name:
                        classes.append("holiday")
                        tooltip = f'title="{holiday_name}"'
                    else:
                        tooltip = ""
                    
                    # Prüfen, ob es ein Wochenende ist
                    if date.weekday() >= 5:  # 5 = Samstag, 6 = Sonntag
                        classes.append("weekend")
                    
                    # Prüfen, ob es heute ist
                    if date == today:
                        classes.append("today")
                    
                    class_str = f'class="{" ".join(classes)}"' if classes else ""
                    
                    html += f'<td {class_str} {tooltip}>{day}</td>'
            
            html += "</tr>"
        
        html += """
            </table>
        </div>
        """
        
        st.markdown(html, unsafe_allow_html=True)
    
    return show_holiday_calendar_ui
