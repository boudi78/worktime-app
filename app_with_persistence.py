import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import calendar
import random
import os
import io
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas
from reportlab.lib import colors
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph
from reportlab.lib.styles import getSampleStyleSheet
from data_persistence import initialize_data, save_all_data, save_employees, save_checkins, save_sick_leaves, save_vacation_requests
from admin_employee_management import delete_employee_with_confirmation, show_employees_page_enhanced

# Seitenkonfiguration
st.set_page_config(page_title="WorkTime App", page_icon=":watch:", layout="wide")

# Hamburger Ferienzeiten 2025 (Beispieldaten)
HAMBURG_FERIEN = [
    {"name": "Frühjahrsferien", "start": "2025-03-10", "end": "2025-03-21"},
    {"name": "Pfingstferien", "start": "2025-05-19", "end": "2025-05-23"},
    {"name": "Sommerferien", "start": "2025-07-14", "end": "2025-08-22"},
    {"name": "Herbstferien", "start": "2025-10-13", "end": "2025-10-24"},
    {"name": "Weihnachtsferien", "start": "2025-12-22", "end": "2026-01-05"}
]

# Beispieldaten generieren
def generate_sample_data():
    if "data_generated" not in st.session_state:
        # Mitarbeiter
        st.session_state["employees"] = [
            {"id": 1, "name": "Max Mustermann", "email": "max@example.com", "role": "Entwickler", "status": "Anwesend", "password": "password123"},
            {"id": 2, "name": "Anna Schmidt", "email": "anna@example.com", "role": "Designer", "status": "Krank", "password": "password123"},
            {"id": 3, "name": "Thomas Müller", "email": "thomas@example.com", "role": "Manager", "status": "Urlaub", "password": "password123"},
            {"id": 4, "name": "Lisa Weber", "email": "lisa@example.com", "role": "Entwickler", "status": "Anwesend", "password": "password123"},
            {"id": 5, "name": "Michael Becker", "email": "michael@example.com", "role": "Marketing", "status": "Anwesend", "password": "password123"}
        ]
        
        # Admin-Benutzer hinzufügen
        st.session_state["employees"].append({
            "id": 6, 
            "name": "Admin Benutzer", 
            "email": "admin@example.com", 
            "role": "Administrator", 
            "status": "Anwesend", 
            "password": "admin123"
        })
        
        # Benutzer hinzufügen
        st.session_state["employees"].append({
            "id": 7, 
            "name": "Mitarbeiter", 
            "email": "user@example.com", 
            "role": "Mitarbeiter", 
            "status": "Anwesend", 
            "password": "user123"
        })
        
        # Check-in/Check-out Daten
        today = datetime.now().date()
        st.session_state["checkins"] = []
        
        for emp in st.session_state["employees"]:
            # Letzten 30 Tage
            for i in range(30):
                day = today - timedelta(days=i)
                # Wochenenden überspringen
                if day.weekday() >= 5:
                    continue
                
                # Wenn krank oder im Urlaub, keine Einträge
                if (emp["status"] == "Krank" and i < 3) or (emp["status"] == "Urlaub" and i < 7):
                    continue
                
                # Zufällige Arbeitszeiten
                start_hour = 8 + random.randint(0, 1)
                start_min = random.randint(0, 59)
                duration_hours = 8 + random.randint(-1, 2)
                
                check_in = datetime.combine(day, datetime.min.time().replace(hour=start_hour, minute=start_min))
                check_out = check_in + timedelta(hours=duration_hours)
                
                # Mittagspause berücksichtigen
                if duration_hours > 6:
                    check_out += timedelta(hours=1)
                
                st.session_state["checkins"].append({
                    "employee_id": emp["id"],
                    "employee_name": emp["name"],
                    "date": day,
                    "check_in": check_in,
                    "check_out": check_out,
                    "duration": duration_hours
                })
        
        # Krankmeldungen
        st.session_state["sick_leaves"] = [
            {"employee_id": 2, "employee_name": "Anna Schmidt", "start_date": today - timedelta(days=2), "end_date": today + timedelta(days=3), "reason": "Grippe"},
            {"employee_id": 5, "employee_name": "Michael Becker", "start_date": today - timedelta(days=10), "end_date": today - timedelta(days=7), "reason": "Erkältung"}
        ]
        
        # Urlaubsanträge
        st.session_state["vacation_requests"] = [
            {"employee_id": 3, "employee_name": "Thomas Müller", "start_date": today - timedelta(days=2), "end_date": today + timedelta(days=5), "status": "Genehmigt"},
            {"employee_id": 1, "employee_name": "Max Mustermann", "start_date": today + timedelta(days=10), "end_date": today + timedelta(days=20), "status": "Ausstehend"}
        ]
        
        # Nächste ID für neue Mitarbeiter
        st.session_state["next_id"] = 8
        
        st.session_state["data_generated"] = True

def init_session_state():
    if "logged_in" not in st.session_state:
        st.session_state["logged_in"] = False
    if "check_in_status" not in st.session_state:
        st.session_state["check_in_status"] = False
    if "check_in_time" not in st.session_state:
        st.session_state["check_in_time"] = None
    if "current_page" not in st.session_state:
        st.session_state["current_page"] = "login"
    if "reset_email" not in st.session_state:
        st.session_state["reset_email"] = ""

# Hilfsfunktionen
def format_time(dt):
    if dt is None:
        return ""
    if isinstance(dt, datetime):
        return dt.strftime("%H:%M")
    return dt

def format_date(dt):
    if dt is None:
        return ""
    if isinstance(dt, datetime):
        return dt.strftime("%d.%m.%Y")
    return dt

def format_datetime(dt):
    if dt is None:
        return ""
    if isinstance(dt, datetime):
        return dt.strftime("%d.%m.%Y %H:%M")
    return dt

def calculate_work_hours(check_in, check_out):
    if check_in is None or check_out is None:
        return 0
    
    duration = (check_out - check_in).total_seconds() / 3600
    
    # Mittagspause abziehen, wenn Arbeitszeit > 6 Stunden
    if duration > 6:
        duration -= 1
    
    return round(duration, 2)

def export_as_csv(data, filename):
    df = pd.DataFrame(data)
    csv = df.to_csv(index=False).encode('utf-8')
    return csv, filename

def export_as_pdf(data, title, filename):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Titel
    styles = getSampleStyleSheet()
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Paragraph(f"Erstellt am {datetime.now().strftime('%d.%m.%Y')}", styles['Normal']))
    elements.append(Paragraph(" ", styles['Normal']))  # Leerzeile
    
    # Tabelle
    if isinstance(data, pd.DataFrame):
        data_list = [data.columns.tolist()] + data.values.tolist()
    else:
        # Annahme: data ist eine Liste von Dictionaries
        if data:
            headers = list(data[0].keys())
            data_list = [headers] + [[row.get(col, "") for col in headers] for row in data]
        else:
            data_list = [["Keine Daten verfügbar"]]
    
    table = Table(data_list)
    
    # Tabellenformatierung
    style = TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.grey),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.whitesmoke),
        ('ALIGN', (0, 0), (-1, -1), 'CENTER'),
        ('FONTNAME', (0, 0), (-1, 0), 'Helvetica-Bold'),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 12),
        ('BACKGROUND', (0, 1), (-1, -1), colors.beige),
        ('GRID', (0, 0), (-1, -1), 1, colors.black)
    ])
    
    table.setStyle(style)
    elements.append(table)
    
    doc.build(elements)
    pdf_bytes = buffer.getvalue()
    buffer.close()
    
    return pdf_bytes, filename

# Seiten
def show_login_page():
    st.title("WorkTime App")
    
    with st.container():
        st.subheader("Anmeldung")
        
        # Anmeldeformular
        with st.form("login_form"):
            username = st.text_input("Benutzername oder E-Mail", key="login_username")
            password = st.text_input("Passwort", type="password", key="login_password")
            
            cols = st.columns([1, 1, 1])
            
            with cols[1]:
                if st.form_submit_button("Anmelden", use_container_width=True):
                    if not username or not password:
                        st.error("Bitte geben Sie Benutzername und Passwort ein.")
                    else:
                        # Benutzer überprüfen
                        for emp in st.session_state["employees"]:
                            if (emp["email"].lower() == username.lower() or emp["name"].lower() == username.lower()) and emp["password"] == password:
                                # Anmeldung erfolgreich
                                st.session_state["logged_in"] = True
                                st.session_state["user_id"] = emp["id"]
                                st.session_state["username"] = emp["name"]
                                st.session_state["user_email"] = emp["email"]
                                st.session_state["user_role"] = emp["role"]
                                st.session_state["is_admin"] = "admin" in emp["role"].lower()
                                st.session_state["current_page"] = "dashboard"
                                st.rerun()
                                break
                        else:
                            st.error("Ungültige Anmeldeinformationen.")
        
        # Passwort vergessen
        if st.button("Passwort vergessen?"):
            st.session_state["current_page"] = "forgot_password"
            st.rerun()
        
        # Registrieren
        if st.button("Registrieren", key="register_button"):
            st.session_state["current_page"] = "register"
            st.rerun()
        
        # Demo-Anmeldedaten
        with st.expander("Demo-Anmeldedaten"):
            st.write("Admin: admin@example.com / admin123")
            st.write("Benutzer: user@example.com / user123")

def show_register_page():
    st.title("WorkTime App")
    
    with st.container():
        st.subheader("Registrierung")
        
        # Registrierungsformular
        with st.form("register_form"):
            name = st.text_input("Vollständiger Name", key="register_name")
            email = st.text_input("E-Mail", key="register_email")
            role = st.selectbox("Rolle", ["Mitarbeiter", "Manager", "Administrator"], key="register_role")
            password = st.text_input("Passwort", type="password", key="register_password")
            confirm_password = st.text_input("Passwort bestätigen", type="password", key="register_confirm_password")
            
            if st.form_submit_button("Registrieren", key="register_submit_button"):
                if not name or not email or not password or not confirm_password:
                    st.error("Bitte füllen Sie alle Felder aus.")
                elif password != confirm_password:
                    st.error("Passwörter stimmen nicht überein.")
                elif any(emp["email"].lower() == email.lower() for emp in st.session_state["employees"]):
                    st.error("Diese E-Mail-Adresse ist bereits registriert.")
                else:
                    # Neuen Benutzer erstellen
                    new_id = st.session_state["next_id"]
                    st.session_state["next_id"] += 1
                    
                    new_user = {
                        "id": new_id,
                        "name": name,
                        "email": email,
                        "role": role,
                        "status": "Anwesend",
                        "password": password
                    }
                    
                    # Benutzer hinzufügen
                    st.session_state["employees"].append(new_user)
                    
                    # Daten speichern
                    save_employees()
                    
                    st.success("Registrierung erfolgreich! Sie können sich jetzt anmelden.")
                    st.session_state["current_page"] = "login"
                    st.rerun()
        
        if st.button("Zurück zur Anmeldung", key="register_back_button"):
            st.session_state["current_page"] = "login"
            st.rerun()

def show_forgot_password_page():
    st.title("WorkTime App")
    
    with st.container():
        st.subheader("Passwort zurücksetzen")
        
        # Formular für Passwort zurücksetzen
        with st.form("reset_password_form"):
            email = st.text_input("E-Mail-Adresse", key="reset_email_input")
            
            if st.form_submit_button("Passwort zurücksetzen"):
                if not email:
                    st.error("Bitte geben Sie Ihre E-Mail-Adresse ein.")
                else:
                    # Prüfen, ob E-Mail existiert
                    email_exists = any(emp["email"].lower() == email.lower() for emp in st.session_state["employees"])
                    
                    if email_exists:
                        # In einer echten App würde hier eine E-Mail gesendet werden
                        st.session_state["reset_email"] = email
                        st.success("Eine E-Mail mit Anweisungen zum Zurücksetzen Ihres Passworts wurde gesendet.")
                        
                        # Für Demo-Zwecke direkt zum Passwort-Reset-Formular
                        st.session_state["current_page"] = "reset_password"
                        st.rerun()
                    else:
                        st.error("Diese E-Mail-Adresse ist nicht registriert.")
        
        if st.button("Zurück zur Anmeldung", key="forgot_back_button"):
            st.session_state["current_page"] = "login"
            st.rerun()

def show_reset_password_page():
    st.title("WorkTime App")
    
    with st.container():
        st.subheader("Neues Passwort festlegen")
        
        # Formular für neues Passwort
        with st.form("new_password_form"):
            st.write(f"E-Mail: {st.session_state['reset_email']}")
            
            new_password = st.text_input("Neues Passwort", type="password", key="new_password_input")
            confirm_password = st.text_input("Passwort bestätigen", type="password", key="confirm_new_password_input")
            
            if st.form_submit_button("Passwort speichern"):
                if not new_password or not confirm_password:
                    st.error("Bitte füllen Sie alle Felder aus.")
                elif new_password != confirm_password:
                    st.error("Passwörter stimmen nicht überein.")
                else:
                    # Passwort aktualisieren
                    email = st.session_state["reset_email"]
                    
                    for emp in st.session_state["employees"]:
                        if emp["email"].lower() == email.lower():
                            emp["password"] = new_password
                            
                            # Daten speichern
                            save_employees()
                            
                            st.success("Passwort erfolgreich aktualisiert!")
                            st.session_state["reset_email"] = ""
                            st.session_state["current_page"] = "login"
                            st.rerun()
                            break
        
        if st.button("Zurück zur Anmeldung", key="reset_back_button"):
            st.session_state["reset_email"] = ""
            st.session_state["current_page"] = "login"
            st.rerun()

def show_dashboard():
    st.title(f"Willkommen, {st.session_state['username']}!")
    
    # Aktuelle Statistiken
    st.subheader("Aktuelle Übersicht")
    
    # Mitarbeiterstatistik
    present_count = sum(1 for emp in st.session_state["employees"] if emp["status"] == "Anwesend")
    sick_count = sum(1 for emp in st.session_state["employees"] if emp["status"] == "Krank")
    vacation_count = sum(1 for emp in st.session_state["employees"] if emp["status"] == "Urlaub")
    
    col1, col2, col3 = st.columns(3)
    with col1:
        st.metric("Mitarbeiter anwesend", f"{present_count}/{len(st.session_state['employees'])}")
    with col2:
        st.metric("Mitarbeiter krank", sick_count)
    with col3:
        st.metric("Mitarbeiter im Urlaub", vacation_count)
    
    # Diagramm: Mitarbeiterstatus
    st.subheader("Mitarbeiterstatus")
    
    status_df = pd.DataFrame(st.session_state["employees"])
    status_counts = status_df["status"].value_counts().reset_index()
    status_counts.columns = ["Status", "Anzahl"]
    
    fig = px.pie(status_counts, values="Anzahl", names="Status", 
                 title="Mitarbeiterstatus", color_discrete_sequence=px.colors.qualitative.Pastel)
    st.plotly_chart(fig, use_container_width=True)
    
    # Aktuelle Check-ins
    st.subheader("Aktuelle Check-ins")
    
    today = datetime.now().date()
    today_checkins = [c for c in st.session_state["checkins"] if c["date"] == today]
    
    if today_checkins:
        checkins_df = pd.DataFrame(today_checkins)
        checkins_df["check_in"] = checkins_df["check_in"].apply(format_time)
        checkins_df["check_out"] = checkins_df["check_out"].apply(format_time)
        
        st.dataframe(checkins_df[["employee_name", "check_in", "check_out"]], use_container_width=True)
    else:
        st.info("Heute wurden noch keine Check-ins erfasst.")

def show_checkin_page():
    st.title("Check-in/Check-out")
    
    today = datetime.now().date()
    current_time = datetime.now()
    
    # Mitarbeiter auswählen (in einer echten App wäre dies der angemeldete Benutzer)
    if st.session_state.get("is_admin", False):
        employee = st.selectbox("Mitarbeiter auswählen", 
                               [emp["name"] for emp in st.session_state["employees"] if emp["status"] == "Anwesend"],
                               key="checkin_employee_select")
        employee_id = next(emp["id"] for emp in st.session_state["employees"] if emp["name"] == employee)
    else:
        employee = st.session_state.get("username")
        employee_id = st.session_state.get("user_id")
    
    # Aktuellen Check-in-Status prüfen
    current_checkin = next((c for c in st.session_state["checkins"] 
                         if c["employee_id"] == employee_id and c["date"] == today), None)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Aktuelle Arbeitszeit")
        
        if current_checkin:
            st.write(f"Check-in: {format_time(current_checkin['check_in'])}")
            
            if current_checkin.get("check_out"):
                st.write(f"Check-out: {format_time(current_checkin['check_out'])}")
                st.write(f"Arbeitszeit: {current_checkin['duration']} Stunden")
            else:
                # Laufende Arbeitszeit berechnen
                elapsed = (current_time - current_checkin["check_in"]).total_seconds() / 3600
                st.write(f"Laufende Arbeitszeit: {elapsed:.2f} Stunden")
        else:
            st.write("Heute noch nicht eingecheckt.")
    
    with col2:
        st.subheader("Aktion")
        
        if current_checkin and not current_checkin.get("check_out"):
            # Check-out
            if st.button("Check-out", key="checkout_button"):
                # Check-out Zeit setzen
                for c in st.session_state["checkins"]:
                    if c["employee_id"] == employee_id and c["date"] == today:
                        c["check_out"] = current_time
                        c["duration"] = calculate_work_hours(c["check_in"], c["check_out"])
                        
                        # Daten speichern
                        save_checkins()
                        
                        st.success(f"Check-out um {format_time(current_time)} erfolgreich!")
                        st.rerun()
        else:
            # Check-in
            if st.button("Check-in", key="checkin_button"):
                new_checkin = {
                    "employee_id": employee_id,
                    "employee_name": employee,
                    "date": today,
                    "check_in": current_time,
                    "check_out": None,
                    "duration": 0
                }
                
                st.session_state["checkins"].append(new_checkin)
                
                # Daten speichern
                save_checkins()
                
                st.success(f"Check-in um {format_time(current_time)} erfolgreich!")
                st.rerun()
    
    # Verlauf anzeigen
    st.subheader("Check-in Verlauf")
    
    # Checkins des Mitarbeiters abrufen
    employee_checkins = [c for c in st.session_state["checkins"] 
                        if c["employee_id"] == employee_id]
    employee_checkins.sort(key=lambda x: x["date"], reverse=True)
    
    if employee_checkins:
        checkins_df = pd.DataFrame(employee_checkins[:10])  # Letzte 10 Einträge
        
        # Formatierung
        checkins_df["date"] = checkins_df["date"].apply(format_date)
        checkins_df["check_in"] = checkins_df["check_in"].apply(format_time)
        checkins_df["check_out"] = checkins_df["check_out"].apply(format_time)
        
        st.dataframe(checkins_df[["date", "check_in", "check_out", "duration"]], use_container_width=True)
        
        # Export-Optionen
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Als CSV exportieren", key="export_csv_button"):
                csv_data, filename = export_as_csv(employee_checkins, "checkins.csv")
                
                st.download_button(
                    label="CSV herunterladen",
                    data=csv_data,
                    file_name=filename,
                    mime="text/csv",
                    key="checkin_csv_download"
                )
        
        with col2:
            if st.button("Als PDF exportieren", key="export_pdf_button"):
                # PDF-Daten vorbereiten
                pdf_data = pd.DataFrame(employee_checkins)
                pdf_data["date"] = pdf_data["date"].apply(format_date)
                pdf_data["check_in"] = pdf_data["check_in"].apply(format_time)
                pdf_data["check_out"] = pdf_data["check_out"].apply(format_time)
                
                for checkin in employee_checkins:
                    if checkin.get("check_out") is None:
                        checkin["duration"] = calculate_work_hours(checkin["check_in"], current_time)
                
                pdf_data = pdf_data[["date", "check_in", "check_out", "duration"]]
                pdf_data.columns = ["Datum", "Check-in", "Check-out", "Stunden"]
                
                pdf_bytes, filename = export_as_pdf(pdf_data, f"Arbeitszeiten - {employee}", "arbeitszeiten.pdf")
                
                st.download_button(
                    label="PDF herunterladen",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    key="checkin_pdf_download"
                )
    else:
        st.info("Keine Check-ins gefunden.")

def delete_employee(employee_id):
    # Mitarbeiter aus allen Listen entfernen
    st.session_state["employees"] = [emp for emp in st.session_state["employees"] if emp["id"] != employee_id]
    
    # Zugehörige Daten entfernen
    st.session_state["checkins"] = [c for c in st.session_state["checkins"] if c["employee_id"] != employee_id]
    st.session_state["vacation_requests"] = [v for v in st.session_state["vacation_requests"] if v["employee_id"] != employee_id]
    st.session_state["sick_leaves"] = [s for s in st.session_state["sick_leaves"] if s["employee_id"] != employee_id]
    
    # Daten speichern
    save_all_data()
    
    return True

def show_work_hours_page():
    st.title("Arbeitszeiten")
    
    # Tabs für verschiedene Ansichten
    tab1, tab2 = st.tabs(["Übersicht", "Detailansicht"])
    
    with tab1:
        st.subheader("Arbeitszeiten-Übersicht")
        
        # Zeitraum auswählen
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Von", value=datetime.now().date() - timedelta(days=30), key="work_hours_start")
        with col2:
            end_date = st.date_input("Bis", value=datetime.now().date(), key="work_hours_end")
        
        # Mitarbeiter auswählen
        if st.session_state.get("is_admin", False):
            employees = st.multiselect(
                "Mitarbeiter auswählen",
                [emp["name"] for emp in st.session_state["employees"]],
                default=[emp["name"] for emp in st.session_state["employees"]],
                key="work_hours_employees"
            )
            
            # Mitarbeiter-IDs ermitteln
            employee_ids = [emp["id"] for emp in st.session_state["employees"] if emp["name"] in employees]
        else:
            # Nur eigene Daten anzeigen
            employees = [st.session_state.get("username")]
            employee_ids = [st.session_state.get("user_id")]
        
        # Daten filtern
        filtered_checkins = [
            c for c in st.session_state["checkins"]
            if c["employee_id"] in employee_ids and start_date <= c["date"] <= end_date
        ]
        
        if filtered_checkins:
            # Daten für Diagramm vorbereiten
            checkins_df = pd.DataFrame(filtered_checkins)
            
            # Gruppieren nach Mitarbeiter und Datum
            grouped_df = checkins_df.groupby(["employee_name", "date"])["duration"].sum().reset_index()
            
            # Diagramm: Arbeitszeiten pro Tag
            fig = px.bar(
                grouped_df,
                x="date",
                y="duration",
                color="employee_name",
                title="Arbeitszeiten pro Tag",
                labels={"date": "Datum", "duration": "Stunden", "employee_name": "Mitarbeiter"}
            )
            st.plotly_chart(fig, use_container_width=True)
            
            # Tabelle mit Gesamtstunden pro Mitarbeiter
            st.subheader("Gesamtstunden pro Mitarbeiter")
            
            total_hours = checkins_df.groupby("employee_name")["duration"].sum().reset_index()
            total_hours.columns = ["Mitarbeiter", "Gesamtstunden"]
            
            st.dataframe(total_hours, use_container_width=True)
            
            # Export-Optionen
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Als CSV exportieren", key="work_hours_csv_button"):
                    csv_data, filename = export_as_csv(filtered_checkins, "work_hours.csv")
                    
                    st.download_button(
                        label="CSV herunterladen",
                        data=csv_data,
                        file_name=filename,
                        mime="text/csv",
                        key="work_hours_csv_download"
                    )
            
            with col2:
                if st.button("Als PDF exportieren", key="work_hours_pdf_button"):
                    # PDF-Daten vorbereiten
                    pdf_data = pd.DataFrame(filtered_checkins)
                    pdf_data["date"] = pdf_data["date"].apply(format_date)
                    pdf_data["check_in"] = pdf_data["check_in"].apply(format_time)
                    pdf_data["check_out"] = pdf_data["check_out"].apply(format_time)
                    
                    pdf_data = pdf_data[["employee_name", "date", "check_in", "check_out", "duration"]]
                    pdf_data.columns = ["Mitarbeiter", "Datum", "Check-in", "Check-out", "Stunden"]
                    
                    pdf_bytes, filename = export_as_pdf(pdf_data, "Arbeitszeiten Übersicht", "arbeitszeiten_uebersicht.pdf")
                    
                    st.download_button(
                        label="PDF herunterladen",
                        data=pdf_bytes,
                        file_name=filename,
                        mime="application/pdf",
                        key="work_hours_pdf_download"
                    )
        else:
            st.info("Keine Daten für den ausgewählten Zeitraum gefunden.")
    
    with tab2:
        st.subheader("Detailansicht")
        
        # Mitarbeiter auswählen
        if st.session_state.get("is_admin", False):
            employee = st.selectbox(
                "Mitarbeiter auswählen",
                [emp["name"] for emp in st.session_state["employees"]],
                key="work_hours_detail_employee"
            )
            
            # Mitarbeiter-ID ermitteln
            employee_id = next(emp["id"] for emp in st.session_state["employees"] if emp["name"] == employee)
        else:
            # Nur eigene Daten anzeigen
            employee = st.session_state.get("username")
            employee_id = st.session_state.get("user_id")
        
        # Zeitraum auswählen
        col1, col2 = st.columns(2)
        with col1:
            detail_start_date = st.date_input("Von", value=datetime.now().date() - timedelta(days=30), key="work_hours_detail_start")
        with col2:
            detail_end_date = st.date_input("Bis", value=datetime.now().date(), key="work_hours_detail_end")
        
        # Daten filtern
        detail_checkins = [
            c for c in st.session_state["checkins"]
            if c["employee_id"] == employee_id and detail_start_date <= c["date"] <= detail_end_date
        ]
        
        if detail_checkins:
            # Daten für Tabelle vorbereiten
            detail_df = pd.DataFrame(detail_checkins)
            detail_df["date"] = detail_df["date"].apply(format_date)
            detail_df["check_in"] = detail_df["check_in"].apply(format_time)
            detail_df["check_out"] = detail_df["check_out"].apply(format_time)
            
            # Tabelle anzeigen
            st.dataframe(detail_df[["date", "check_in", "check_out", "duration"]], use_container_width=True)
            
            # Gesamtstunden
            total_hours = detail_df["duration"].sum()
            st.metric("Gesamtstunden", f"{total_hours:.2f}")
            
            # Export-Optionen
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Als CSV exportieren", key="my_hours_csv_button"):
                    csv_data, filename = export_as_csv(detail_checkins, f"arbeitszeiten_{employee.replace(' ', '_')}.csv")
                    
                    st.download_button(
                        label="CSV herunterladen",
                        data=csv_data,
                        file_name=filename,
                        mime="text/csv",
                        key="my_hours_csv_download"
                    )
            
            with col2:
                if st.button("Als PDF exportieren", key="my_hours_pdf_button"):
                    # PDF-Daten vorbereiten
                    pdf_data = detail_df[["date", "check_in", "check_out", "duration"]]
                    pdf_data.columns = ["Datum", "Check-in", "Check-out", "Stunden"]
                    
                    pdf_bytes, filename = export_as_pdf(pdf_data, f"Arbeitszeiten - {employee}", f"arbeitszeiten_{employee.replace(' ', '_')}.pdf")
                    
                    st.download_button(
                        label="PDF herunterladen",
                        data=pdf_bytes,
                        file_name=filename,
                        mime="application/pdf",
                        key="my_hours_pdf_download"
                    )
        else:
            st.info("Keine Daten für den ausgewählten Zeitraum gefunden.")

def show_sick_leave_page():
    st.title("Krankmeldungen")
    
    # Tabs für verschiedene Funktionen
    tab1, tab2 = st.tabs(["Übersicht", "Neue Krankmeldung"])
    
    with tab1:
        st.subheader("Krankmeldungen-Übersicht")
        
        # Krankmeldungen filtern
        if st.session_state.get("is_admin", False):
            # Alle Krankmeldungen für Admins
            sick_leaves = st.session_state["sick_leaves"]
        else:
            # Nur eigene Krankmeldungen für normale Benutzer
            sick_leaves = [s for s in st.session_state["sick_leaves"] 
                          if s["employee_id"] == st.session_state.get("user_id")]
        
        if sick_leaves:
            # Daten für Tabelle vorbereiten
            sick_df = pd.DataFrame(sick_leaves)
            sick_df["start_date"] = sick_df["start_date"].apply(format_date)
            sick_df["end_date"] = sick_df["end_date"].apply(format_date)
            
            # Tabelle anzeigen
            st.dataframe(sick_df[["employee_name", "start_date", "end_date", "reason"]], use_container_width=True)
        else:
            st.info("Keine Krankmeldungen gefunden.")
    
    with tab2:
        st.subheader("Neue Krankmeldung")
        
        # Mitarbeiter auswählen
        if st.session_state.get("is_admin", False):
            employee = st.selectbox(
                "Mitarbeiter auswählen",
                [emp["name"] for emp in st.session_state["employees"]],
                key="sick_leave_employee"
            )
            
            # Mitarbeiter-ID ermitteln
            employee_id = next(emp["id"] for emp in st.session_state["employees"] if emp["name"] == employee)
            employee_name = employee
        else:
            # Eigene Daten verwenden
            employee_id = st.session_state.get("user_id")
            employee_name = st.session_state.get("username")
        
        # Formular für neue Krankmeldung
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input("Von", value=datetime.now().date(), key="sick_leave_start")
        
        with col2:
            end_date = st.date_input("Bis", value=datetime.now().date() + timedelta(days=3), key="sick_leave_end")
        
        reason = st.text_area("Grund", key="sick_leave_reason")
        
        if st.button("Krankmeldung speichern", key="save_sick_button"):
            if start_date > end_date:
                st.error("Das Enddatum muss nach dem Startdatum liegen.")
            else:
                # Neue Krankmeldung erstellen
                new_sick_leave = {
                    "employee_id": employee_id,
                    "employee_name": employee_name,
                    "start_date": start_date,
                    "end_date": end_date,
                    "reason": reason
                }
                
                # Krankmeldung hinzufügen
                st.session_state["sick_leaves"].append(new_sick_leave)
                
                # Mitarbeiterstatus aktualisieren
                for emp in st.session_state["employees"]:
                    if emp["id"] == employee_id:
                        emp["status"] = "Krank"
                        break
                
                # Daten speichern
                save_sick_leaves()
                save_employees()
                
                st.success("Krankmeldung erfolgreich gespeichert.")
                st.rerun()

def show_vacation_page():
    st.title("Urlaubsanträge")
    
    # Tabs für verschiedene Funktionen
    tab1, tab2, tab3 = st.tabs(["Übersicht", "Neuer Antrag", "Ferienkalender"])
    
    with tab1:
        st.subheader("Urlaubsanträge-Übersicht")
        
        # Urlaubsanträge filtern
        if st.session_state.get("is_admin", False):
            # Alle Anträge für Admins
            vacation_requests = st.session_state["vacation_requests"]
            
            # Status-Filter
            status_filter = st.selectbox(
                "Status filtern",
                ["Alle", "Ausstehend", "Genehmigt", "Abgelehnt"],
                key="vacation_status_filter"
            )
            
            if status_filter != "Alle":
                vacation_requests = [v for v in vacation_requests if v["status"] == status_filter]
        else:
            # Nur eigene Anträge für normale Benutzer
            vacation_requests = [v for v in st.session_state["vacation_requests"] 
                               if v["employee_id"] == st.session_state.get("user_id")]
        
        if vacation_requests:
            # Daten für Tabelle vorbereiten
            vacation_df = pd.DataFrame(vacation_requests)
            vacation_df["start_date"] = vacation_df["start_date"].apply(format_date)
            vacation_df["end_date"] = vacation_df["end_date"].apply(format_date)
            
            # Tabelle anzeigen
            for v in vacation_requests:
                with st.expander(f"{v['employee_name']} - {format_date(v['start_date'])} bis {format_date(v['end_date'])}"):
                    st.write(f"**Status:** {v['status']}")
                    
                    # Berechnung der Urlaubstage
                    start_date = v['start_date'] if isinstance(v['start_date'], datetime) else datetime.strptime(v['start_date'], "%Y-%m-%d").date()
                    end_date = v['end_date'] if isinstance(v['end_date'], datetime) else datetime.strptime(v['end_date'], "%Y-%m-%d").date()
                    
                    # Nur Werktage zählen
                    vacation_days = 0
                    current_date = start_date
                    while current_date <= end_date:
                        if current_date.weekday() < 5:  # 0-4 sind Montag bis Freitag
                            vacation_days += 1
                        current_date += timedelta(days=1)
                    
                    st.write(f"**Urlaubstage:** {vacation_days} Werktage")
                    
                    # Admin-Aktionen
                    if st.session_state.get("is_admin", False) and v["status"] == "Ausstehend":
                        col1, col2 = st.columns(2)
                        
                        with col1:
                            if st.button("Genehmigen", key=f"approve_vacation_{v['employee_id']}_{v['start_date']}"):
                                # Antrag genehmigen
                                for vr in st.session_state["vacation_requests"]:
                                    if vr["employee_id"] == v["employee_id"] and vr["start_date"] == v["start_date"] and vr["end_date"] == v["end_date"]:
                                        vr["status"] = "Genehmigt"
                                        
                                        # Mitarbeiterstatus aktualisieren, wenn Urlaub jetzt ist
                                        today = datetime.now().date()
                                        if start_date <= today <= end_date:
                                            for emp in st.session_state["employees"]:
                                                if emp["id"] == v["employee_id"]:
                                                    emp["status"] = "Urlaub"
                                                    break
                                        
                                        # Daten speichern
                                        save_vacation_requests()
                                        save_employees()
                                        
                                        st.success("Urlaubsantrag genehmigt.")
                                        st.rerun()
                                        break
                        
                        with col2:
                            if st.button("Ablehnen", key=f"reject_vacation_{v['employee_id']}_{v['start_date']}"):
                                # Antrag ablehnen
                                for vr in st.session_state["vacation_requests"]:
                                    if vr["employee_id"] == v["employee_id"] and vr["start_date"] == v["start_date"] and vr["end_date"] == v["end_date"]:
                                        vr["status"] = "Abgelehnt"
                                        
                                        # Daten speichern
                                        save_vacation_requests()
                                        
                                        st.success("Urlaubsantrag abgelehnt.")
                                        st.rerun()
                                        break
        else:
            st.info("Keine Urlaubsanträge gefunden.")
    
    with tab2:
        st.subheader("Neuer Urlaubsantrag")
        
        # Mitarbeiter auswählen
        if st.session_state.get("is_admin", False):
            employee = st.selectbox(
                "Mitarbeiter auswählen",
                [emp["name"] for emp in st.session_state["employees"]],
                key="vacation_employee"
            )
            
            # Mitarbeiter-ID ermitteln
            employee_id = next(emp["id"] for emp in st.session_state["employees"] if emp["name"] == employee)
            employee_name = employee
        else:
            # Eigene Daten verwenden
            employee_id = st.session_state.get("user_id")
            employee_name = st.session_state.get("username")
        
        # Formular für neuen Urlaubsantrag
        col1, col2 = st.columns(2)
        
        with col1:
            start_date = st.date_input("Von", value=datetime.now().date() + timedelta(days=14), key="vacation_start")
        
        with col2:
            end_date = st.date_input("Bis", value=datetime.now().date() + timedelta(days=21), key="vacation_end")
        
        # Berechnung der Urlaubstage
        vacation_days = 0
        current_date = start_date
        while current_date <= end_date:
            if current_date.weekday() < 5:  # 0-4 sind Montag bis Freitag
                vacation_days += 1
            current_date += timedelta(days=1)
        
        st.write(f"**Urlaubstage:** {vacation_days} Werktage")
        
        if st.button("Urlaubsantrag speichern", key="save_vacation_button"):
            if start_date > end_date:
                st.error("Das Enddatum muss nach dem Startdatum liegen.")
            else:
                # Neuen Urlaubsantrag erstellen
                new_vacation = {
                    "employee_id": employee_id,
                    "employee_name": employee_name,
                    "start_date": start_date,
                    "end_date": end_date,
                    "status": "Ausstehend" if not st.session_state.get("is_admin", False) else "Genehmigt"
                }
                
                # Urlaubsantrag hinzufügen
                st.session_state["vacation_requests"].append(new_vacation)
                
                # Wenn Admin und Urlaub jetzt ist, Status aktualisieren
                if st.session_state.get("is_admin", False):
                    today = datetime.now().date()
                    if start_date <= today <= end_date:
                        for emp in st.session_state["employees"]:
                            if emp["id"] == employee_id:
                                emp["status"] = "Urlaub"
                                break
                
                # Daten speichern
                save_vacation_requests()
                save_employees()
                
                st.success("Urlaubsantrag erfolgreich gespeichert.")
                st.rerun()
    
    with tab3:
        st.subheader("Ferienkalender")
        
        # Aktuelles Jahr
        current_year = datetime.now().year
        
        # Ferienkalender anzeigen
        st.write(f"**Schulferien Hamburg {current_year}**")
        
        # Tabelle mit Ferienzeiten
        ferien_df = pd.DataFrame(HAMBURG_FERIEN)
        ferien_df["start"] = pd.to_datetime(ferien_df["start"]).dt.strftime("%d.%m.%Y")
        ferien_df["end"] = pd.to_datetime(ferien_df["end"]).dt.strftime("%d.%m.%Y")
        ferien_df.columns = ["Ferien", "Von", "Bis"]
        
        st.table(ferien_df)
        
        # Export-Optionen
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Als CSV exportieren", key="ferien_csv_button"):
                csv_data, filename = export_as_csv(HAMBURG_FERIEN, "ferien.csv")
                
                st.download_button(
                    label="CSV herunterladen",
                    data=csv_data,
                    file_name=filename,
                    mime="text/csv",
                    key="ferien_csv_download"
                )
        
        with col2:
            if st.button("Als PDF exportieren", key="ferien_pdf_button"):
                # PDF-Daten vorbereiten
                pdf_data = ferien_df
                
                pdf_bytes, filename = export_as_pdf(pdf_data, f"Schulferien Hamburg {current_year}", "ferien.pdf")
                
                st.download_button(
                    label="PDF herunterladen",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    key="ferien_pdf_download"
                )

def show_statistics_page():
    st.title("Statistiken")
    
    # Tabs für verschiedene Statistiken
    tab1, tab2, tab3 = st.tabs(["Arbeitszeiten", "Anwesenheit", "Krankheit & Urlaub"])
    
    with tab1:
        st.subheader("Arbeitszeitstatistiken")
        
        # Zeitraum auswählen
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input("Von", value=datetime.now().date() - timedelta(days=30), key="stats_start")
        with col2:
            end_date = st.date_input("Bis", value=datetime.now().date(), key="stats_end")
        
        # Daten filtern
        if st.session_state.get("is_admin", False):
            # Alle Daten für Admins
            filtered_checkins = [
                c for c in st.session_state["checkins"]
                if start_date <= c["date"] <= end_date
            ]
        else:
            # Nur eigene Daten für normale Benutzer
            filtered_checkins = [
                c for c in st.session_state["checkins"]
                if c["employee_id"] == st.session_state.get("user_id") and start_date <= c["date"] <= end_date
            ]
        
        if filtered_checkins:
            # Daten für Diagramme vorbereiten
            checkins_df = pd.DataFrame(filtered_checkins)
            
            # Diagramm 1: Durchschnittliche Arbeitszeit pro Tag der Woche
            st.subheader("Durchschnittliche Arbeitszeit pro Wochentag")
            
            # Wochentag hinzufügen
            checkins_df["weekday"] = checkins_df["date"].apply(lambda x: x.weekday())
            checkins_df["weekday_name"] = checkins_df["weekday"].apply(lambda x: ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"][x])
            
            # Gruppieren nach Wochentag
            weekday_avg = checkins_df.groupby("weekday_name")["duration"].mean().reset_index()
            weekday_avg = weekday_avg.sort_values("weekday", key=lambda x: pd.Categorical(x, categories=["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"]))
            
            fig1 = px.bar(
                weekday_avg,
                x="weekday_name",
                y="duration",
                title="Durchschnittliche Arbeitszeit pro Wochentag",
                labels={"weekday_name": "Wochentag", "duration": "Durchschnittliche Stunden"}
            )
            st.plotly_chart(fig1, use_container_width=True)
            
            # Diagramm 2: Arbeitszeit pro Mitarbeiter
            if st.session_state.get("is_admin", False):
                st.subheader("Arbeitszeit pro Mitarbeiter")
                
                # Gruppieren nach Mitarbeiter
                employee_hours = checkins_df.groupby("employee_name")["duration"].sum().reset_index()
                
                fig2 = px.bar(
                    employee_hours,
                    x="employee_name",
                    y="duration",
                    title="Gesamtarbeitszeit pro Mitarbeiter",
                    labels={"employee_name": "Mitarbeiter", "duration": "Gesamtstunden"}
                )
                st.plotly_chart(fig2, use_container_width=True)
            
            # Diagramm 3: Arbeitszeit-Trend
            st.subheader("Arbeitszeit-Trend")
            
            # Gruppieren nach Datum
            date_hours = checkins_df.groupby("date")["duration"].sum().reset_index()
            
            fig3 = px.line(
                date_hours,
                x="date",
                y="duration",
                title="Arbeitszeit-Trend",
                labels={"date": "Datum", "duration": "Stunden"}
            )
            st.plotly_chart(fig3, use_container_width=True)
            
            # Export-Optionen
            col1, col2 = st.columns(2)
            
            with col1:
                if st.button("Als CSV exportieren", key="stats_csv_button"):
                    # CSV-Daten vorbereiten
                    export_data = checkins_df.copy()
                    export_data["date"] = export_data["date"].apply(format_date)
                    export_data["check_in"] = export_data["check_in"].apply(format_time)
                    export_data["check_out"] = export_data["check_out"].apply(format_time)
                    
                    csv_data, filename = export_as_csv(export_data, "arbeitszeit_statistik.csv")
                    
                    st.download_button(
                        label="CSV herunterladen",
                        data=csv_data,
                        file_name=filename,
                        mime="text/csv",
                        key="stats_csv_download"
                    )
            
            with col2:
                if st.button("Als PDF exportieren", key="stats_pdf_button"):
                    # PDF-Daten vorbereiten
                    export_data = checkins_df.copy()
                    export_data["date"] = export_data["date"].apply(format_date)
                    export_data["check_in"] = export_data["check_in"].apply(format_time)
                    export_data["check_out"] = export_data["check_out"].apply(format_time)
                    
                    pdf_data = export_data[["employee_name", "date", "check_in", "check_out", "duration"]]
                    pdf_data.columns = ["Mitarbeiter", "Datum", "Check-in", "Check-out", "Stunden"]
                    
                    pdf_bytes, filename = export_as_pdf(pdf_data, "Arbeitszeitstatistik", "arbeitszeit_statistik.pdf")
                    
                    st.download_button(
                        label="PDF herunterladen",
                        data=pdf_bytes,
                        file_name=filename,
                        mime="application/pdf",
                        key="stats_pdf_download"
                    )
        else:
            st.info("Keine Daten für den ausgewählten Zeitraum gefunden.")
    
    with tab2:
        st.subheader("Anwesenheitsstatistik")
        
        if st.session_state.get("is_admin", False):
            # Aktuelle Anwesenheit
            st.write("**Aktuelle Anwesenheit**")
            
            # Status zählen
            status_counts = {}
            for emp in st.session_state["employees"]:
                status = emp["status"]
                status_counts[status] = status_counts.get(status, 0) + 1
            
            # Diagramm: Anwesenheitsstatus
            status_df = pd.DataFrame({"Status": list(status_counts.keys()), "Anzahl": list(status_counts.values())})
            
            fig4 = px.pie(
                status_df,
                values="Anzahl",
                names="Status",
                title="Anwesenheitsstatus",
                color_discrete_sequence=px.colors.qualitative.Pastel
            )
            st.plotly_chart(fig4, use_container_width=True)
            
            # Tabelle mit Mitarbeiterstatus
            st.write("**Mitarbeiterstatus**")
            
            employees_df = pd.DataFrame(st.session_state["employees"])
            employees_df = employees_df[["name", "role", "status"]]
            employees_df.columns = ["Name", "Rolle", "Status"]
            
            st.dataframe(employees_df, use_container_width=True)
        else:
            st.info("Diese Statistik ist nur für Administratoren verfügbar.")
    
    with tab3:
        st.subheader("Krankheits- und Urlaubsstatistik")
        
        if st.session_state.get("is_admin", False):
            # Zeitraum auswählen
            col1, col2 = st.columns(2)
            with col1:
                sick_start_date = st.date_input("Von", value=datetime.now().date() - timedelta(days=90), key="sick_stats_start")
            with col2:
                sick_end_date = st.date_input("Bis", value=datetime.now().date(), key="sick_stats_end")
            
            # Krankmeldungen filtern
            filtered_sick_leaves = [
                s for s in st.session_state["sick_leaves"]
                if (isinstance(s["start_date"], datetime) and sick_start_date <= s["start_date"].date() <= sick_end_date) or
                   (isinstance(s["start_date"], str) and sick_start_date <= datetime.strptime(s["start_date"], "%Y-%m-%d").date() <= sick_end_date)
            ]
            
            # Urlaubsanträge filtern
            filtered_vacation_requests = [
                v for v in st.session_state["vacation_requests"]
                if v["status"] == "Genehmigt" and
                   ((isinstance(v["start_date"], datetime) and sick_start_date <= v["start_date"].date() <= sick_end_date) or
                    (isinstance(v["start_date"], str) and sick_start_date <= datetime.strptime(v["start_date"], "%Y-%m-%d").date() <= sick_end_date))
            ]
            
            if filtered_sick_leaves or filtered_vacation_requests:
                # Diagramm: Krankheitstage pro Mitarbeiter
                if filtered_sick_leaves:
                    st.subheader("Krankheitstage pro Mitarbeiter")
                    
                    # Krankheitstage berechnen
                    sick_days_by_employee = {}
                    
                    for sick in filtered_sick_leaves:
                        employee_name = sick["employee_name"]
                        
                        # Start- und Enddatum konvertieren
                        start_date = sick["start_date"] if isinstance(sick["start_date"], datetime) else datetime.strptime(sick["start_date"], "%Y-%m-%d").date()
                        end_date = sick["end_date"] if isinstance(sick["end_date"], datetime) else datetime.strptime(sick["end_date"], "%Y-%m-%d").date()
                        
                        # Nur Werktage zählen
                        days = 0
                        current_date = start_date if isinstance(start_date, datetime) else start_date
                        end = end_date if isinstance(end_date, datetime) else end_date
                        
                        while current_date <= end:
                            if current_date.weekday() < 5:  # 0-4 sind Montag bis Freitag
                                days += 1
                            current_date += timedelta(days=1)
                        
                        sick_days_by_employee[employee_name] = sick_days_by_employee.get(employee_name, 0) + days
                    
                    # Diagramm erstellen
                    sick_days_df = pd.DataFrame({"Mitarbeiter": list(sick_days_by_employee.keys()), "Krankheitstage": list(sick_days_by_employee.values())})
                    
                    fig5 = px.bar(
                        sick_days_df,
                        x="Mitarbeiter",
                        y="Krankheitstage",
                        title="Krankheitstage pro Mitarbeiter",
                        labels={"Mitarbeiter": "Mitarbeiter", "Krankheitstage": "Tage"}
                    )
                    st.plotly_chart(fig5, use_container_width=True)
                
                # Diagramm: Urlaubstage pro Mitarbeiter
                if filtered_vacation_requests:
                    st.subheader("Genehmigte Urlaubstage pro Mitarbeiter")
                    
                    # Urlaubstage berechnen
                    vacation_days_by_employee = {}
                    
                    for vacation in filtered_vacation_requests:
                        employee_name = vacation["employee_name"]
                        
                        # Start- und Enddatum konvertieren
                        start_date = vacation["start_date"] if isinstance(vacation["start_date"], datetime) else datetime.strptime(vacation["start_date"], "%Y-%m-%d").date()
                        end_date = vacation["end_date"] if isinstance(vacation["end_date"], datetime) else datetime.strptime(vacation["end_date"], "%Y-%m-%d").date()
                        
                        # Nur Werktage zählen
                        days = 0
                        current_date = start_date if isinstance(start_date, datetime) else start_date
                        end = end_date if isinstance(end_date, datetime) else end_date
                        
                        while current_date <= end:
                            if current_date.weekday() < 5:  # 0-4 sind Montag bis Freitag
                                days += 1
                            current_date += timedelta(days=1)
                        
                        vacation_days_by_employee[employee_name] = vacation_days_by_employee.get(employee_name, 0) + days
                    
                    # Diagramm erstellen
                    vacation_days_df = pd.DataFrame({"Mitarbeiter": list(vacation_days_by_employee.keys()), "Urlaubstage": list(vacation_days_by_employee.values())})
                    
                    fig6 = px.bar(
                        vacation_days_df,
                        x="Mitarbeiter",
                        y="Urlaubstage",
                        title="Genehmigte Urlaubstage pro Mitarbeiter",
                        labels={"Mitarbeiter": "Mitarbeiter", "Urlaubstage": "Tage"}
                    )
                    st.plotly_chart(fig6, use_container_width=True)
            else:
                st.info("Keine Daten für den ausgewählten Zeitraum gefunden.")
        else:
            # Für normale Benutzer nur eigene Daten anzeigen
            employee_id = st.session_state.get("user_id")
            employee_name = st.session_state.get("username")
            
            # Eigene Krankmeldungen
            sick_leaves = [s for s in st.session_state["sick_leaves"] if s["employee_id"] == employee_id]
            
            if sick_leaves:
                st.subheader("Ihre Krankmeldungen")
                
                sick_df = pd.DataFrame(sick_leaves)
                sick_df["start_date"] = sick_df["start_date"].apply(format_date)
                sick_df["end_date"] = sick_df["end_date"].apply(format_date)
                
                st.dataframe(sick_df[["start_date", "end_date", "reason"]], use_container_width=True)
            else:
                st.info("Keine Krankmeldungen gefunden.")
            
            # Eigene Urlaubsanträge
            vacation_requests = [v for v in st.session_state["vacation_requests"] if v["employee_id"] == employee_id]
            
            if vacation_requests:
                st.subheader("Ihre Urlaubsanträge")
                
                vacation_df = pd.DataFrame(vacation_requests)
                vacation_df["start_date"] = vacation_df["start_date"].apply(format_date)
                vacation_df["end_date"] = vacation_df["end_date"].apply(format_date)
                
                st.dataframe(vacation_df[["start_date", "end_date", "status"]], use_container_width=True)
            else:
                st.info("Keine Urlaubsanträge gefunden.")

def show_settings_page():
    st.title("Einstellungen")
    
    # Tabs für verschiedene Einstellungen
    tab1, tab2, tab3 = st.tabs(["Profil", "Arbeitszeiteinstellungen", "Systemeinstellungen"])
    
    with tab1:
        st.subheader("Profileinstellungen")
        
        # Aktuellen Benutzer abrufen
        user_id = st.session_state.get("user_id")
        user = next((emp for emp in st.session_state["employees"] if emp["id"] == user_id), None)
        
        if user:
            col1, col2 = st.columns(2)
            
            with col1:
                name = st.text_input("Name", value=user["name"], key="profile_name")
                email = st.text_input("E-Mail", value=user["email"], key="profile_email")
            
            with col2:
                role = st.text_input("Rolle", value=user["role"], disabled=not st.session_state.get("is_admin", False), key="profile_role")
                status = st.selectbox("Status", ["Anwesend", "Abwesend", "Krank", "Urlaub"], index=["Anwesend", "Abwesend", "Krank", "Urlaub"].index(user["status"]), key="profile_status")
            
            # Passwort ändern
            st.subheader("Passwort ändern")
            
            col1, col2 = st.columns(2)
            
            with col1:
                current_password = st.text_input("Aktuelles Passwort", type="password", key="current_password")
            
            with col2:
                new_password = st.text_input("Neues Passwort", type="password", key="new_password")
                confirm_password = st.text_input("Passwort bestätigen", type="password", key="confirm_password")
            
            if st.button("Einstellungen speichern", key="save_settings_button"):
                # Profiländerungen
                user["name"] = name
                
                # E-Mail-Änderung nur, wenn nicht bereits verwendet
                if email != user["email"] and not any(emp["email"].lower() == email.lower() for emp in st.session_state["employees"] if emp["id"] != user_id):
                    user["email"] = email
                elif email != user["email"]:
                    st.error("Diese E-Mail-Adresse wird bereits verwendet.")
                
                # Rolle und Status
                if st.session_state.get("is_admin", False):
                    user["role"] = role
                user["status"] = status
                
                # Passwortänderung
                if current_password and new_password and confirm_password:
                    if current_password == user["password"]:
                        if new_password == confirm_password:
                            user["password"] = new_password
                            st.success("Passwort erfolgreich geändert.")
                        else:
                            st.error("Die neuen Passwörter stimmen nicht überein.")
                    else:
                        st.error("Das aktuelle Passwort ist falsch.")
                
                # Session-State aktualisieren
                st.session_state["username"] = name
                st.session_state["user_email"] = email
                st.session_state["user_role"] = role
                st.session_state["is_admin"] = "admin" in role.lower()
                
                # Daten speichern
                save_employees()
                
                st.success("Einstellungen erfolgreich gespeichert.")
                st.rerun()
        else:
            st.error("Benutzer nicht gefunden.")
    
    with tab2:
        if st.session_state.get("is_admin", False):
            st.subheader("Arbeitszeiteinstellungen")
            
            # Standardarbeitszeiten
            col1, col2 = st.columns(2)
            
            with col1:
                start_time = st.time_input("Standard-Arbeitsbeginn", value=datetime.strptime("08:00", "%H:%M").time(), key="default_start_time")
            
            with col2:
                end_time = st.time_input("Standard-Arbeitsende", value=datetime.strptime("17:00", "%H:%M").time(), key="default_end_time")
            
            # Pausenregelungen
            break_duration = st.slider("Standard-Pausendauer (Stunden)", min_value=0.0, max_value=2.0, value=1.0, step=0.25, key="default_break_duration")
            
            # Arbeitszeitmodelle
            st.subheader("Arbeitszeitmodelle")
            
            models = ["Vollzeit", "Teilzeit", "Gleitzeit", "Schichtarbeit"]
            enabled_models = st.multiselect("Aktivierte Arbeitszeitmodelle", models, default=models, key="enabled_models")
            
            if st.button("Arbeitszeiteinstellungen speichern", key="save_work_settings"):
                # In einer echten App würden diese Einstellungen gespeichert werden
                st.success("Arbeitszeiteinstellungen gespeichert.")
        else:
            st.info("Diese Einstellungen sind nur für Administratoren verfügbar.")
    
    with tab3:
        if st.session_state.get("is_admin", False):
            st.subheader("Systemeinstellungen")
            
            # Benachrichtigungseinstellungen
            st.write("**Benachrichtigungseinstellungen**")
            
            email_notifications = st.checkbox("E-Mail-Benachrichtigungen aktivieren", value=True, key="email_notifications")
            browser_notifications = st.checkbox("Browser-Benachrichtigungen aktivieren", value=True, key="browser_notifications")
            
            # Datenexport
            st.write("**Datenexport**")
            
            if st.button("Alle Daten exportieren"):
                # In einer echten App würde hier ein Datenexport erstellt werden
                st.info("Datenexport wird vorbereitet...")
            
            # Datensicherung
            st.write("**Datensicherung**")
            
            backup_frequency = st.selectbox("Backup-Häufigkeit", ["Täglich", "Wöchentlich", "Monatlich"], key="backup_frequency")
            
            if st.button("Manuelles Backup erstellen"):
                # In einer echten App würde hier ein Backup erstellt werden
                st.info("Backup wird erstellt...")
            
            if st.button("Systemeinstellungen speichern", key="save_system_settings"):
                # In einer echten App würden diese Einstellungen gespeichert werden
                st.success("Systemeinstellungen gespeichert.")
        else:
            st.info("Diese Einstellungen sind nur für Administratoren verfügbar.")

def show_help_page():
    st.title("Hilfe & Support")
    
    # FAQ
    st.subheader("Häufig gestellte Fragen")
    
    with st.expander("Wie erfasse ich meine Arbeitszeit?"):
        st.write("""
        1. Navigieren Sie zur Seite "Check-in/Check-out"
        2. Klicken Sie auf den "Check-in" Button, wenn Sie Ihre Arbeit beginnen
        3. Klicken Sie auf den "Check-out" Button, wenn Sie Ihre Arbeit beenden
        4. Ihre Arbeitszeit wird automatisch berechnet und gespeichert
        """)
    
    with st.expander("Wie beantrage ich Urlaub?"):
        st.write("""
        1. Navigieren Sie zur Seite "Urlaubsanträge"
        2. Wählen Sie den Tab "Neuer Antrag"
        3. Wählen Sie den Zeitraum für Ihren Urlaub
        4. Klicken Sie auf "Urlaubsantrag speichern"
        5. Ihr Antrag wird zur Genehmigung an Ihren Vorgesetzten weitergeleitet
        """)
    
    with st.expander("Wie melde ich mich krank?"):
        st.write("""
        1. Navigieren Sie zur Seite "Krankmeldungen"
        2. Wählen Sie den Tab "Neue Krankmeldung"
        3. Geben Sie den Zeitraum und den Grund für Ihre Krankmeldung an
        4. Klicken Sie auf "Krankmeldung speichern"
        """)
    
    with st.expander("Wie ändere ich mein Passwort?"):
        st.write("""
        1. Navigieren Sie zur Seite "Einstellungen"
        2. Wählen Sie den Tab "Profil"
        3. Geben Sie Ihr aktuelles Passwort und zweimal Ihr neues Passwort ein
        4. Klicken Sie auf "Einstellungen speichern"
        """)
    
    # Kontakt
    st.subheader("Kontakt")
    
    st.write("""
    Bei Fragen oder Problemen wenden Sie sich bitte an:
    
    **Support-Team**  
    E-Mail: support@worktime-app.com  
    Telefon: +49 123 456789
    
    Geschäftszeiten: Mo-Fr, 9:00 - 17:00 Uhr
    """)
    
    # Feedback
    st.subheader("Feedback")
    
    with st.form("feedback_form"):
        feedback_type = st.selectbox("Art des Feedbacks", ["Allgemeines Feedback", "Fehlermeldung", "Verbesserungsvorschlag"], key="feedback_type")
        feedback_text = st.text_area("Ihr Feedback", key="feedback_text")
        
        if st.form_submit_button("Feedback senden"):
            if feedback_text:
                # In einer echten App würde das Feedback gespeichert oder gesendet werden
                st.success("Vielen Dank für Ihr Feedback!")
            else:
                st.error("Bitte geben Sie Ihr Feedback ein.")

# Hauptanwendung
def main():
    # Daten initialisieren
    initialize_data()
    
    # Session-State initialisieren
    init_session_state()
    
    # Seite basierend auf Session-State anzeigen
    if not st.session_state["logged_in"]:
        # Nicht angemeldet
        if st.session_state["current_page"] == "login":
            show_login_page()
        elif st.session_state["current_page"] == "register":
            show_register_page()
        elif st.session_state["current_page"] == "forgot_password":
            show_forgot_password_page()
        elif st.session_state["current_page"] == "reset_password":
            show_reset_password_page()
        else:
            show_login_page()
    else:
        # Angemeldet
        # Sidebar für Navigation
        with st.sidebar:
            st.write(f"Angemeldet als: **{st.session_state['username']}**")
            st.write(f"Rolle: **{st.session_state['user_role']}**")
            
            st.divider()
            
            # Navigationsmenü
            pages = ["Dashboard", "Check-in/Check-out", "Arbeitszeiten", "Krankmeldungen", "Urlaubsanträge"]
            
            # Admin-Seiten
            if st.session_state.get("is_admin", False):
                pages.extend(["Mitarbeiter", "Statistiken"])
            
            # Allgemeine Seiten
            pages.extend(["Einstellungen", "Hilfe"])
            
            # Seitenauswahl
            page = st.radio("Navigation", pages, key="admin_nav" if st.session_state.get("is_admin", False) else "user_nav")
            
            st.divider()
            
            # Abmelden
            if st.button("Abmelden"):
                st.session_state["logged_in"] = False
                st.session_state["current_page"] = "login"
                st.rerun()
        
        # Hauptinhalt basierend auf ausgewählter Seite
        if page == "Dashboard":
            show_dashboard()
        elif page == "Check-in/Check-out":
            show_checkin_page()
        elif page == "Mitarbeiter" and st.session_state.get("is_admin", False):
            show_employees_page_enhanced()
        elif page == "Arbeitszeiten":
            show_work_hours_page()
        elif page == "Krankmeldungen":
            show_sick_leave_page()
        elif page == "Urlaubsanträge":
            show_vacation_page()
        elif page == "Statistiken" and st.session_state.get("is_admin", False):
            show_statistics_page()
        elif page == "Einstellungen":
            show_settings_page()
        elif page == "Hilfe":
            show_help_page()

if __name__ == "__main__":
    main()
