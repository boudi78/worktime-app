# Implementierung der Krankmeldungs- und Urlaubsoptimierungen

# 1. Begründungsmöglichkeit für Krankmeldungen
def implement_sick_leave_reasons():
    """
    Implementierung der Begründungsmöglichkeit für Krankmeldungen
    """
    def show_enhanced_sick_leave_page():
        """
        Zeigt die erweiterte Krankmeldungsseite mit Begründungsmöglichkeit an
        """
        st.title("Krankmeldungen")
        
        # Mitarbeiter auswählen
        if st.session_state.get("is_admin", False):
            employee = st.selectbox("Mitarbeiter auswählen", 
                                   [emp["name"] for emp in st.session_state["employees"]],
                                   key="sick_leave_employee_select")
            employee_id = next(emp["id"] for emp in st.session_state["employees"] if emp["name"] == employee)
        else:
            employee = st.session_state.get("username")
            employee_id = st.session_state.get("user_id")
            st.write(f"Mitarbeiter: {employee}")
        
        # Bestehende Krankmeldungen anzeigen
        st.subheader("Bestehende Krankmeldungen")
        
        sick_leaves = [s for s in st.session_state["sick_leaves"] if s["employee_id"] == employee_id]
        sick_leaves.sort(key=lambda x: x["start_date"], reverse=True)
        
        if sick_leaves:
            for sick_leave in sick_leaves:
                with st.expander(f"{sick_leave['start_date']} bis {sick_leave['end_date']} - {sick_leave.get('status', 'Eingereicht')}"):
                    st.write(f"**Zeitraum:** {sick_leave['start_date']} bis {sick_leave['end_date']}")
                    st.write(f"**Status:** {sick_leave.get('status', 'Eingereicht')}")
                    
                    # Begründung anzeigen
                    if "reason" in sick_leave and sick_leave["reason"]:
                        st.write(f"**Begründung:** {sick_leave['reason']}")
                    else:
                        st.write("**Begründung:** Keine angegeben")
                    
                    # Kategorie anzeigen
                    if "category" in sick_leave and sick_leave["category"]:
                        st.write(f"**Kategorie:** {sick_leave['category']}")
                    
                    # Dokumente anzeigen
                    if "documents" in sick_leave and sick_leave["documents"]:
                        st.write("**Dokumente:**")
                        for doc in sick_leave["documents"]:
                            st.write(f"- {doc['name']} (hochgeladen am {doc['upload_date']})")
                    
                    # Admin-Kommentar anzeigen
                    if "admin_comment" in sick_leave and sick_leave["admin_comment"]:
                        st.write(f"**Admin-Kommentar:** {sick_leave['admin_comment']}")
                    
                    # Bearbeiten/Löschen-Buttons (nur für eigene Krankmeldungen oder als Admin)
                    if st.session_state.get("is_admin", False) or sick_leave.get("status") == "Eingereicht":
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Bearbeiten", key=f"edit_sick_{sick_leave.get('id', 0)}"):
                                st.session_state["edit_sick_leave"] = sick_leave
                                st.session_state["show_edit_sick_form"] = True
                        with col2:
                            if st.button("Löschen", key=f"delete_sick_{sick_leave.get('id', 0)}"):
                                st.session_state["sick_leaves"].remove(sick_leave)
                                st.success("Krankmeldung wurde gelöscht.")
                                st.rerun()
        else:
            st.info("Keine Krankmeldungen vorhanden.")
        
        # Neue Krankmeldung erstellen
        st.subheader("Neue Krankmeldung erstellen")
        
        # Formular für neue Krankmeldung
        with st.form("new_sick_leave_form"):
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Von", value=datetime.now().date(), key="new_sick_start")
            with col2:
                end_date = st.date_input("Bis", value=datetime.now().date(), key="new_sick_end")
            
            # Begründung hinzufügen
            reason = st.text_area("Begründung", key="new_sick_reason", 
                                help="Bitte geben Sie eine kurze Begründung für Ihre Krankmeldung an.")
            
            # Kategorie auswählen
            categories = ["Erkältung/Grippe", "Magen-Darm", "Verletzung", "Arztbesuch", "Operation", "Psychische Gesundheit", "Sonstiges"]
            category = st.selectbox("Kategorie", categories, key="new_sick_category")
            
            # Dokument hochladen (simuliert)
            upload_document = st.checkbox("Krankenschein hochladen", key="upload_sick_document")
            
            if upload_document:
                uploaded_file = st.file_uploader("Krankenschein hochladen", type=["pdf", "jpg", "png"], key="sick_document")
                
                # In einer echten App würde hier die Datei gespeichert werden
                if uploaded_file is not None:
                    st.success(f"Datei '{uploaded_file.name}' erfolgreich hochgeladen.")
            
            # Formular absenden
            submit_button = st.form_submit_button("Krankmeldung einreichen")
            
            if submit_button:
                # Validierung
                if end_date < start_date:
                    st.error("Das Enddatum kann nicht vor dem Startdatum liegen.")
                else:
                    # Neue Krankmeldung erstellen
                    new_sick_leave = {
                        "id": len(st.session_state["sick_leaves"]) + 1,
                        "employee_id": employee_id,
                        "start_date": start_date,
                        "end_date": end_date,
                        "reason": reason,
                        "category": category,
                        "status": "Eingereicht",
                        "created_at": datetime.now()
                    }
                    
                    # Dokument hinzufügen, falls vorhanden
                    if upload_document and uploaded_file is not None:
                        new_sick_leave["documents"] = [{
                            "name": uploaded_file.name,
                            "upload_date": datetime.now().date(),
                            "file_path": f"uploads/{uploaded_file.name}"  # In einer echten App würde hier der tatsächliche Pfad stehen
                        }]
                    
                    # Zur Liste hinzufügen
                    st.session_state["sick_leaves"].append(new_sick_leave)
                    
                    # Mitarbeiterstatus aktualisieren
                    if datetime.now().date() >= start_date and datetime.now().date() <= end_date:
                        employee_obj = next((emp for emp in st.session_state["employees"] if emp["id"] == employee_id), None)
                        if employee_obj:
                            employee_obj["status"] = "Krank"
                    
                    st.success("Krankmeldung wurde erfolgreich eingereicht.")
                    
                    # Benachrichtigung an Admins senden (simuliert)
                    if "notifications" not in st.session_state:
                        st.session_state["notifications"] = []
                    
                    st.session_state["notifications"].append({
                        "type": "sick_leave",
                        "employee_id": employee_id,
                        "employee_name": employee,
                        "message": f"Neue Krankmeldung von {employee} vom {start_date} bis {end_date}",
                        "timestamp": datetime.now(),
                        "read": False
                    })
                    
                    st.info("Benachrichtigung an Administratoren wurde gesendet.")
                    st.rerun()
        
        # Formular zum Bearbeiten einer bestehenden Krankmeldung
        if st.session_state.get("show_edit_sick_form", False) and "edit_sick_leave" in st.session_state:
            sick_leave = st.session_state["edit_sick_leave"]
            
            st.subheader("Krankmeldung bearbeiten")
            
            with st.form("edit_sick_leave_form"):
                col1, col2 = st.columns(2)
                with col1:
                    start_date = st.date_input("Von", value=sick_leave["start_date"], key="edit_sick_start")
                with col2:
                    end_date = st.date_input("Bis", value=sick_leave["end_date"], key="edit_sick_end")
                
                # Begründung bearbeiten
                reason = st.text_area("Begründung", value=sick_leave.get("reason", ""), key="edit_sick_reason")
                
                # Kategorie bearbeiten
                categories = ["Erkältung/Grippe", "Magen-Darm", "Verletzung", "Arztbesuch", "Operation", "Psychische Gesundheit", "Sonstiges"]
                category = st.selectbox("Kategorie", categories, 
                                      index=categories.index(sick_leave.get("category", "Sonstiges")) if "category" in sick_leave else 6,
                                      key="edit_sick_category")
                
                # Status bearbeiten (nur für Admins)
                if st.session_state.get("is_admin", False):
                    status_options = ["Eingereicht", "Bestätigt", "Abgelehnt"]
                    status = st.selectbox("Status", status_options, 
                                        index=status_options.index(sick_leave.get("status", "Eingereicht")),
                                        key="edit_sick_status")
                    
                    # Admin-Kommentar
                    admin_comment = st.text_area("Admin-Kommentar", value=sick_leave.get("admin_comment", ""), 
                                              key="edit_sick_admin_comment")
                
                # Dokument hochladen (simuliert)
                upload_document = st.checkbox("Neuen Krankenschein hochladen", key="edit_upload_sick_document")
                
                if upload_document:
                    uploaded_file = st.file_uploader("Krankenschein hochladen", type=["pdf", "jpg", "png"], key="edit_sick_document")
                    
                    # In einer echten App würde hier die Datei gespeichert werden
                    if uploaded_file is not None:
                        st.success(f"Datei '{uploaded_file.name}' erfolgreich hochgeladen.")
                
                # Formular absenden
                submit_button = st.form_submit_button("Änderungen speichern")
                
                if submit_button:
                    # Validierung
                    if end_date < start_date:
                        st.error("Das Enddatum kann nicht vor dem Startdatum liegen.")
                    else:
                        # Krankmeldung aktualisieren
                        sick_leave["start_date"] = start_date
                        sick_leave["end_date"] = end_date
                        sick_leave["reason"] = reason
                        sick_leave["category"] = category
                        sick_leave["modified_at"] = datetime.now()
                        
                        # Status und Admin-Kommentar aktualisieren (nur für Admins)
                        if st.session_state.get("is_admin", False):
                            sick_leave["status"] = status
                            sick_leave["admin_comment"] = admin_comment
                        
                        # Dokument hinzufügen, falls vorhanden
                        if upload_document and uploaded_file is not None:
                            if "documents" not in sick_leave:
                                sick_leave["documents"] = []
                            
                            sick_leave["documents"].append({
                                "name": uploaded_file.name,
                                "upload_date": datetime.now().date(),
                                "file_path": f"uploads/{uploaded_file.name}"  # In einer echten App würde hier der tatsächliche Pfad stehen
                            })
                        
                        # Mitarbeiterstatus aktualisieren
                        if datetime.now().date() >= start_date and datetime.now().date() <= end_date:
                            employee_obj = next((emp for emp in st.session_state["employees"] if emp["id"] == employee_id), None)
                            if employee_obj:
                                if sick_leave.get("status") == "Bestätigt":
                                    employee_obj["status"] = "Krank"
                                elif sick_leave.get("status") == "Abgelehnt":
                                    employee_obj["status"] = "Anwesend"
                        
                        st.success("Krankmeldung wurde erfolgreich aktualisiert.")
                        
                        # Benachrichtigung senden, wenn Status geändert wurde (simuliert)
                        if st.session_state.get("is_admin", False) and sick_leave.get("status") in ["Bestätigt", "Abgelehnt"]:
                            if "notifications" not in st.session_state:
                                st.session_state["notifications"] = []
                            
                            employee_obj = next((emp for emp in st.session_state["employees"] if emp["id"] == sick_leave["employee_id"]), {"name": "Unbekannt"})
                            
                            st.session_state["notifications"].append({
                                "type": "sick_leave_status",
                                "employee_id": sick_leave["employee_id"],
                                "employee_name": employee_obj["name"],
                                "message": f"Status Ihrer Krankmeldung vom {sick_leave['start_date']} bis {sick_leave['end_date']} wurde auf '{sick_leave['status']}' geändert.",
                                "timestamp": datetime.now(),
                                "read": False
                            })
                            
                            st.info(f"Benachrichtigung an {employee_obj['name']} wurde gesendet.")
                        
                        # Formular zurücksetzen
                        st.session_state["show_edit_sick_form"] = False
                        del st.session_state["edit_sick_leave"]
                        st.rerun()
            
            # Abbrechen-Button
            if st.button("Abbrechen"):
                st.session_state["show_edit_sick_form"] = False
                del st.session_state["edit_sick_leave"]
                st.rerun()
    
    # Funktion zur Anzeige der Krankmeldungsstatistiken
    def show_sick_leave_statistics():
        """
        Zeigt Statistiken zu Krankmeldungen an
        """
        st.title("Krankmeldungsstatistiken")
        
        # Nur für Admins zugänglich
        if not st.session_state.get("is_admin", False):
            st.error("Sie haben keine Berechtigung für diese Seite.")
            return
        
        # Zeitraum auswählen
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Von", 
                value=datetime.now().date() - timedelta(days=365),
                key="sick_stats_start_date"
            )
        with col2:
            end_date = st.date_input(
                "Bis", 
                value=datetime.now().date(),
                key="sick_stats_end_date"
            )
        
        # Krankmeldungen für den Zeitraum abrufen
        sick_leaves = [s for s in st.session_state["sick_leaves"] 
                      if s.get("status") == "Bestätigt" and
                      not (s["end_date"] < start_date or s["start_date"] > end_date)]
        
        if not sick_leaves:
            st.info("Keine bestätigten Krankmeldungen im ausgewählten Zeitraum gefunden.")
            return
        
        # Gesamtstatistik
        st.subheader("Gesamtstatistik")
        
        total_days = sum((min(s["end_date"], end_date) - max(s["start_date"], start_date)).days + 1 for s in sick_leaves)
        total_employees = len(set(s["employee_id"] for s in sick_leaves))
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Anzahl Krankmeldungen", len(sick_leaves))
        with col2:
            st.metric("Gesamte Krankheitstage", total_days)
        with col3:
            st.metric("Betroffene Mitarbeiter", total_employees)
        
        # Krankmeldungen nach Kategorie
        st.subheader("Krankmeldungen nach Kategorie")
        
        # Kategorien zählen
        category_counts = {}
        for s in sick_leaves:
            category = s.get("category", "Sonstiges")
            if category in category_counts:
                category_counts[category] += 1
            else:
                category_counts[category] = 1
        
        # Diagramm erstellen
        if category_counts:
            fig = px.pie(
                names=list(category_counts.keys()),
                values=list(category_counts.values()),
                title="Verteilung nach Kategorie"
            )
            st.plotly_chart(fig)
        
        # Krankmeldungen nach Monat
        st.subheader("Krankmeldungen nach Monat")
        
        # Monate zählen
        month_counts = {}
        for s in sick_leaves:
            # Alle Tage der Krankmeldung durchgehen
            current_date = max(s["start_date"], start_date)
            end = min(s["end_date"], end_date)
            
            while current_date <= end:
                month_key = current_date.strftime("%Y-%m")
                month_name = current_date.strftime("%B %Y")
                
                if month_name in month_counts:
                    month_counts[month_name] += 1
                else:
                    month_counts[month_name] = 1
                
                # Zum nächsten Tag
                current_date += timedelta(days=1)
        
        # Diagramm erstellen
        if month_counts:
            # Nach Datum sortieren
            sorted_months = sorted(month_counts.items(), key=lambda x: datetime.strptime(x[0], "%B %Y"))
            months = [m[0] for m in sorted_months]
            counts = [m[1] for m in sorted_months]
            
            fig = px.bar(
                x=months,
                y=counts,
                title="Krankheitstage pro Monat"
            )
            st.plotly_chart(fig)
        
        # Krankmeldungen nach Mitarbeiter
        st.subheader("Krankmeldungen nach Mitarbeiter")
        
        # Mitarbeiter zählen
        employee_counts = {}
        for s in sick_leaves:
            employee = next((emp["name"] for emp in st.session_state["employees"] if emp["id"] == s["employee_id"]), "Unbekannt")
            days = (min(s["end_date"], end_date) - max(s["start_date"], start_date)).days + 1
            
            if employee in employee_counts:
                employee_counts[employee] += days
            else:
                employee_counts[employee] = days
        
        # Diagramm erstellen
        if employee_counts:
            # Nach Anzahl der Tage sortieren
            sorted_employees = sorted(employee_counts.items(), key=lambda x: x[1], reverse=True)
            employees = [e[0] for e in sorted_employees]
            days = [e[1] for e in sorted_employees]
            
            fig = px.bar(
                x=employees,
                y=days,
                title="Krankheitstage pro Mitarbeiter"
            )
            st.plotly_chart(fig)
        
        # Export-Optionen
        st.subheader("Daten exportieren")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Als CSV exportieren"):
                export_sick_leave_data_as_csv(sick_leaves, start_date, end_date)
        with col2:
            if st.button("Als PDF exportieren"):
                export_sick_leave_data_as_pdf(sick_leaves, start_date, end_date)
    
    def export_sick_leave_data_as_csv(sick_leaves, start_date, end_date):
        """
        Exportiert Krankmeldungsdaten als CSV
        """
        # Daten für CSV vorbereiten
        data = []
        for sick_leave in sick_leaves:
            employee = next((emp["name"] for emp in st.session_state["employees"] if emp["id"] == sick_leave["employee_id"]), "Unbekannt")
            days = (min(sick_leave["end_date"], end_date) - max(sick_leave["start_date"], start_date)).days + 1
            
            data.append({
                "Mitarbeiter": employee,
                "Von": sick_leave["start_date"],
                "Bis": sick_leave["end_date"],
                "Tage": days,
                "Kategorie": sick_leave.get("category", "Sonstiges"),
                "Begründung": sick_leave.get("reason", "")
            })
        
        # CSV erstellen
        df = pd.DataFrame(data)
        csv = df.to_csv(index=False)
        
        # Download-Link erstellen
        st.download_button(
            label="CSV herunterladen",
            data=csv,
            file_name=f"krankmeldungen_{start_date}_bis_{end_date}.csv",
            mime="text/csv"
        )
    
    def export_sick_leave_data_as_pdf(sick_leaves, start_date, end_date):
        """
        Exportiert Krankmeldungsdaten als PDF
        """
        # Daten für PDF vorbereiten
        data = []
        for sick_leave in sick_leaves:
            employee = next((emp["name"] for emp in st.session_state["employees"] if emp["id"] == sick_leave["employee_id"]), "Unbekannt")
            days = (min(sick_leave["end_date"], end_date) - max(sick_leave["start_date"], start_date)).days + 1
            
            data.append([
                employee,
                sick_leave["start_date"].strftime("%d.%m.%Y"),
                sick_leave["end_date"].strftime("%d.%m.%Y"),
                str(days),
                sick_leave.get("category", "Sonstiges")
            ])
        
        # PDF erstellen
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        # Titel
        styles = getSampleStyleSheet()
        elements.append(Paragraph(f"Krankmeldungsbericht ({start_date} bis {end_date})", styles["Title"]))
        elements.append(Paragraph(f"Anzahl der Krankmeldungen: {len(sick_leaves)}", styles["Normal"]))
        elements.append(Paragraph(" ", styles["Normal"]))  # Leerzeile
        
        # Tabelle
        table_data = [["Mitarbeiter", "Von", "Bis", "Tage", "Kategorie"]] + data
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
        
        # Zebrastreifen für bessere Lesbarkeit
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                style.add('BACKGROUND', (0, i), (-1, i), colors.white)
        
        table.setStyle(style)
        elements.append(table)
        
        # PDF generieren
        doc.build(elements)
        
        # Download-Link erstellen
        st.download_button(
            label="PDF herunterladen",
            data=buffer.getvalue(),
            file_name=f"krankmeldungen_{start_date}_bis_{end_date}.pdf",
            mime="application/pdf"
        )
    
    return {
        "show_enhanced_sick_leave_page": show_enhanced_sick_leave_page,
        "show_sick_leave_statistics": show_sick_leave_statistics,
        "export_sick_leave_data_as_csv": export_sick_leave_data_as_csv,
        "export_sick_leave_data_as_pdf": export_sick_leave_data_as_pdf
    }

# 2. Automatische Benachrichtigung bei Urlaubsanträgen
def implement_vacation_notifications():
    """
    Implementierung der automatischen Benachrichtigungen für Urlaubsanträge
    """
    def send_vacation_notification(vacation_request):
        """
        Sendet eine Benachrichtigung über einen neuen Urlaubsantrag
        """
        # In einer echten App würde hier eine E-Mail gesendet werden
        # Hier simulieren wir das durch Speichern in session_state
        
        if "notifications" not in st.session_state:
            st.session_state["notifications"] = []
        
        employee = next((emp for emp in st.session_state["employees"] if emp["id"] == vacation_request["employee_id"]), {"name": "Unbekannt"})
        
        notification = {
            "type": "vacation_request",
            "employee_id": vacation_request["employee_id"],
            "employee_name": employee["name"],
            "vacation_id": vacation_request["id"],
            "message": f"Neuer Urlaubsantrag von {employee['name']} vom {vacation_request['start_date']} bis {vacation_request['end_date']}",
            "timestamp": datetime.now(),
            "read": False
        }
        
        st.session_state["notifications"].append(notification)
        
        return notification
    
    def show_notification_center():
        """
        Zeigt das Benachrichtigungszentrum an
        """
        st.title("Benachrichtigungen")
        
        # Prüfen, ob Benachrichtigungen vorhanden sind
        if "notifications" not in st.session_state or not st.session_state["notifications"]:
            st.info("Keine Benachrichtigungen vorhanden.")
            return
        
        # Benachrichtigungen nach Typ filtern
        notification_type = st.radio(
            "Benachrichtigungstyp",
            ["Alle", "Urlaubsanträge", "Krankmeldungen", "Statusänderungen"],
            key="notification_type_filter"
        )
        
        # Benachrichtigungen filtern
        filtered_notifications = st.session_state["notifications"]
        
        if notification_type == "Urlaubsanträge":
            filtered_notifications = [n for n in filtered_notifications if n["type"] == "vacation_request"]
        elif notification_type == "Krankmeldungen":
            filtered_notifications = [n for n in filtered_notifications if n["type"] == "sick_leave"]
        elif notification_type == "Statusänderungen":
            filtered_notifications = [n for n in filtered_notifications if n["type"] in ["vacation_status", "sick_leave_status"]]
        
        # Nach Datum sortieren (neueste zuerst)
        filtered_notifications.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Benachrichtigungen anzeigen
        st.subheader(f"Benachrichtigungen ({len(filtered_notifications)})")
        
        for i, notification in enumerate(filtered_notifications):
            # Hintergrundfarbe basierend auf Lesestatus
            bg_color = "white" if notification["read"] else "lightyellow"
            
            # Icon basierend auf Typ
            icon = "📅" if "vacation" in notification["type"] else "🤒" if "sick" in notification["type"] else "ℹ️"
            
            with st.container():
                st.markdown(
                    f"""
                    <div style="background-color: {bg_color}; padding: 10px; border-radius: 5px; margin-bottom: 10px;">
                        <strong>{icon} {notification["message"]}</strong><br>
                        <small>{notification["timestamp"].strftime("%d.%m.%Y %H:%M")}</small>
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                # Aktionen für ungelesene Benachrichtigungen
                if not notification["read"]:
                    col1, col2 = st.columns([1, 3])
                    with col1:
                        if st.button("Als gelesen markieren", key=f"mark_read_{i}"):
                            notification["read"] = True
                            st.success("Als gelesen markiert.")
                            st.rerun()
                    with col2:
                        if "vacation_request" in notification["type"]:
                            if st.button("Zum Urlaubsantrag", key=f"goto_vacation_{i}"):
                                st.session_state["current_page"] = "vacation"
                                st.session_state["selected_vacation_id"] = notification["vacation_id"]
                                notification["read"] = True
                                st.rerun()
                        elif "sick_leave" in notification["type"] and not "status" in notification["type"]:
                            if st.button("Zur Krankmeldung", key=f"goto_sick_{i}"):
                                st.session_state["current_page"] = "sick_leave"
                                notification["read"] = True
                                st.rerun()
        
        # Alle als gelesen markieren
        if st.button("Alle als gelesen markieren"):
            for notification in st.session_state["notifications"]:
                notification["read"] = True
            st.success("Alle Benachrichtigungen wurden als gelesen markiert.")
            st.rerun()
    
    def show_notification_badge():
        """
        Zeigt ein Benachrichtigungs-Badge in der Sidebar an
        """
        if "notifications" in st.session_state and st.session_state["notifications"]:
            unread_count = sum(1 for n in st.session_state["notifications"] if not n["read"])
            
            if unread_count > 0:
                st.sidebar.markdown(
                    f"""
                    <div style="background-color: red; color: white; border-radius: 50%; width: 24px; height: 24px; 
                    display: flex; align-items: center; justify-content: center; margin-bottom: 10px;">
                        {unread_count}
                    </div>
                    """,
                    unsafe_allow_html=True
                )
                
                if st.sidebar.button("Benachrichtigungen anzeigen"):
                    st.session_state["current_page"] = "notifications"
                    st.rerun()
    
    return {
        "send_vacation_notification": send_vacation_notification,
        "show_notification_center": show_notification_center,
        "show_notification_badge": show_notification_badge
    }

# 3. Urlaubsgenehmigung mit Kommentarfunktion
def implement_vacation_approval():
    """
    Implementierung der Urlaubsgenehmigung mit Kommentarfunktion
    """
    def show_enhanced_vacation_page():
        """
        Zeigt die erweiterte Urlaubsseite mit Genehmigungsfunktion an
        """
        st.title("Urlaubsverwaltung")
        
        # Mitarbeiter auswählen
        if st.session_state.get("is_admin", False):
            employee = st.selectbox("Mitarbeiter auswählen", 
                                   [emp["name"] for emp in st.session_state["employees"]],
                                   key="vacation_employee_select")
            employee_id = next(emp["id"] for emp in st.session_state["employees"] if emp["name"] == employee)
        else:
            employee = st.session_state.get("username")
            employee_id = st.session_state.get("user_id")
            st.write(f"Mitarbeiter: {employee}")
        
        # Bestehende Urlaubsanträge anzeigen
        st.subheader("Bestehende Urlaubsanträge")
        
        vacation_requests = [v for v in st.session_state["vacation_requests"] if v["employee_id"] == employee_id]
        vacation_requests.sort(key=lambda x: x["start_date"], reverse=True)
        
        if vacation_requests:
            for vacation in vacation_requests:
                # Farbgebung basierend auf Status
                status_color = {
                    "Beantragt": "orange",
                    "Genehmigt": "green",
                    "Abgelehnt": "red"
                }.get(vacation.get("status", "Beantragt"), "gray")
                
                with st.expander(f"{vacation['start_date']} bis {vacation['end_date']} - {vacation.get('status', 'Beantragt')}"):
                    st.markdown(f"**Status:** <span style='color:{status_color};'>{vacation.get('status', 'Beantragt')}</span>", unsafe_allow_html=True)
                    st.write(f"**Zeitraum:** {vacation['start_date']} bis {vacation['end_date']}")
                    
                    # Anzahl der Urlaubstage berechnen
                    days = (vacation['end_date'] - vacation['start_date']).days + 1
                    weekdays = sum(1 for i in range(days) if (vacation['start_date'] + timedelta(days=i)).weekday() < 5)
                    st.write(f"**Urlaubstage:** {days} Tage ({weekdays} Arbeitstage)")
                    
                    # Begründung anzeigen
                    if "reason" in vacation and vacation["reason"]:
                        st.write(f"**Begründung:** {vacation['reason']}")
                    
                    # Kommentare anzeigen
                    if "comments" in vacation and vacation["comments"]:
                        st.write("**Kommentare:**")
                        for comment in vacation["comments"]:
                            st.markdown(f"- **{comment['author']}** ({comment['timestamp'].strftime('%d.%m.%Y %H:%M')}): {comment['text']}")
                    
                    # Admin-Aktionen
                    if st.session_state.get("is_admin", False) and vacation.get("status") == "Beantragt":
                        st.write("**Admin-Aktionen:**")
                        
                        # Kommentar hinzufügen
                        comment = st.text_area("Kommentar", key=f"vacation_comment_{vacation.get('id', 0)}")
                        
                        col1, col2 = st.columns(2)
                        with col1:
                            if st.button("Genehmigen", key=f"approve_vacation_{vacation.get('id', 0)}"):
                                vacation["status"] = "Genehmigt"
                                
                                # Kommentar hinzufügen
                                if comment:
                                    if "comments" not in vacation:
                                        vacation["comments"] = []
                                    
                                    vacation["comments"].append({
                                        "author": st.session_state.get("username", "Admin"),
                                        "text": comment,
                                        "timestamp": datetime.now()
                                    })
                                
                                # Mitarbeiterstatus aktualisieren
                                if datetime.now().date() >= vacation["start_date"] and datetime.now().date() <= vacation["end_date"]:
                                    employee_obj = next((emp for emp in st.session_state["employees"] if emp["id"] == employee_id), None)
                                    if employee_obj:
                                        employee_obj["status"] = "Urlaub"
                                
                                # Benachrichtigung senden
                                if "notifications" not in st.session_state:
                                    st.session_state["notifications"] = []
                                
                                st.session_state["notifications"].append({
                                    "type": "vacation_status",
                                    "employee_id": employee_id,
                                    "employee_name": employee,
                                    "message": f"Ihr Urlaubsantrag vom {vacation['start_date']} bis {vacation['end_date']} wurde genehmigt.",
                                    "timestamp": datetime.now(),
                                    "read": False
                                })
                                
                                st.success("Urlaubsantrag wurde genehmigt.")
                                st.rerun()
                        
                        with col2:
                            if st.button("Ablehnen", key=f"reject_vacation_{vacation.get('id', 0)}"):
                                vacation["status"] = "Abgelehnt"
                                
                                # Kommentar hinzufügen
                                if comment:
                                    if "comments" not in vacation:
                                        vacation["comments"] = []
                                    
                                    vacation["comments"].append({
                                        "author": st.session_state.get("username", "Admin"),
                                        "text": comment,
                                        "timestamp": datetime.now()
                                    })
                                
                                # Benachrichtigung senden
                                if "notifications" not in st.session_state:
                                    st.session_state["notifications"] = []
                                
                                st.session_state["notifications"].append({
                                    "type": "vacation_status",
                                    "employee_id": employee_id,
                                    "employee_name": employee,
                                    "message": f"Ihr Urlaubsantrag vom {vacation['start_date']} bis {vacation['end_date']} wurde abgelehnt.",
                                    "timestamp": datetime.now(),
                                    "read": False
                                })
                                
                                st.error("Urlaubsantrag wurde abgelehnt.")
                                st.rerun()
                    
                    # Mitarbeiter-Aktionen
                    elif not st.session_state.get("is_admin", False) and vacation.get("status") == "Beantragt":
                        if st.button("Zurückziehen", key=f"withdraw_vacation_{vacation.get('id', 0)}"):
                            st.session_state["vacation_requests"].remove(vacation)
                            st.success("Urlaubsantrag wurde zurückgezogen.")
                            st.rerun()
                    
                    # Kommentar hinzufügen (für alle)
                    if vacation.get("status") != "Beantragt":
                        comment = st.text_area("Neuer Kommentar", key=f"new_comment_{vacation.get('id', 0)}")
                        
                        if st.button("Kommentar hinzufügen", key=f"add_comment_{vacation.get('id', 0)}"):
                            if "comments" not in vacation:
                                vacation["comments"] = []
                            
                            vacation["comments"].append({
                                "author": st.session_state.get("username", "Unbekannt"),
                                "text": comment,
                                "timestamp": datetime.now()
                            })
                            
                            st.success("Kommentar wurde hinzugefügt.")
                            st.rerun()
        else:
            st.info("Keine Urlaubsanträge vorhanden.")
        
        # Neuen Urlaubsantrag erstellen
        st.subheader("Neuen Urlaubsantrag erstellen")
        
        # Verfügbare Urlaubstage anzeigen (simuliert)
        employee_obj = next((emp for emp in st.session_state["employees"] if emp["id"] == employee_id), None)
        if employee_obj:
            if "vacation_days" not in employee_obj:
                employee_obj["vacation_days"] = {
                    "total": 30,
                    "used": sum(
                        (v["end_date"] - v["start_date"]).days + 1
                        for v in st.session_state["vacation_requests"]
                        if v["employee_id"] == employee_id and v.get("status") == "Genehmigt"
                    ),
                    "planned": sum(
                        (v["end_date"] - v["start_date"]).days + 1
                        for v in st.session_state["vacation_requests"]
                        if v["employee_id"] == employee_id and v.get("status") == "Beantragt"
                    )
                }
            
            vacation_days = employee_obj["vacation_days"]
            remaining = vacation_days["total"] - vacation_days["used"]
            
            col1, col2, col3 = st.columns(3)
            with col1:
                st.metric("Gesamt", vacation_days["total"])
            with col2:
                st.metric("Verwendet", vacation_days["used"])
            with col3:
                st.metric("Verbleibend", remaining)
        
        # Formular für neuen Urlaubsantrag
        with st.form("new_vacation_form"):
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input("Von", value=datetime.now().date() + timedelta(days=14), key="new_vacation_start")
            with col2:
                end_date = st.date_input("Bis", value=datetime.now().date() + timedelta(days=14), key="new_vacation_end")
            
            # Begründung hinzufügen
            reason = st.text_area("Begründung", key="new_vacation_reason", 
                                help="Bitte geben Sie eine kurze Begründung für Ihren Urlaubsantrag an.")
            
            # Urlaubstyp auswählen
            vacation_types = ["Erholungsurlaub", "Sonderurlaub", "Unbezahlter Urlaub", "Bildungsurlaub", "Sonstiges"]
            vacation_type = st.selectbox("Urlaubstyp", vacation_types, key="new_vacation_type")
            
            # Vertretung auswählen
            colleagues = [emp["name"] for emp in st.session_state["employees"] if emp["id"] != employee_id]
            substitute = st.selectbox("Vertretung", ["Keine"] + colleagues, key="new_vacation_substitute")
            
            # Formular absenden
            submit_button = st.form_submit_button("Urlaubsantrag einreichen")
            
            if submit_button:
                # Validierung
                if end_date < start_date:
                    st.error("Das Enddatum kann nicht vor dem Startdatum liegen.")
                else:
                    # Anzahl der Urlaubstage berechnen
                    days = (end_date - start_date).days + 1
                    
                    # Prüfen, ob genügend Urlaubstage verfügbar sind
                    if employee_obj and "vacation_days" in employee_obj:
                        if days > remaining:
                            st.warning(f"Achtung: Sie haben nur noch {remaining} Urlaubstage verfügbar, aber {days} Tage beantragt.")
                    
                    # Neuen Urlaubsantrag erstellen
                    new_vacation = {
                        "id": len(st.session_state["vacation_requests"]) + 1,
                        "employee_id": employee_id,
                        "start_date": start_date,
                        "end_date": end_date,
                        "days": days,
                        "reason": reason,
                        "type": vacation_type,
                        "substitute": substitute if substitute != "Keine" else None,
                        "status": "Beantragt",
                        "created_at": datetime.now()
                    }
                    
                    # Zur Liste hinzufügen
                    st.session_state["vacation_requests"].append(new_vacation)
                    
                    # Geplante Urlaubstage aktualisieren
                    if employee_obj and "vacation_days" in employee_obj:
                        employee_obj["vacation_days"]["planned"] += days
                    
                    st.success("Urlaubsantrag wurde erfolgreich eingereicht.")
                    
                    # Benachrichtigung an Admins senden
                    vacation_notifications = implement_vacation_notifications()
                    notification = vacation_notifications["send_vacation_notification"](new_vacation)
                    
                    st.info("Benachrichtigung an Administratoren wurde gesendet.")
                    st.rerun()
    
    def show_vacation_calendar():
        """
        Zeigt einen Urlaubskalender für alle Mitarbeiter an
        """
        st.title("Urlaubskalender")
        
        # Monat und Jahr auswählen
        col1, col2 = st.columns(2)
        with col1:
            month = st.selectbox(
                "Monat",
                range(1, 13),
                index=datetime.now().month - 1,
                key="vacation_calendar_month"
            )
        with col2:
            year = st.selectbox(
                "Jahr",
                range(2020, 2030),
                index=datetime.now().year - 2020,
                key="vacation_calendar_year"
            )
        
        # Kalenderansicht erstellen
        cal = calendar.monthcalendar(year, month)
        
        # Daten für den ausgewählten Monat abrufen
        month_start = datetime(year, month, 1).date()
        if month == 12:
            month_end = datetime(year + 1, 1, 1).date() - timedelta(days=1)
        else:
            month_end = datetime(year, month + 1, 1).date() - timedelta(days=1)
        
        # Urlaubsanträge für den Monat abrufen
        vacation_requests = [v for v in st.session_state["vacation_requests"] 
                            if v.get("status") == "Genehmigt" and
                            not (v["end_date"] < month_start or v["start_date"] > month_end)]
        
        # Mitarbeiter mit Urlaub im ausgewählten Monat
        employees_on_vacation = {}
        for v in vacation_requests:
            employee = next((emp for emp in st.session_state["employees"] if emp["id"] == v["employee_id"]), {"name": "Unbekannt"})
            
            # Alle Tage des Urlaubs durchgehen
            current_date = max(v["start_date"], month_start)
            end = min(v["end_date"], month_end)
            
            while current_date <= end:
                date_key = current_date.isoformat()
                
                if date_key not in employees_on_vacation:
                    employees_on_vacation[date_key] = []
                
                employees_on_vacation[date_key].append(employee["name"])
                
                # Zum nächsten Tag
                current_date += timedelta(days=1)
        
        # Wochentage-Header
        weekdays = ["Mo", "Di", "Mi", "Do", "Fr", "Sa", "So"]
        cols = st.columns(7)
        for i, col in enumerate(cols):
            with col:
                st.markdown(f"**{weekdays[i]}**", unsafe_allow_html=True)
        
        # Kalender rendern
        for week in cal:
            cols = st.columns(7)
            for i, day in enumerate(week):
                with cols[i]:
                    if day == 0:
                        # Leerer Tag (außerhalb des Monats)
                        st.markdown("&nbsp;", unsafe_allow_html=True)
                    else:
                        # Tag im Monat
                        current_date = datetime(year, month, day).date()
                        date_key = current_date.isoformat()
                        
                        # Mitarbeiter im Urlaub an diesem Tag
                        employees_today = employees_on_vacation.get(date_key, [])
                        
                        # Hintergrundfarbe basierend auf Anzahl der Mitarbeiter im Urlaub
                        bg_color = "white"
                        if employees_today:
                            # Farbintensität basierend auf Anzahl der Mitarbeiter
                            intensity = min(len(employees_today) * 20, 100)
                            bg_color = f"rgba(135, 206, 250, {intensity/100})"  # Hellblau mit variabler Transparenz
                        
                        # Container für den Tag mit Hintergrundfarbe
                        with st.container():
                            st.markdown(
                                f"""
                                <div style="background-color: {bg_color}; padding: 5px; border-radius: 5px; min-height: 80px;">
                                    <strong>{day}</strong>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                            
                            # Mitarbeiter im Urlaub anzeigen
                            if employees_today:
                                for emp in employees_today:
                                    st.write(f"- {emp}")
    
    def show_vacation_statistics():
        """
        Zeigt Statistiken zu Urlaubsanträgen an
        """
        st.title("Urlaubsstatistiken")
        
        # Nur für Admins zugänglich
        if not st.session_state.get("is_admin", False):
            st.error("Sie haben keine Berechtigung für diese Seite.")
            return
        
        # Zeitraum auswählen
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Von", 
                value=datetime(datetime.now().year, 1, 1).date(),
                key="vacation_stats_start_date"
            )
        with col2:
            end_date = st.date_input(
                "Bis", 
                value=datetime(datetime.now().year, 12, 31).date(),
                key="vacation_stats_end_date"
            )
        
        # Urlaubsanträge für den Zeitraum abrufen
        vacation_requests = [v for v in st.session_state["vacation_requests"] 
                            if not (v["end_date"] < start_date or v["start_date"] > end_date)]
        
        if not vacation_requests:
            st.info("Keine Urlaubsanträge im ausgewählten Zeitraum gefunden.")
            return
        
        # Gesamtstatistik
        st.subheader("Gesamtstatistik")
        
        # Nach Status gruppieren
        status_counts = {
            "Beantragt": len([v for v in vacation_requests if v.get("status") == "Beantragt"]),
            "Genehmigt": len([v for v in vacation_requests if v.get("status") == "Genehmigt"]),
            "Abgelehnt": len([v for v in vacation_requests if v.get("status") == "Abgelehnt"])
        }
        
        col1, col2, col3 = st.columns(3)
        with col1:
            st.metric("Beantragt", status_counts["Beantragt"])
        with col2:
            st.metric("Genehmigt", status_counts["Genehmigt"])
        with col3:
            st.metric("Abgelehnt", status_counts["Abgelehnt"])
        
        # Urlaubstage pro Mitarbeiter
        st.subheader("Urlaubstage pro Mitarbeiter")
        
        # Urlaubstage pro Mitarbeiter berechnen
        employee_days = {}
        for v in vacation_requests:
            if v.get("status") != "Genehmigt":
                continue
                
            employee = next((emp for emp in st.session_state["employees"] if emp["id"] == v["employee_id"]), {"name": "Unbekannt"})
            days = (min(v["end_date"], end_date) - max(v["start_date"], start_date)).days + 1
            
            if employee["name"] in employee_days:
                employee_days[employee["name"]] += days
            else:
                employee_days[employee["name"]] = days
        
        # Diagramm erstellen
        if employee_days:
            # Nach Anzahl der Tage sortieren
            sorted_employees = sorted(employee_days.items(), key=lambda x: x[1], reverse=True)
            employees = [e[0] for e in sorted_employees]
            days = [e[1] for e in sorted_employees]
            
            fig = px.bar(
                x=employees,
                y=days,
                title="Urlaubstage pro Mitarbeiter"
            )
            st.plotly_chart(fig)
        
        # Urlaubsanträge nach Monat
        st.subheader("Urlaubsanträge nach Monat")
        
        # Monate zählen
        month_counts = {}
        for v in vacation_requests:
            if v.get("status") != "Genehmigt":
                continue
                
            # Alle Tage des Urlaubs durchgehen
            current_date = max(v["start_date"], start_date)
            end = min(v["end_date"], end_date)
            
            while current_date <= end:
                month_key = current_date.strftime("%Y-%m")
                month_name = current_date.strftime("%B %Y")
                
                if month_name in month_counts:
                    month_counts[month_name] += 1
                else:
                    month_counts[month_name] = 1
                
                # Zum nächsten Tag
                current_date += timedelta(days=1)
        
        # Diagramm erstellen
        if month_counts:
            # Nach Datum sortieren
            sorted_months = sorted(month_counts.items(), key=lambda x: datetime.strptime(x[0], "%B %Y"))
            months = [m[0] for m in sorted_months]
            counts = [m[1] for m in sorted_months]
            
            fig = px.bar(
                x=months,
                y=counts,
                title="Urlaubstage pro Monat"
            )
            st.plotly_chart(fig)
        
        # Urlaubsanträge nach Typ
        st.subheader("Urlaubsanträge nach Typ")
        
        # Typen zählen
        type_counts = {}
        for v in vacation_requests:
            if v.get("status") != "Genehmigt":
                continue
                
            vacation_type = v.get("type", "Erholungsurlaub")
            days = (min(v["end_date"], end_date) - max(v["start_date"], start_date)).days + 1
            
            if vacation_type in type_counts:
                type_counts[vacation_type] += days
            else:
                type_counts[vacation_type] = days
        
        # Diagramm erstellen
        if type_counts:
            fig = px.pie(
                names=list(type_counts.keys()),
                values=list(type_counts.values()),
                title="Verteilung nach Urlaubstyp"
            )
            st.plotly_chart(fig)
        
        # Export-Optionen
        st.subheader("Daten exportieren")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Als CSV exportieren"):
                export_vacation_data_as_csv(vacation_requests, start_date, end_date)
        with col2:
            if st.button("Als PDF exportieren"):
                export_vacation_data_as_pdf(vacation_requests, start_date, end_date)
    
    def export_vacation_data_as_csv(vacation_requests, start_date, end_date):
        """
        Exportiert Urlaubsdaten als CSV
        """
        # Daten für CSV vorbereiten
        data = []
        for vacation in vacation_requests:
            employee = next((emp["name"] for emp in st.session_state["employees"] if emp["id"] == vacation["employee_id"]), "Unbekannt")
            days = (min(vacation["end_date"], end_date) - max(vacation["start_date"], start_date)).days + 1
            
            data.append({
                "Mitarbeiter": employee,
                "Von": vacation["start_date"],
                "Bis": vacation["end_date"],
                "Tage": days,
                "Typ": vacation.get("type", "Erholungsurlaub"),
                "Status": vacation.get("status", "Beantragt"),
                "Begründung": vacation.get("reason", "")
            })
        
        # CSV erstellen
        df = pd.DataFrame(data)
        csv = df.to_csv(index=False)
        
        # Download-Link erstellen
        st.download_button(
            label="CSV herunterladen",
            data=csv,
            file_name=f"urlaub_{start_date}_bis_{end_date}.csv",
            mime="text/csv"
        )
    
    def export_vacation_data_as_pdf(vacation_requests, start_date, end_date):
        """
        Exportiert Urlaubsdaten als PDF
        """
        # Daten für PDF vorbereiten
        data = []
        for vacation in vacation_requests:
            employee = next((emp["name"] for emp in st.session_state["employees"] if emp["id"] == vacation["employee_id"]), "Unbekannt")
            days = (min(vacation["end_date"], end_date) - max(vacation["start_date"], start_date)).days + 1
            
            data.append([
                employee,
                vacation["start_date"].strftime("%d.%m.%Y"),
                vacation["end_date"].strftime("%d.%m.%Y"),
                str(days),
                vacation.get("type", "Erholungsurlaub"),
                vacation.get("status", "Beantragt")
            ])
        
        # PDF erstellen
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        # Titel
        styles = getSampleStyleSheet()
        elements.append(Paragraph(f"Urlaubsbericht ({start_date} bis {end_date})", styles["Title"]))
        elements.append(Paragraph(f"Anzahl der Urlaubsanträge: {len(vacation_requests)}", styles["Normal"]))
        elements.append(Paragraph(" ", styles["Normal"]))  # Leerzeile
        
        # Tabelle
        table_data = [["Mitarbeiter", "Von", "Bis", "Tage", "Typ", "Status"]] + data
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
        
        # Zebrastreifen für bessere Lesbarkeit
        for i in range(1, len(table_data)):
            if i % 2 == 0:
                style.add('BACKGROUND', (0, i), (-1, i), colors.white)
        
        table.setStyle(style)
        elements.append(table)
        
        # PDF generieren
        doc.build(elements)
        
        # Download-Link erstellen
        st.download_button(
            label="PDF herunterladen",
            data=buffer.getvalue(),
            file_name=f"urlaub_{start_date}_bis_{end_date}.pdf",
            mime="application/pdf"
        )
    
    return {
        "show_enhanced_vacation_page": show_enhanced_vacation_page,
        "show_vacation_calendar": show_vacation_calendar,
        "show_vacation_statistics": show_vacation_statistics,
        "export_vacation_data_as_csv": export_vacation_data_as_csv,
        "export_vacation_data_as_pdf": export_vacation_data_as_pdf
    }

# Hauptfunktion zur Integration aller Krankmeldungs- und Urlaubsoptimierungen
def integrate_sick_leave_vacation_optimizations(app):
    """
    Integriert alle Krankmeldungs- und Urlaubsoptimierungen in die App
    """
    # Begründungsmöglichkeit für Krankmeldungen implementieren
    sick_leave_reasons = implement_sick_leave_reasons()
    
    # Automatische Benachrichtigung bei Urlaubsanträgen implementieren
    vacation_notifications = implement_vacation_notifications()
    
    # Urlaubsgenehmigung mit Kommentarfunktion implementieren
    vacation_approval = implement_vacation_approval()
    
    # Funktionen in die App integrieren
    # (Hier würde die tatsächliche Integration in die App erfolgen)
    
    # Beispiel für die Integration in die Hauptapp
    def extended_main():
        # Benachrichtigungs-Badge in der Sidebar anzeigen
        vacation_notifications["show_notification_badge"]()
        
        # Seitenauswahl erweitern
        if page == "Krankmeldungen":
            sick_leave_reasons["show_enhanced_sick_leave_page"]()
        elif page == "Urlaub":
            vacation_approval["show_enhanced_vacation_page"]()
        elif page == "Urlaubskalender":
            vacation_approval["show_vacation_calendar"]()
        elif page == "Benachrichtigungen":
            vacation_notifications["show_notification_center"]()
        
        # Admin-Seiten
        if st.session_state.get("is_admin", False):
            if page == "Krankmeldungsstatistiken":
                sick_leave_reasons["show_sick_leave_statistics"]()
            elif page == "Urlaubsstatistiken":
                vacation_approval["show_vacation_statistics"]()
    
    # Rückgabe der erweiterten App-Funktionalität
    return {
        "extended_main": extended_main,
        "sick_leave_reasons": sick_leave_reasons,
        "vacation_notifications": vacation_notifications,
        "vacation_approval": vacation_approval
    }
