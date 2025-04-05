import streamlit as st
import pandas as pd
from datetime import datetime, timedelta
import calendar
from modules.utils import load_sick_leaves, load_vacation_requests, load_employees, load_time_entries
import locale

try:
    locale.setlocale(locale.LC_TIME, 'de_DE.UTF-8')  # für Linux/mac
except locale.Error:
    try:
        locale.setlocale(locale.LC_TIME, 'deu')  # für Windows, fallback
    except locale.Error:
        pass  # Wenn beide fehlschlagen, Standard-Locale verwenden

# --------------------
# Daten vorbereiten
# --------------------

# Feiertage in Hamburg (mit Feiertagsnamen)
feiertage = {
    "2025-01-01": "Neujahr",
    "2025-04-18": "Karfreitag",
    "2025-05-01": "Tag der Arbeit",
    "2025-05-29": "Himmelfahrt",
    "2025-06-09": "Pfingstmontag",
    "2025-10-03": "Tag der Deutschen Einheit",
    "2025-12-25": "Weihnachten",
    "2025-12-26": "2. Weihnachtstag",
    "2024-01-01": "Neujahr",
    "2024-03-29": "Karfreitag",
    "2024-05-01": "Tag der Arbeit",
    "2024-05-09": "Himmelfahrt",
    "2024-05-20": "Pfingstmontag",
    "2024-10-03": "Tag der Deutschen Einheit",
    "2024-12-25": "Weihnachten",
    "2024-12-26": "2. Weihnachtstag"
}

# Helper Functions
def ist_feiertag(datum, feiertage):
    return datum.strftime("%Y-%m-%d") in feiertage

def ist_urlaub(datum, urlaub_data):
    for vacation in urlaub_data:
        try:
            start_key = 'start_date' if 'start_date' in vacation else 'date'
            end_key = 'end_date' if 'end_date' in vacation else 'end'

            if start_key not in vacation or end_key not in vacation:
                continue

            vacation_start = datetime.strptime(vacation.get(start_key), '%Y-%m-%d').date()
            vacation_end = datetime.strptime(vacation.get(end_key), '%Y-%m-%d').date()

            if vacation_start <= datum.date() <= vacation_end:
                user_id = vacation.get('user_id', vacation.get('employee_id', None))
                return True, user_id
        except Exception as e:
            print(f"Fehler bei Urlaubsdaten: {e}")
            continue
    return False, None

def ist_krank(datum, krank_data):
    for sick_leave in krank_data:
        try:
            start_key = 'start_date' if 'start_date' in sick_leave else 'date'
            end_key = 'end_date' if 'end_date' in sick_leave else 'end'

            if start_key not in sick_leave or end_key not in sick_leave:
                continue

            sick_start = datetime.strptime(sick_leave.get(start_key), '%Y-%m-%d').date()
            sick_end = datetime.strptime(sick_leave.get(end_key), '%Y-%m-%d').date()

            if sick_start <= datum.date() <= sick_end:
                user_id = sick_leave.get('user_id', None)
                if user_id is None and 'employee' in sick_leave:
                    employees = load_employees()
                    for emp in employees:
                        if emp.get('name') == sick_leave['employee']:
                            user_id = emp.get('id')
                            break
                return True, user_id
        except Exception as e:
            print(f"Fehler bei Krankheitsdaten: {e}")
            continue
    return False, None

def show_calendar():
    st.title("📅 Kalender")
    
    # CSS für Kalender direkt einfügen
    st.markdown("""
    <style>
    .calendar-table {
        width: 100%;
        border-collapse: collapse;
        margin-bottom: 20px;
    }
    .calendar-table th, .calendar-table td {
        border: 1px solid #ddd;
        padding: 8px;
        text-align: center;
    }
    .calendar-table th {
        background-color: #2C3E50 !important;
        color: #FFFFFF !important;
        font-weight: bold;
        font-size: 16px;
        padding: 10px;
    }
    .holiday {
        background-color: #FFF1F1 !important;
        color: #FF5733 !important;
        font-weight: bold;
    }
    .vacation {
        background-color: #E6FFEC !important;
        color: #33FF57 !important;
        font-weight: bold;
    }
    .sick {
        background-color: #FFEBE5 !important;
        color: #FF5733 !important;
        font-weight: bold;
    }
    .overtime {
        background-color: #FFF5CC !important;
        color: #FFC300 !important;
        font-weight: bold;
    }
    .weekend {
        background-color: #F0F0F0 !important;
        color: #8C8C8C !important;
        font-weight: bold;
    }
    .today {
        background-color: #2C3E50 !important;
        color: white !important;
        font-weight: bold;
    }
    .legend-container {
        display: flex;
        flex-wrap: wrap;
        gap: 10px;
        margin-bottom: 20px;
    }
    .legend-item {
        display: flex;
        align-items: center;
        margin-right: 15px;
    }
    .legend-color {
        width: 20px;
        height: 20px;
        margin-right: 5px;
        border: 1px solid #ccc;
    }
    </style>
    """, unsafe_allow_html=True)

    # Load employee data and create user map
    employees = load_employees()
    user_map = {emp["id"]: emp["name"] for emp in employees}
    
    # Load sick leave and vacation data
    sick_leaves = load_sick_leaves()
    vacation_requests = load_vacation_requests()

    # Load time entries and create overtime mapping
    time_entries = load_time_entries()
    overtime_map = {}
    for entry in time_entries:
        try:
            entry_date = datetime.strptime(entry["check_in"].split(" ")[0], "%Y-%m-%d").date()
            if "overtime" not in entry:
                check_in = datetime.strptime(entry["check_in"], "%Y-%m-%d %H:%M:%S")
                check_out = datetime.strptime(entry["check_out"], "%Y-%m-%d %H:%M:%S")
                hours = (check_out - check_in).total_seconds() / 3600
                is_overtime = hours > 8
                overtime_map[(entry["user_id"], entry_date)] = is_overtime
            else:
                overtime_map[(entry["user_id"], entry_date)] = entry.get("overtime", False)
        except Exception as e:
            print(f"Fehler beim Verarbeiten von Überstunden: {e}")
            continue

    # Monat auswählen
    heute = datetime.today()
    col1, col2 = st.columns(2)
    
    with col1:
        monat = st.selectbox("📅 Monat", 
                           options=list(range(1, 13)), 
                           index=heute.month - 1,
                           format_func=lambda m: ["Januar", "Februar", "März", "April", "Mai", "Juni", 
                                                "Juli", "August", "September", "Oktober", "November", "Dezember"][m-1])
    
    with col2:
        jahr = st.selectbox("📅 Jahr", 
                          options=list(range(2024, 2027)), 
                          index=1 if heute.year == 2025 else 0 if heute.year == 2024 else 2)

    # Filter-Checkboxen
    col1, col2, col3 = st.columns(3)
    
    with col1:
        urlaub_filter = st.checkbox("Urlaub anzeigen", value=True)
    
    with col2:
        krank_filter = st.checkbox("Krankmeldungen anzeigen", value=True)
    
    with col3:
        feiertag_filter = st.checkbox("Feiertage anzeigen", value=True)

    # Employee Filter
    names = [emp["name"] for emp in employees]
    selected_user = st.selectbox("Mitarbeiter filtern", ["Alle"] + names)
    selected_user_id = None
    if selected_user != "Alle":
        selected_user_id = next((emp["id"] for emp in employees if emp["name"] == selected_user), None)

    # Calculate calendar start and end
    start_date = datetime(jahr, monat, 1)
    
    # Bestimme die Anzahl der Tage im Monat
    _, days_in_month = calendar.monthrange(jahr, monat)
    end_date = datetime(jahr, monat, days_in_month)

    # Kalender-Überschrift
    st.write(f"### Kalender für {start_date.strftime('%B %Y')}")

    # Erstelle HTML für den Kalender
    cal_html = f"""
    <table class="calendar-table">
        <thead>
            <tr>
                <th>Mo</th>
                <th>Di</th>
                <th>Mi</th>
                <th>Do</th>
                <th>Fr</th>
                <th>Sa</th>
                <th>So</th>
            </tr>
        </thead>
        <tbody>
    """
    
    # Bestimme den Wochentag des ersten Tags im Monat (0 = Montag, 6 = Sonntag)
    first_day_weekday = start_date.weekday()
    
    # Erstelle Kalender-Zeilen
    day_counter = 1
    cal_html += "<tr>"
    
    # Füge leere Zellen für Tage vor dem ersten Tag des Monats hinzu
    for i in range(first_day_weekday):
        cal_html += "<td></td>"
    
    # Füge die Tage des Monats hinzu
    while day_counter <= days_in_month:
        current_date = datetime(jahr, monat, day_counter)
        weekday = current_date.weekday()
        
        # Wenn wir am Ende einer Woche sind, beginne eine neue Zeile
        if weekday == 0 and day_counter > 1:
            cal_html += "</tr><tr>"
        
        # Bestimme den Status des Tages
        css_class = ""
        tooltip = ""
        
        # Ist es ein Wochenende?
        if weekday >= 5:
            css_class = "weekend"
        
        # Ist es heute?
        if current_date.date() == heute.date():
            css_class = "today"
            tooltip = "Heute"
        
        # Ist es ein Feiertag?
        date_str = current_date.strftime("%Y-%m-%d")
        if date_str in feiertage and feiertag_filter:
            css_class = "holiday"
            tooltip = f"Feiertag: {feiertage[date_str]}"
        
        # Ist es ein Urlaubstag?
        is_vacation, vacation_user_id = ist_urlaub(current_date, vacation_requests)
        if is_vacation and urlaub_filter and (selected_user == "Alle" or user_map.get(vacation_user_id) == selected_user):
            css_class = "vacation"
            tooltip = f"Urlaub: {user_map.get(vacation_user_id, 'Unbekannt')}"
        
        # Ist es ein Krankheitstag?
        is_sick, sick_user_id = ist_krank(current_date, sick_leaves)
        if is_sick and krank_filter and (selected_user == "Alle" or user_map.get(sick_user_id) == selected_user):
            css_class = "sick"
            tooltip = f"Krank: {user_map.get(sick_user_id, 'Unbekannt')}"
        
        # Ist es ein Überstundentag?
        is_overtime = False
        if selected_user_id:
            is_overtime = overtime_map.get((selected_user_id, current_date.date()), False)
        else:
            for user_id in user_map.keys():
                if overtime_map.get((user_id, current_date.date()), False):
                    is_overtime = True
                    break
        
        if is_overtime:
            css_class = "overtime"
            tooltip = "Überstunden"
        
        # Füge den Tag zum Kalender hinzu
        if css_class:
            cal_html += f'<td class="{css_class}" title="{tooltip}">{day_counter}</td>'
        else:
            cal_html += f'<td>{day_counter}</td>'
        
        day_counter += 1
    
    # Fülle die letzte Zeile mit leeren Zellen auf
    remaining_cells = 7 - ((day_counter - 1 + first_day_weekday) % 7)
    if remaining_cells < 7:
        for i in range(remaining_cells):
            cal_html += "<td></td>"
    
    cal_html += "</tr></tbody></table>"
    
    # Zeige den Kalender an
    st.markdown(cal_html, unsafe_allow_html=True)
    
    # Legende anzeigen
    st.subheader("Legende")
    
    legend_html = """
    <div class="legend-container">
        <div class="legend-item">
            <div class="legend-color" style="background-color: #FFF1F1; border-color: #FF5733;"></div>
            <span>Feiertag</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: #E6FFEC; border-color: #33FF57;"></div>
            <span>Urlaub</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: #FFEBE5; border-color: #FF5733;"></div>
            <span>Krankmeldung</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: #FFF5CC; border-color: #FFC300;"></div>
            <span>Überstunden</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: #F0F0F0; border-color: #8C8C8C;"></div>
            <span>Wochenende</span>
        </div>
        <div class="legend-item">
            <div class="legend-color" style="background-color: #2C3E50; border-color: #2C3E50;"></div>
            <span>Heute</span>
        </div>
    </div>
    """
    
    st.markdown(legend_html, unsafe_allow_html=True)
    
    # Zeige Feiertage für den ausgewählten Monat an
    st.subheader("Feiertage in Hamburg")
    feiertage_im_monat = []
    for date_str, name in feiertage.items():
        date = datetime.strptime(date_str, "%Y-%m-%d")
        if date.month == monat and date.year == jahr:
            feiertage_im_monat.append(f"- {date.day}. {date.strftime('%B')}: {name}")
    
    if feiertage_im_monat:
        for feiertag in feiertage_im_monat:
            st.markdown(feiertag)
    else:
        st.info("Keine Feiertage in diesem Monat.")
    
    # Export-Option
    if st.checkbox("Daten anzeigen"):
        combined_df = pd.DataFrame(vacation_requests + sick_leaves)
        st.dataframe(combined_df)
        csv = combined_df.to_csv(index=False).encode("utf-8")
        st.download_button("CSV exportieren", data=csv, file_name="abwesenheiten.csv", mime="text/csv")
