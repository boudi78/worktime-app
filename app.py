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
                
                # Check-out Zeit berechnen
                if i == 0 and emp["status"] == "Anwesend":
                    check_out = None  # Heute noch nicht ausgecheckt
                else:
                    check_out = check_in + timedelta(hours=duration_hours)
                
                # Dauer und Überstunden berechnen
                if check_out:
                    duration = (check_out - check_in).total_seconds() / 3600  # Stunden
                    overtime = max(0, duration - 8)
                else:
                    duration = None
                    overtime = None
                
                st.session_state["checkins"].append({
                    "employee_id": emp["id"],
                    "employee_name": emp["name"],
                    "date": day,
                    "check_in": check_in,
                    "check_out": check_out,
                    "duration": duration,
                    "overtime": overtime
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
        
        # Nächste Benutzer-ID
        st.session_state["next_id"] = 8
        
        st.session_state["data_generated"] = True

# Initialisierung der Session-State-Variablen
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

# Funktion zum Exportieren von Daten als CSV
def export_as_csv(data, filename):
    df = pd.DataFrame(data)
    csv = df.to_csv(index=False)
    return csv, filename

# Funktion zum Exportieren von Daten als PDF
def export_as_pdf(data, title, filename):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=letter)
    elements = []
    
    # Titel hinzufügen
    styles = getSampleStyleSheet()
    elements.append(Paragraph(title, styles['Title']))
    elements.append(Paragraph(f"Erstellt am: {datetime.now().strftime('%d.%m.%Y %H:%M')}", styles['Normal']))
    elements.append(Paragraph(" ", styles['Normal']))  # Leerzeile
    
    # Daten in Tabelle umwandeln
    if data:
        df = pd.DataFrame(data)
        table_data = [df.columns.tolist()] + df.values.tolist()
        
        # Tabelle erstellen
        table = Table(table_data)
        
        # Tabellenstil
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
    else:
        elements.append(Paragraph("Keine Daten verfügbar", styles['Normal']))
    
    # PDF erstellen
    doc.build(elements)
    pdf_data = buffer.getvalue()
    buffer.close()
    
    return pdf_data, filename

# Login-Seite
def show_login_page():
    st.title("WorkTime App")
    st.header("Anmeldung")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        username = st.text_input("Benutzername oder E-Mail", key="login_username")
        password = st.text_input("Passwort", type="password", key="login_password")
        
        col_btn1, col_btn2 = st.columns(2)
        
        with col_btn1:
            if st.button("Anmelden", key="login_button"):
                # Benutzer überprüfen
                user_found = False
                
                for emp in st.session_state["employees"]:
                    if (emp["name"].lower() == username.lower() or emp["email"].lower() == username.lower()) and emp["password"] == password:
                        user_found = True
                        st.session_state["logged_in"] = True
                        st.session_state["user_id"] = emp["id"]
                        st.session_state["username"] = emp["name"]
                        st.session_state["user_email"] = emp["email"]
                        st.session_state["user_role"] = emp["role"]
                        st.session_state["is_admin"] = "admin" in emp["role"].lower()
                        st.session_state["current_page"] = "dashboard"
                        st.success(f"Erfolgreich eingeloggt als {emp['name']}")
                        st.rerun()
                
                if not user_found:
                    st.error("Falscher Benutzername oder Passwort")
        
        with col_btn2:
            if st.button("Passwort vergessen?", key="forgot_password_button"):
                st.session_state["current_page"] = "forgot_password"
                st.rerun()
        
        st.write("Noch kein Konto?")
        if st.button("Registrieren", key="register_button"):
            st.session_state["current_page"] = "register"
            st.rerun()
    
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/3456/3456426.png", width=150) 
        st.write("WorkTime App - Ihre Arbeitszeiterfassung")
        st.write("Version 1.0")

# Registrierungsseite
def show_register_page():
    st.title("Registrierung")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        name = st.text_input("Vollständiger Name", key="register_name")
        email = st.text_input("E-Mail", key="register_email")
        role = st.selectbox("Rolle", ["Mitarbeiter", "Manager", "Administrator"], key="register_role")
        password = st.text_input("Passwort", type="password", key="register_password")
        confirm_password = st.text_input("Passwort bestätigen", type="password", key="register_confirm_password")
        
        if st.button("Registrieren", key="register_submit_button"):
            # Validierung
            if not name or not email or not password:
                st.error("Bitte füllen Sie alle Pflichtfelder aus")
            elif password != confirm_password:
                st.error("Passwörter stimmen nicht überein")
            elif any(emp["email"].lower() == email.lower() for emp in st.session_state["employees"]):
                st.error("Diese E-Mail-Adresse wird bereits verwendet")
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
                
                st.session_state["employees"].append(new_user)
                st.success("Registrierung erfolgreich! Sie können sich jetzt anmelden.")
                
                # Zurück zur Login-Seite
                st.session_state["current_page"] = "login"
                st.rerun()
        
        if st.button("Zurück zur Anmeldung", key="register_back_button"):
            st.session_state["current_page"] = "login"
            st.rerun()
    
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/3456/3456426.png", width=150) 
        st.write("WorkTime App - Ihre Arbeitszeiterfassung")
        st.write("Version 1.0")

# Passwort vergessen Seite
def show_forgot_password_page():
    st.title("Passwort zurücksetzen")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        email = st.text_input("E-Mail-Adresse", key="forgot_email")
        
        if st.button("Passwort zurücksetzen", key="forgot_submit_button"):
            # Überprüfen, ob die E-Mail existiert
            email_exists = any(emp["email"].lower() == email.lower() for emp in st.session_state["employees"])
            
            if email_exists:
                st.success("Eine E-Mail mit Anweisungen zum Zurücksetzen Ihres Passworts wurde gesendet.")
                st.session_state["reset_email"] = email
                st.session_state["current_page"] = "reset_password"
                st.rerun()
            else:
                st.error("Diese E-Mail-Adresse ist nicht registriert.")
        
        if st.button("Zurück zur Anmeldung", key="forgot_back_button"):
            st.session_state["current_page"] = "login"
            st.rerun()
    
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/3456/3456426.png", width=150) 
        st.write("WorkTime App - Ihre Arbeitszeiterfassung")
        st.write("Version 1.0")

# Passwort zurücksetzen Seite
def show_reset_password_page():
    st.title("Neues Passwort festlegen")
    
    col1, col2 = st.columns([2, 1])
    
    with col1:
        st.write(f"E-Mail: {st.session_state['reset_email']}")
        new_password = st.text_input("Neues Passwort", type="password", key="reset_new_password")
        confirm_password = st.text_input("Passwort bestätigen", type="password", key="reset_confirm_password")
        
        if st.button("Passwort ändern", key="reset_submit_button"):
            if not new_password:
                st.error("Bitte geben Sie ein neues Passwort ein")
            elif new_password != confirm_password:
                st.error("Passwörter stimmen nicht überein")
            else:
                # Passwort aktualisieren
                for emp in st.session_state["employees"]:
                    if emp["email"].lower() == st.session_state["reset_email"].lower():
                        emp["password"] = new_password
                        break
                
                st.success("Ihr Passwort wurde erfolgreich geändert. Sie können sich jetzt anmelden.")
                
                # Zurück zur Login-Seite
                st.session_state["current_page"] = "login"
                st.rerun()
        
        if st.button("Zurück zur Anmeldung", key="reset_back_button"):
            st.session_state["current_page"] = "login"
            st.rerun()
    
    with col2:
        st.image("https://cdn-icons-png.flaticon.com/512/3456/3456426.png", width=150) 
        st.write("WorkTime App - Ihre Arbeitszeiterfassung")
        st.write("Version 1.0")

# Dashboard-Seite
def show_dashboard():
    st.title("Dashboard")
    
    # Übersichtskarten
    col1, col2, col3 = st.columns(3)
    
    # Anwesende Mitarbeiter zählen
    present_count = sum(1 for emp in st.session_state["employees"] if emp["status"] == "Anwesend")
    sick_count = sum(1 for emp in st.session_state["employees"] if emp["status"] == "Krank")
    vacation_count = sum(1 for emp in st.session_state["employees"] if emp["status"] == "Urlaub")
    
    with col1:
        st.metric("Mitarbeiter anwesend", f"{present_count}/{len(st.session_state['employees'])}")
    with col2:
        st.metric("Krankmeldungen", sick_count)
    with col3:
        st.metric("Im Urlaub", vacation_count)
    
    # Aktuelle Anwesenheit
    st.subheader("Aktuelle Anwesenheit")
    
    # Tabelle mit Mitarbeiterstatus
    status_df = pd.DataFrame(st.session_state["employees"])
    st.dataframe(status_df[["name", "role", "status"]], use_container_width=True)
    
    # Heutige Check-ins
    st.subheader("Heutige Check-ins")
    today = datetime.now().date()
    today_checkins = [c for c in st.session_state["checkins"] if c["date"] == today]
    
    if today_checkins:
        checkins_df = pd.DataFrame(today_checkins)
        
        # Formatierung der Daten für die Anzeige
        checkins_df["check_in"] = checkins_df["check_in"].apply(lambda x: x.strftime("%H:%M") if pd.notna(x) else "-")
        checkins_df["check_out"] = checkins_df["check_out"].apply(lambda x: x.strftime("%H:%M") if pd.notna(x) else "-")
        
        st.dataframe(checkins_df[["employee_name", "check_in", "check_out"]], use_container_width=True)
    else:
        st.info("Heute wurden noch keine Check-ins registriert.")
    
    # Nächste Ferien
    st.subheader("Nächste Hamburger Ferien")
    today = datetime.now().date()
    upcoming_ferien = [f for f in HAMBURG_FERIEN if datetime.strptime(f["end"], "%Y-%m-%d").date() >= today]
    upcoming_ferien.sort(key=lambda x: datetime.strptime(x["start"], "%Y-%m-%d").date())
    
    if upcoming_ferien:
        next_ferien = upcoming_ferien[0]
        st.info(f"{next_ferien['name']}: {next_ferien['start']} bis {next_ferien['end']}")
    else:
        st.info("Keine kommenden Ferien gefunden.")

# Check-in/Check-out Seite
def show_checkin_page():
    st.title("Check-in/Check-out")
    
    # Mitarbeiter auswählen (in einer echten App wäre dies der angemeldete Benutzer)
    if st.session_state.get("is_admin", False):
        employee = st.selectbox("Mitarbeiter auswählen", 
                               [emp["name"] for emp in st.session_state["employees"] if emp["status"] == "Anwesend"],
                               key="checkin_employee_select")
        employee_id = next(emp["id"] for emp in st.session_state["employees"] if emp["name"] == employee)
    else:
        employee = st.session_state.get("username")
        employee_id = st.session_state.get("user_id")
    
    # Aktuellen Status anzeigen
    
    # Prüfen, ob der Mitarbeiter heute bereits eingecheckt hat
    today = datetime.now().date()
    today_checkin = next((c for c in st.session_state["checkins"] 
                         if c["employee_id"] == employee_id and c["date"] == today), None)
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.subheader("Aktueller Status")
        
        if today_checkin and today_checkin["check_out"] is None:
            # Bereits eingecheckt, aber noch nicht ausgecheckt
            check_in_time = today_checkin["check_in"]
            st.success(f"Eingecheckt seit: {check_in_time.strftime('%H:%M Uhr')}")
            
            if st.button("Check-out", key="checkout_button"):
                # Check-out durchführen
                check_out_time = datetime.now()
                duration = (check_out_time - check_in_time).total_seconds() / 3600  # Stunden
                
                # Eintrag aktualisieren
                for c in st.session_state["checkins"]:
                    if c["employee_id"] == employee_id and c["date"] == today:
                        c["check_out"] = check_out_time
                        c["duration"] = round(duration, 2)
                        c["overtime"] = max(0, round(duration - 8, 2))
                
                st.success(f"Erfolgreich ausgecheckt um {check_out_time.strftime('%H:%M Uhr')}")
                st.info(f"Arbeitszeit heute: {round(duration, 2)} Stunden")
                if duration > 8:
                    st.info(f"Überstunden heute: {round(duration - 8, 2)} Stunden")
                
                st.rerun()
        else:
            # Noch nicht eingecheckt oder bereits ausgecheckt
            if today_checkin and today_checkin["check_out"]:
                st.info(f"Bereits ausgecheckt um {today_checkin['check_out'].strftime('%H:%M Uhr')}")
                st.info(f"Arbeitszeit heute: {round(today_checkin['duration'], 2)} Stunden")
                if today_checkin['overtime'] > 0:
                    st.info(f"Überstunden heute: {round(today_checkin['overtime'], 2)} Stunden")
            else:
                st.warning("Noch nicht eingecheckt")
            
            if st.button("Check-in", key="checkin_button"):
                # Check-in durchführen
                check_in_time = datetime.now()
                
                # Neuen Eintrag erstellen
                new_checkin = {
                    "employee_id": employee_id,
                    "employee_name": employee,
                    "date": today,
                    "check_in": check_in_time,
                    "check_out": None,
                    "duration": None,
                    "overtime": None
                }
                
                st.session_state["checkins"].append(new_checkin)
                st.success(f"Erfolgreich eingecheckt um {check_in_time.strftime('%H:%M Uhr')}")
                st.rerun()
    
    with col2:
        st.subheader("Arbeitszeiten diese Woche")
        
        # Wochenanfang und -ende berechnen
        today = datetime.now().date()
        start_of_week = today - timedelta(days=today.weekday())
        end_of_week = start_of_week + timedelta(days=6)
        
        # Arbeitszeiten dieser Woche
        week_checkins = [c for c in st.session_state["checkins"] 
                        if c["employee_id"] == employee_id and 
                        start_of_week <= c["date"] <= end_of_week]
        
        # Gesamtstunden und Überstunden berechnen
        total_hours = sum(c["duration"] or 0 for c in week_checkins)
        total_overtime = sum(c["overtime"] or 0 for c in week_checkins)
        
        st.metric("Gesamtstunden diese Woche", f"{round(total_hours, 2)}")
        st.metric("Überstunden diese Woche", f"{round(total_overtime, 2)}")
    
    # Letzte Check-ins anzeigen
    st.subheader("Letzte Check-ins")
    employee_checkins = [c for c in st.session_state["checkins"] 
                        if c["employee_id"] == employee_id]
    employee_checkins.sort(key=lambda x: x["date"], reverse=True)
    
    if employee_checkins:
        checkins_df = pd.DataFrame(employee_checkins[:10])  # Letzte 10 Einträge
        
        # Formatierung der Daten für die Anzeige
        checkins_df["date"] = checkins_df["date"].apply(lambda x: x.strftime("%d.%m.%Y"))
        checkins_df["check_in"] = checkins_df["check_in"].apply(lambda x: x.strftime("%H:%M") if pd.notna(x) else "-")
        checkins_df["check_out"] = checkins_df["check_out"].apply(lambda x: x.strftime("%H:%M") if pd.notna(x) else "-")
        
        st.dataframe(checkins_df[["date", "check_in", "check_out", "duration", "overtime"]], use_container_width=True)
        
        # Export-Optionen
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Als CSV exportieren", key="checkin_csv_export"):
                csv_data, filename = export_as_csv(employee_checkins, "checkins.csv")
                st.download_button(
                    label="CSV-Datei herunterladen",
                    data=csv_data,
                    file_name=filename,
                    mime="text/csv",
                    key="checkin_csv_download"
                )
        
        with col2:
            if st.button("Als PDF exportieren", key="checkin_pdf_export"):
                # Daten für PDF vorbereiten
                pdf_data = []
                for checkin in employee_checkins:
                    pdf_data.append({
                        "Datum": checkin["date"].strftime("%d.%m.%Y"),
                        "Check-in": checkin["check_in"].strftime("%H:%M") if checkin["check_in"] else "-",
                        "Check-out": checkin["check_out"].strftime("%H:%M") if checkin["check_out"] else "-",
                        "Stunden": round(checkin["duration"], 2) if checkin["duration"] else "-",
                        "Überstunden": round(checkin["overtime"], 2) if checkin["overtime"] else "-"
                    })
                
                pdf_bytes, filename = export_as_pdf(pdf_data, f"Arbeitszeiten - {employee}", "arbeitszeiten.pdf")
                st.download_button(
                    label="PDF-Datei herunterladen",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    key="checkin_pdf_download"
                )
    else:
        st.info("Keine Check-ins gefunden.")
def delete_employee(employee_id):
    st.session_state["employees"] = [emp for emp in st.session_state["employees"] if emp["id"] != employee_id]
    
    # Auch zugehörige Check-ins, Urlaubsanträge und Krankmeldungen entfernen
    st.session_state["checkins"] = [c for c in st.session_state["checkins"] if c["employee_id"] != employee_id]
    st.session_state["vacation_requests"] = [v for v in st.session_state["vacation_requests"] if v["employee_id"] != employee_id]
    st.session_state["sick_leaves"] = [s for s in st.session_state["sick_leaves"] if s["employee_id"] != employee_id]

    st.success("Mitarbeiter erfolgreich gelöscht!")
    st.rerun()

# Mitarbeiter-Seite (nur für Admins)
def show_employees_page():
    st.title("Mitarbeiterverwaltung")
    
    # Suchfunktion
    search_term = st.text_input("Mitarbeiter suchen", key="employee_search")
    
    # Mitarbeiterliste filtern
    filtered_employees = st.session_state["employees"]
    if search_term:
        filtered_employees = [emp for emp in st.session_state["employees"] 
                             if search_term.lower() in emp["name"].lower() or 
                             search_term.lower() in emp["email"].lower() or
                             search_term.lower() in emp["role"].lower()]
    
    # Mitarbeiterliste anzeigen
    if filtered_employees:
        for i, emp in enumerate(filtered_employees):
            # Expander ohne key Parameter
            with st.expander(f"{emp['name']} - {emp['role']}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**ID:** {emp['id']}")
                    st.write(f"**Email:** {emp['email']}")
                    st.write(f"**Status:** {emp['status']}")
                
                with col2:
                    # Mitarbeiterdetails anzeigen
                    # Check-ins des Mitarbeiters
                    emp_checkins = [c for c in st.session_state["checkins"] if c["employee_id"] == emp["id"]]
                    total_hours = sum(c["duration"] or 0 for c in emp_checkins)
                    total_overtime = sum(c["overtime"] or 0 for c in emp_checkins)
                    
                    st.write(f"**Gesamte Arbeitsstunden:** {round(total_hours, 2)}")
                    st.write(f"**Gesamte Überstunden:** {round(total_overtime, 2)}")
                    
                    # Krankmeldungen und Urlaub
                    sick_leaves = [s for s in st.session_state["sick_leaves"] if s["employee_id"] == emp["id"]]
                    vacations = [v for v in st.session_state["vacation_requests"] if v["employee_id"] == emp["id"]]
                    
                    if sick_leaves:
                        st.write("**Krankmeldungen:**")
                        for sick in sick_leaves:
                            st.write(f"- {sick['start_date'].strftime('%d.%m.%Y')} bis {sick['end_date'].strftime('%d.%m.%Y')}: {sick['reason']}")
                    
                    if vacations:
                        st.write("**Urlaubsanträge:**")
                        for vacation in vacations:
                            st.write(f"- {vacation['start_date'].strftime('%d.%m.%Y')} bis {vacation['end_date'].strftime('%d.%m.%Y')}: {vacation['status']}")
                
                # Aktionen
                col1, col2, col3 = st.columns(3)
                
                with col1:
                    if st.button("Arbeitszeiten anzeigen", key=f"view_hours_{emp['id']}"):
                        # Arbeitszeiten in Session speichern und zur Arbeitszeitseite wechseln
                        st.session_state["selected_employee_id"] = emp["id"]
                        st.session_state["selected_employee_name"] = emp["name"]
                        st.rerun()  # In einer echten App würde hier zur Arbeitszeitseite navigiert werden
                
                with col2:
                    if st.button("Urlaub verwalten", key=f"manage_vacation_{emp['id']}"):
                        # In einer echten App würde hier zur Urlaubsverwaltung navigiert werden
                        pass
                
                with col3:
                    if st.button("Bearbeiten", key=f"edit_{emp['id']}"):
                        # In einer echten App würde hier zum Bearbeitungsformular navigiert werden
                        pass
    else:
        st.info("Keine Mitarbeiter gefunden.")
    
    # Neuen Mitarbeiter hinzufügen
    st.subheader("Neuen Mitarbeiter hinzufügen")
    
    col1, col2 = st.columns(2)
    
    with col1:
        new_name = st.text_input("Name", key="new_employee_name")
        new_email = st.text_input("E-Mail", key="new_employee_email")
    
    with col2:
        new_role = st.selectbox("Rolle", ["Mitarbeiter", "Manager", "Administrator"], key="new_employee_role")
        new_password = st.text_input("Passwort", type="password", key="new_employee_password")
    
    if st.button("Mitarbeiter hinzufügen", key="add_employee_button"):
        if not new_name or not new_email or not new_password:
            st.error("Bitte füllen Sie alle Pflichtfelder aus")
        elif any(emp["email"].lower() == new_email.lower() for emp in st.session_state["employees"]):
            st.error("Diese E-Mail-Adresse wird bereits verwendet")
        else:
            # Neuen Mitarbeiter erstellen
            new_id = st.session_state["next_id"]
            st.session_state["next_id"] += 1
            
            new_employee = {
                "id": new_id,
                "name": new_name,
                "email": new_email,
                "role": new_role,
                "status": "Anwesend",
                "password": new_password
            }
            
            st.session_state["employees"].append(new_employee)
            st.success(f"Mitarbeiter {new_name} erfolgreich hinzugefügt")
            st.rerun()

# Arbeitszeiten-Seite (für Admins)
def show_work_hours_page():
    st.title("Arbeitszeitübersicht")
    
    # Mitarbeiter auswählen
    if "selected_employee_id" in st.session_state and "selected_employee_name" in st.session_state:
        # Vorausgewählter Mitarbeiter von der Mitarbeiterseite
        employee_id = st.session_state["selected_employee_id"]
        employee = st.session_state["selected_employee_name"]
        
        # Session-Variablen löschen
        del st.session_state["selected_employee_id"]
        del st.session_state["selected_employee_name"]
    else:
        # Mitarbeiter aus Dropdown auswählen
        employee = st.selectbox("Mitarbeiter auswählen", 
                               [emp["name"] for emp in st.session_state["employees"]],
                               key="work_hours_employee_select")
        employee_id = next(emp["id"] for emp in st.session_state["employees"] if emp["name"] == employee)
    
    # Zeitraum auswählen
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Von", datetime.now().date() - timedelta(days=30), key="work_hours_start_date")
    with col2:
        end_date = st.date_input("Bis", datetime.now().date(), key="work_hours_end_date")
    
    # Arbeitszeiten filtern
    filtered_checkins = [c for c in st.session_state["checkins"] 
                        if c["employee_id"] == employee_id and 
                        start_date <= c["date"] <= end_date]
    
    # Arbeitszeiten anzeigen
    if filtered_checkins:
        # Tabelle mit Arbeitszeiten
        checkins_df = pd.DataFrame(filtered_checkins)
        checkins_df = checkins_df.sort_values("date", ascending=False)
        
        # Formatierung der Daten für die Anzeige
        checkins_df["date"] = checkins_df["date"].apply(lambda x: x.strftime("%d.%m.%Y"))
        checkins_df["check_in"] = checkins_df["check_in"].apply(lambda x: x.strftime("%H:%M") if pd.notna(x) else "-")
        checkins_df["check_out"] = checkins_df["check_out"].apply(lambda x: x.strftime("%H:%M") if pd.notna(x) else "-")
        
        st.dataframe(checkins_df[["date", "check_in", "check_out", "duration", "overtime"]], use_container_width=True)
        
        # Zusammenfassung
        total_hours = sum(c["duration"] or 0 for c in filtered_checkins)
        total_overtime = sum(c["overtime"] or 0 for c in filtered_checkins)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Gesamte Arbeitsstunden", f"{round(total_hours, 2)}")
        with col2:
            st.metric("Gesamte Überstunden", f"{round(total_overtime, 2)}")
        with col3:
            st.metric("Arbeitstage", len(filtered_checkins))
        
        # Diagramm mit Arbeitszeiten
        chart_data = pd.DataFrame(filtered_checkins)
        chart_data = chart_data.sort_values("date")
        
        # Nur Einträge mit Check-out
        chart_data_filtered = chart_data[chart_data["check_out"].notna()]
        
        if not chart_data_filtered.empty:
            # Datum für die Anzeige formatieren
            chart_data_filtered["date_str"] = chart_data_filtered["date"].apply(lambda x: x.strftime("%d.%m"))
            
            fig = px.bar(chart_data_filtered, x="date_str", y=["duration", "overtime"], 
                        title="Arbeitszeitverlauf",
                        labels={"value": "Stunden", "date_str": "Datum", "variable": "Typ"})
            st.plotly_chart(fig, use_container_width=True)
        
        # Export-Optionen
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Als CSV exportieren", key="work_hours_csv_export"):
                csv_data, filename = export_as_csv(filtered_checkins, f"arbeitszeiten_{employee}.csv")
                st.download_button(
                    label="CSV-Datei herunterladen",
                    data=csv_data,
                    file_name=filename,
                    mime="text/csv",
                    key="work_hours_csv_download"
                )
        
        with col2:
            if st.button("Als PDF exportieren", key="work_hours_pdf_export"):
                # Daten für PDF vorbereiten
                pdf_data = []
                for checkin in filtered_checkins:
                    pdf_data.append({
                        "Datum": checkin["date"].strftime("%d.%m.%Y"),
                        "Check-in": checkin["check_in"].strftime("%H:%M") if checkin["check_in"] else "-",
                        "Check-out": checkin["check_out"].strftime("%H:%M") if checkin["check_out"] else "-",
                        "Stunden": round(checkin["duration"], 2) if checkin["duration"] else "-",
                        "Überstunden": round(checkin["overtime"], 2) if checkin["overtime"] else "-"
                    })
                
                pdf_bytes, filename = export_as_pdf(pdf_data, f"Arbeitszeiten - {employee}", f"arbeitszeiten_{employee}.pdf")
                st.download_button(
                    label="PDF-Datei herunterladen",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    key="work_hours_pdf_download"
                )
    else:
        st.info("Keine Arbeitszeiten im ausgewählten Zeitraum gefunden.")

# Meine Arbeitszeiten-Seite (für Mitarbeiter)
def show_my_work_hours_page():
    st.title("Meine Arbeitszeiten")
    
    # Mitarbeiter-ID aus Session
    employee_id = st.session_state.get("user_id")
    employee = st.session_state.get("username")
    
    # Zeitraum auswählen
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("Von", datetime.now().date() - timedelta(days=30), key="my_hours_start_date")
    with col2:
        end_date = st.date_input("Bis", datetime.now().date(), key="my_hours_end_date")
    
    # Arbeitszeiten filtern
    filtered_checkins = [c for c in st.session_state["checkins"] 
                        if c["employee_id"] == employee_id and 
                        start_date <= c["date"] <= end_date]
    
    # Arbeitszeiten anzeigen
    if filtered_checkins:
        # Tabelle mit Arbeitszeiten
        checkins_df = pd.DataFrame(filtered_checkins)
        checkins_df = checkins_df.sort_values("date", ascending=False)
        
        # Formatierung der Daten für die Anzeige
        checkins_df["date"] = checkins_df["date"].apply(lambda x: x.strftime("%d.%m.%Y"))
        checkins_df["check_in"] = checkins_df["check_in"].apply(lambda x: x.strftime("%H:%M") if pd.notna(x) else "-")
        checkins_df["check_out"] = checkins_df["check_out"].apply(lambda x: x.strftime("%H:%M") if pd.notna(x) else "-")
        
        st.dataframe(checkins_df[["date", "check_in", "check_out", "duration", "overtime"]], use_container_width=True)
        
        # Zusammenfassung
        total_hours = sum(c["duration"] or 0 for c in filtered_checkins)
        total_overtime = sum(c["overtime"] or 0 for c in filtered_checkins)
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Gesamte Arbeitsstunden", f"{round(total_hours, 2)}")
        with col2:
            st.metric("Gesamte Überstunden", f"{round(total_overtime, 2)}")
        with col3:
            st.metric("Arbeitstage", len(filtered_checkins))
        
        # Diagramm mit Arbeitszeiten
        chart_data = pd.DataFrame(filtered_checkins)
        chart_data = chart_data.sort_values("date")
        
        # Nur Einträge mit Check-out
        chart_data_filtered = chart_data[chart_data["check_out"].notna()]
        
        if not chart_data_filtered.empty:
            # Datum für die Anzeige formatieren
            chart_data_filtered["date_str"] = chart_data_filtered["date"].apply(lambda x: x.strftime("%d.%m"))
            
            fig = px.bar(chart_data_filtered, x="date_str", y=["duration", "overtime"], 
                        title="Arbeitszeitverlauf",
                        labels={"value": "Stunden", "date_str": "Datum", "variable": "Typ"})
            st.plotly_chart(fig, use_container_width=True)
        
        # Export-Optionen
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Als CSV exportieren", key="my_hours_csv_export"):
                csv_data, filename = export_as_csv(filtered_checkins, "meine_arbeitszeiten.csv")
                st.download_button(
                    label="CSV-Datei herunterladen",
                    data=csv_data,
                    file_name=filename,
                    mime="text/csv",
                    key="my_hours_csv_download"
                )
        
        with col2:
            if st.button("Als PDF exportieren", key="my_hours_pdf_export"):
                # Daten für PDF vorbereiten
                pdf_data = []
                for checkin in filtered_checkins:
                    pdf_data.append({
                        "Datum": checkin["date"].strftime("%d.%m.%Y"),
                        "Check-in": checkin["check_in"].strftime("%H:%M") if checkin["check_in"] else "-",
                        "Check-out": checkin["check_out"].strftime("%H:%M") if checkin["check_out"] else "-",
                        "Stunden": round(checkin["duration"], 2) if checkin["duration"] else "-",
                        "Überstunden": round(checkin["overtime"], 2) if checkin["overtime"] else "-"
                    })
                
                pdf_bytes, filename = export_as_pdf(pdf_data, "Meine Arbeitszeiten", "meine_arbeitszeiten.pdf")
                st.download_button(
                    label="PDF-Datei herunterladen",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    key="my_hours_pdf_download"
                )
    else:
        st.info("Keine Arbeitszeiten im ausgewählten Zeitraum gefunden.")

# Urlaub & Krankmeldungen Seite
def show_leave_page():
    st.title("Urlaub & Krankmeldungen")
    
    tab1, tab2 = st.tabs(["Krankmeldungen", "Urlaubsanträge"])
    
    with tab1:
        st.subheader("Krankmeldungen")
        
        # Krankmeldungen anzeigen
        if st.session_state.get("is_admin", False):
            # Admin sieht alle Krankmeldungen
            sick_leaves = st.session_state["sick_leaves"]
        else:
            # Mitarbeiter sieht nur eigene Krankmeldungen
            employee_id = st.session_state.get("user_id")
            sick_leaves = [s for s in st.session_state["sick_leaves"] if s["employee_id"] == employee_id]
        
        if sick_leaves:
            sick_df = pd.DataFrame(sick_leaves)
            
            # Formatierung der Daten für die Anzeige
            sick_df["start_date"] = sick_df["start_date"].apply(lambda x: x.strftime("%d.%m.%Y"))
            sick_df["end_date"] = sick_df["end_date"].apply(lambda x: x.strftime("%d.%m.%Y"))
            
            st.dataframe(sick_df[["employee_name", "start_date", "end_date", "reason"]], use_container_width=True)
        else:
            st.info("Keine Krankmeldungen vorhanden.")
        
        # Neue Krankmeldung
        st.subheader("Neue Krankmeldung")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.session_state.get("is_admin", False):
                sick_employee = st.selectbox("Mitarbeiter", 
                                           [emp["name"] for emp in st.session_state["employees"]],
                                           key="sick_employee_select")
                sick_employee_id = next(emp["id"] for emp in st.session_state["employees"] if emp["name"] == sick_employee)
            else:
                sick_employee = st.session_state.get("username")
                sick_employee_id = st.session_state.get("user_id")
                st.write(f"Mitarbeiter: {sick_employee}")
            
            sick_start = st.date_input("Von", datetime.now().date(), key="sick_start")
        with col2:
            sick_reason = st.text_input("Grund", key="sick_reason")
            sick_end = st.date_input("Bis", datetime.now().date() + timedelta(days=3), key="sick_end")
        
        if st.button("Krankmeldung speichern", key="save_sick_button"):
            # Neue Krankmeldung erstellen
            new_sick_leave = {
                "employee_id": sick_employee_id,
                "employee_name": sick_employee,
                "start_date": sick_start,
                "end_date": sick_end,
                "reason": sick_reason
            }
            
            st.session_state["sick_leaves"].append(new_sick_leave)
            
            # Mitarbeiterstatus aktualisieren
            for emp in st.session_state["employees"]:
                if emp["id"] == sick_employee_id:
                    emp["status"] = "Krank"
            
            st.success("Krankmeldung erfolgreich gespeichert.")
            st.rerun()
    
    with tab2:
        st.subheader("Urlaubsanträge")
        
        # Urlaubsanträge anzeigen
        if st.session_state.get("is_admin", False):
            # Admin sieht alle Urlaubsanträge
            vacation_requests = st.session_state["vacation_requests"]
        else:
            # Mitarbeiter sieht nur eigene Urlaubsanträge
            employee_id = st.session_state.get("user_id")
            vacation_requests = [v for v in st.session_state["vacation_requests"] if v["employee_id"] == employee_id]
        
        if vacation_requests:
            vacation_df = pd.DataFrame(vacation_requests)
            
            # Formatierung der Daten für die Anzeige
            vacation_df["start_date"] = vacation_df["start_date"].apply(lambda x: x.strftime("%d.%m.%Y"))
            vacation_df["end_date"] = vacation_df["end_date"].apply(lambda x: x.strftime("%d.%m.%Y"))
            
            st.dataframe(vacation_df[["employee_name", "start_date", "end_date", "status"]], use_container_width=True)
            
            # Admin kann Urlaubsanträge genehmigen/ablehnen
            if st.session_state.get("is_admin", False):
                st.subheader("Urlaubsantrag bearbeiten")
                
                vacation_index = st.selectbox("Urlaubsantrag auswählen", 
                                            range(len(vacation_requests)),
                                            format_func=lambda i: f"{vacation_requests[i]['employee_name']}: {vacation_requests[i]['start_date'].strftime('%d.%m.%Y')} - {vacation_requests[i]['end_date'].strftime('%d.%m.%Y')}",
                                            key="vacation_select_index")
                
                new_status = st.selectbox("Status", ["Ausstehend", "Genehmigt", "Abgelehnt"], key="vacation_status_select")
                
                if st.button("Status aktualisieren", key="update_vacation_status"):
                    # Status aktualisieren
                    vacation_requests[vacation_index]["status"] = new_status
                    
                    # Mitarbeiterstatus aktualisieren, wenn genehmigt
                    if new_status == "Genehmigt":
                        employee_id = vacation_requests[vacation_index]["employee_id"]
                        for emp in st.session_state["employees"]:
                            if emp["id"] == employee_id:
                                emp["status"] = "Urlaub"
                    
                    st.success("Status erfolgreich aktualisiert.")
                    st.rerun()
        else:
            st.info("Keine Urlaubsanträge vorhanden.")
        
        # Neuer Urlaubsantrag
        st.subheader("Neuer Urlaubsantrag")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.session_state.get("is_admin", False):
                vacation_employee = st.selectbox("Mitarbeiter für Urlaub", 
                                               [emp["name"] for emp in st.session_state["employees"]],
                                               key="vacation_employee_select")
                vacation_employee_id = next(emp["id"] for emp in st.session_state["employees"] if emp["name"] == vacation_employee)
            else:
                vacation_employee = st.session_state.get("username")
                vacation_employee_id = st.session_state.get("user_id")
                st.write(f"Mitarbeiter: {vacation_employee}")
            
            vacation_start = st.date_input("Urlaub von", datetime.now().date() + timedelta(days=7), key="vacation_start")
        with col2:
            if st.session_state.get("is_admin", False):
                vacation_status = st.selectbox("Status", ["Ausstehend", "Genehmigt", "Abgelehnt"], key="new_vacation_status")
            else:
                vacation_status = "Ausstehend"
                st.write("Status: Ausstehend")
            
            vacation_end = st.date_input("Urlaub bis", datetime.now().date() + timedelta(days=14), key="vacation_end")
        
        if st.button("Urlaubsantrag speichern", key="save_vacation_button"):
            # Neuen Urlaubsantrag erstellen
            new_vacation = {
                "employee_id": vacation_employee_id,
                "employee_name": vacation_employee,
                "start_date": vacation_start,
                "end_date": vacation_end,
                "status": vacation_status
            }
            
            st.session_state["vacation_requests"].append(new_vacation)
            
            # Mitarbeiterstatus aktualisieren, wenn genehmigt
            if vacation_status == "Genehmigt":
                for emp in st.session_state["employees"]:
                    if emp["id"] == vacation_employee_id:
                        emp["status"] = "Urlaub"
            
            st.success("Urlaubsantrag erfolgreich gespeichert.")
            st.rerun()

# Kalender-Seite
def show_calendar_page():
    st.title("Kalender")
    
    # Monatsauswahl
    current_month = datetime.now().month
    current_year = datetime.now().year
    
    col1, col2 = st.columns(2)
    with col1:
        month = st.selectbox("Monat auswählen", 
                           range(1, 13), 
                           index=current_month-1,
                           format_func=lambda m: calendar.month_name[m],
                           key="calendar_month")
    with col2:
        year = st.selectbox("Jahr auswählen", range(2024, 2027), index=current_year-2024, key="calendar_year")
    
    # Kalender erstellen
    cal = calendar.monthcalendar(year, month)
    month_name = calendar.month_name[month]
    
    st.subheader(f"{month_name} {year}")
    
    # Kalender-Tabelle
    cal_df = pd.DataFrame(cal)
    cal_df.columns = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
    
    # Feiertage und Ferien markieren
    styled_df = cal_df.copy()
    
    # Kalender anzeigen
    st.dataframe(styled_df, use_container_width=True)
    
    # Legende
    st.write("Legende:")
    col1, col2, col3 = st.columns(3)
    with col1:
        st.markdown('<span style="background-color: yellow; padding: 5px;">Krankmeldung</span>', unsafe_allow_html=True)
    with col2:
        st.markdown('<span style="background-color: lightblue; padding: 5px;">Urlaub</span>', unsafe_allow_html=True)
    with col3:
        st.markdown('<span style="background-color: lightgreen; padding: 5px;">Feiertag</span>', unsafe_allow_html=True)
    
    # Hamburger Ferien anzeigen
    st.subheader("Hamburger Ferien 2025")
    
    # Ferien als Tabelle anzeigen
    ferien_df = pd.DataFrame(HAMBURG_FERIEN)
    st.dataframe(ferien_df, use_container_width=True)
    
    # Export-Optionen
    col1, col2 = st.columns(2)
    
    with col1:
        if st.button("Ferien als CSV exportieren", key="ferien_csv_export"):
            csv_data, filename = export_as_csv(HAMBURG_FERIEN, "hamburg_ferien.csv")
            st.download_button(
                label="CSV-Datei herunterladen",
                data=csv_data,
                file_name=filename,
                mime="text/csv",
                key="ferien_csv_download"
            )
    
    with col2:
        if st.button("Ferien als PDF exportieren", key="ferien_pdf_export"):
            # Daten für PDF vorbereiten
            pdf_data = []
            for ferien in HAMBURG_FERIEN:
                pdf_data.append({
                    "Ferienname": ferien["name"],
                    "Beginn": ferien["start"],
                    "Ende": ferien["end"]
                })
            
            pdf_bytes, filename = export_as_pdf(pdf_data, "Hamburger Ferien 2025", "hamburg_ferien.pdf")
            st.download_button(
                label="PDF-Datei herunterladen",
                data=pdf_bytes,
                file_name=filename,
                mime="application/pdf",
                key="ferien_pdf_download"
            )
    
    # Ereignisse im Kalender
    if st.session_state.get("is_admin", False):
        st.subheader("Alle Ereignisse im Kalender")
        
        # Krankmeldungen
        st.write("**Krankmeldungen:**")
        for sick in st.session_state["sick_leaves"]:
            st.write(f"- {sick['employee_name']}: {sick['start_date'].strftime('%d.%m.%Y')} bis {sick['end_date'].strftime('%d.%m.%Y')} ({sick['reason']})")
        
        # Urlaubsanträge
        st.write("**Genehmigte Urlaubsanträge:**")
        approved_vacations = [v for v in st.session_state["vacation_requests"] if v["status"] == "Genehmigt"]
        if approved_vacations:
            for vacation in approved_vacations:
                st.write(f"- {vacation['employee_name']}: {vacation['start_date'].strftime('%d.%m.%Y')} bis {vacation['end_date'].strftime('%d.%m.%Y')}")
        else:
            st.info("Keine genehmigten Urlaubsanträge vorhanden.")
    else:
        # Mitarbeiter sieht nur eigene Ereignisse
        employee_id = st.session_state.get("user_id")
        
        st.subheader("Meine Ereignisse im Kalender")
        
        # Krankmeldungen
        st.write("**Meine Krankmeldungen:**")
        my_sick_leaves = [s for s in st.session_state["sick_leaves"] if s["employee_id"] == employee_id]
        if my_sick_leaves:
            for sick in my_sick_leaves:
                st.write(f"- {sick['start_date'].strftime('%d.%m.%Y')} bis {sick['end_date'].strftime('%d.%m.%Y')} ({sick['reason']})")
        else:
            st.info("Keine Krankmeldungen vorhanden.")
        
        # Urlaubsanträge
        st.write("**Meine Urlaubsanträge:**")
        my_vacations = [v for v in st.session_state["vacation_requests"] if v["employee_id"] == employee_id]
        if my_vacations:
            for vacation in my_vacations:
                st.write(f"- {vacation['start_date'].strftime('%d.%m.%Y')} bis {vacation['end_date'].strftime('%d.%m.%Y')} ({vacation['status']})")
        else:
            st.info("Keine Urlaubsanträge vorhanden.")

# Statistiken-Seite (nur für Admins)
def show_statistics_page():
    st.title("Statistiken")
    
    # Zeitraum auswählen
    col1, col2 = st.columns(2)
    with col1:
        stats_start_date = st.date_input("Statistik von", datetime.now().date() - timedelta(days=30), key="stats_start")
    with col2:
        stats_end_date = st.date_input("Statistik bis", datetime.now().date(), key="stats_end")
    
    # Arbeitszeiten filtern
    filtered_checkins = [c for c in st.session_state["checkins"] 
                        if c["check_out"] is not None and
                        stats_start_date <= c["date"] <= stats_end_date]
    
    if filtered_checkins:
        # Arbeitszeiten pro Mitarbeiter
        st.subheader("Arbeitszeiten pro Mitarbeiter")
        
        # Daten für das Diagramm vorbereiten
        employee_hours = {}
        employee_overtime = {}
        
        for checkin in filtered_checkins:
            emp_name = checkin["employee_name"]
            if emp_name not in employee_hours:
                employee_hours[emp_name] = 0
                employee_overtime[emp_name] = 0
            
            employee_hours[emp_name] += checkin["duration"] or 0
            employee_overtime[emp_name] += checkin["overtime"] or 0
        
        # Diagramm erstellen
        hours_df = pd.DataFrame({
            "Mitarbeiter": list(employee_hours.keys()),
            "Arbeitsstunden": list(employee_hours.values()),
            "Überstunden": list(employee_overtime.values())
        })
        
        fig = px.bar(hours_df, x="Mitarbeiter", y=["Arbeitsstunden", "Überstunden"], 
                    title="Arbeitszeiten pro Mitarbeiter",
                    labels={"value": "Stunden", "variable": "Typ"})
        st.plotly_chart(fig, use_container_width=True)
        
        # Arbeitszeiten pro Tag
        st.subheader("Arbeitszeiten pro Tag")
        
        # Daten für das Diagramm vorbereiten
        daily_hours = {}
        
        for checkin in filtered_checkins:
            date_str = checkin["date"].strftime("%d.%m.%Y")
            if date_str not in daily_hours:
                daily_hours[date_str] = 0
            
            daily_hours[date_str] += checkin["duration"] or 0
        
        # Diagramm erstellen
        daily_df = pd.DataFrame({
            "Datum": list(daily_hours.keys()),
            "Stunden": list(daily_hours.values())
        })
        
        # Nach Datum sortieren
        daily_df["Datum"] = pd.to_datetime(daily_df["Datum"], format="%d.%m.%Y")
        daily_df = daily_df.sort_values("Datum")
        daily_df["Datum"] = daily_df["Datum"].dt.strftime("%d.%m.%Y")
        
        fig = px.line(daily_df, x="Datum", y="Stunden", 
                     title="Arbeitszeiten pro Tag",
                     labels={"Stunden": "Stunden", "Datum": "Datum"})
        st.plotly_chart(fig, use_container_width=True)
        
        # Zusammenfassung
        st.subheader("Zusammenfassung")
        
        total_hours = sum(checkin["duration"] or 0 for checkin in filtered_checkins)
        total_overtime = sum(checkin["overtime"] or 0 for checkin in filtered_checkins)
        avg_hours = total_hours / len(set(checkin["date"] for checkin in filtered_checkins))
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Gesamte Arbeitsstunden", f"{round(total_hours, 2)}")
        with col2:
            st.metric("Gesamte Überstunden", f"{round(total_overtime, 2)}")
        with col3:
            st.metric("Durchschnittliche Stunden pro Tag", f"{round(avg_hours, 2)}")
        
        # Export-Optionen
        col1, col2 = st.columns(2)
        
        with col1:
            if st.button("Statistiken als CSV exportieren", key="stats_csv_export"):
                # Daten für CSV vorbereiten
                csv_data = []
                for emp_name in employee_hours:
                    csv_data.append({
                        "Mitarbeiter": emp_name,
                        "Arbeitsstunden": round(employee_hours[emp_name], 2),
                        "Überstunden": round(employee_overtime[emp_name], 2)
                    })
                
                csv_bytes, filename = export_as_csv(csv_data, "statistiken.csv")
                st.download_button(
                    label="CSV-Datei herunterladen",
                    data=csv_bytes,
                    file_name=filename,
                    mime="text/csv",
                    key="stats_csv_download"
                )
        
        with col2:
            if st.button("Statistiken als PDF exportieren", key="stats_pdf_export"):
                # Daten für PDF vorbereiten
                pdf_data = []
                for emp_name in employee_hours:
                    pdf_data.append({
                        "Mitarbeiter": emp_name,
                        "Arbeitsstunden": round(employee_hours[emp_name], 2),
                        "Überstunden": round(employee_overtime[emp_name], 2)
                    })
                
                pdf_bytes, filename = export_as_pdf(pdf_data, "Arbeitszeit-Statistiken", "statistiken.pdf")
                st.download_button(
                    label="PDF-Datei herunterladen",
                    data=pdf_bytes,
                    file_name=filename,
                    mime="application/pdf",
                    key="stats_pdf_download"
                )
    else:
        st.info("Keine Daten im ausgewählten Zeitraum gefunden.")

# Einstellungen-Seite
def show_settings_page():
    st.title("Einstellungen")
    
    # Persönliche Einstellungen
    st.subheader("Persönliche Einstellungen")
    
    col1, col2 = st.columns(2)
    
    with col1:
        # Aktuellen Benutzer finden
        user = next((emp for emp in st.session_state["employees"] if emp["id"] == st.session_state.get("user_id")), None)
        
        if user:
            name = st.text_input("Name", value=user["name"], key="settings_name")
            email = st.text_input("E-Mail", value=user["email"], key="settings_email")
        else:
            name = st.text_input("Name", key="settings_name")
            email = st.text_input("E-Mail", key="settings_email")
    
    with col2:
        current_password = st.text_input("Aktuelles Passwort", type="password", key="settings_current_password")
        new_password = st.text_input("Neues Passwort", type="password", key="settings_new_password")
        confirm_password = st.text_input("Passwort bestätigen", type="password", key="settings_confirm_password")
    
    if st.button("Einstellungen speichern", key="save_settings_button"):
        if user:
            # Validierung
            if new_password and new_password != confirm_password:
                st.error("Neue Passwörter stimmen nicht überein")
            elif new_password and current_password != user["password"]:
                st.error("Aktuelles Passwort ist falsch")
            else:
                # Benutzer aktualisieren
                user["name"] = name
                user["email"] = email
                
                if new_password:
                    user["password"] = new_password
                
                st.success("Einstellungen erfolgreich gespeichert")
                
                # Session-Variablen aktualisieren
                st.session_state["username"] = name
                st.session_state["user_email"] = email
                
                st.rerun()
        else:
            st.error("Benutzer nicht gefunden")
    
    # Admin-Einstellungen
    if st.session_state.get("is_admin", False):
        st.subheader("Admin-Einstellungen")
        
        # Arbeitszeiteinstellungen
        st.write("**Arbeitszeiteinstellungen**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            work_start = st.time_input("Arbeitsbeginn", datetime.strptime("08:00", "%H:%M").time(), key="work_start")
            work_end = st.time_input("Arbeitsende", datetime.strptime("17:00", "%H:%M").time(), key="work_end")
        
        with col2:
            break_duration = st.number_input("Pausendauer (Stunden)", min_value=0.0, max_value=2.0, value=1.0, step=0.5, key="break_duration")
            overtime_threshold = st.number_input("Überstunden ab (Stunden)", min_value=6.0, max_value=10.0, value=8.0, step=0.5, key="overtime_threshold")
        
        if st.button("Arbeitszeiteinstellungen speichern", key="save_work_settings"):
            st.success("Arbeitszeiteinstellungen erfolgreich gespeichert")
        
        # Systemeinstellungen
        st.write("**Systemeinstellungen**")
        
        col1, col2 = st.columns(2)
        
        with col1:
            data_retention = st.number_input("Datenspeicherung (Monate)", min_value=1, max_value=60, value=24, key="data_retention")
            auto_logout = st.number_input("Automatische Abmeldung nach (Minuten)", min_value=5, max_value=120, value=30, key="auto_logout")
        
        with col2:
            backup_enabled = st.checkbox("Automatische Backups aktivieren", value=True, key="backup_enabled")
            backup_frequency = st.selectbox("Backup-Häufigkeit", ["Täglich", "Wöchentlich", "Monatlich"], key="backup_frequency")
        
        if st.button("Systemeinstellungen speichern", key="save_system_settings"):
            st.success("Systemeinstellungen erfolgreich gespeichert")

# Hauptanwendung
def main():
    # Beispieldaten generieren
    generate_sample_data()
    
    # Session-State initialisieren
    init_session_state()
    
    # Seitenauswahl basierend auf aktuellem Status
    if not st.session_state["logged_in"]:
        if st.session_state["current_page"] == "register":
            show_register_page()
        elif st.session_state["current_page"] == "forgot_password":
            show_forgot_password_page()
        elif st.session_state["current_page"] == "reset_password":
            show_reset_password_page()
        else:
            show_login_page()
    else:
        # Seitenleiste
        st.sidebar.title("Navigation")
        
        # Benutzerinfo anzeigen
        st.sidebar.success(f"Eingeloggt als: {st.session_state.get('username')}")
        st.sidebar.info(f"Rolle: {st.session_state.get('user_role')}")
        
        # Navigation
        if st.session_state.get("is_admin", False):
            page = st.sidebar.selectbox(
                "Seite auswählen:",
                ["Dashboard", "Check-in/Check-out", "Mitarbeiter", "Arbeitszeiten", 
                 "Urlaub & Krankmeldungen", "Kalender", "Statistiken", "Einstellungen"],
                key="admin_nav"
            )
        else:
            page = st.sidebar.selectbox(
                "Seite auswählen:",
                ["Dashboard", "Check-in/Check-out", "Meine Arbeitszeiten", 
                 "Urlaub & Krankmeldungen", "Kalender", "Einstellungen"],
                key="user_nav"
            )
        
        # Suchfunktion
        st.sidebar.subheader("Suche")
        search_term = st.sidebar.text_input("Suchbegriff eingeben", key="sidebar_search")
        if search_term:
            st.sidebar.info(f"Suche nach: {search_term}")
            # Hamburger Ferien suchen
            if "hamburg" in search_term.lower() and "ferien" in search_term.lower():
                st.sidebar.success("Hamburger Ferien gefunden!")
                for ferien in HAMBURG_FERIEN:
                    st.sidebar.write(f"{ferien['name']}: {ferien['start']} bis {ferien['end']}")
        
        # Logout-Button
        if st.sidebar.button("Abmelden", key="logout_button"):
            st.session_state.clear()
            st.rerun()
        
        # Hauptinhalt basierend auf ausgewählter Seite
        if page == "Dashboard":
            show_dashboard()
        elif page == "Check-in/Check-out":
            show_checkin_page()
        elif page == "Mitarbeiter" and st.session_state.get("is_admin", False):
            show_employees_page()
        elif page == "Arbeitszeiten" and st.session_state.get("is_admin", False):
            show_work_hours_page()
        elif page == "Meine Arbeitszeiten":
            show_my_work_hours_page()
        elif page == "Urlaub & Krankmeldungen":
            show_leave_page()
        elif page == "Kalender":
            show_calendar_page()
        elif page == "Statistiken" and st.session_state.get("is_admin", False):
            show_statistics_page()
        elif page == "Einstellungen":
            show_settings_page()

if __name__ == "__main__":
    main()


