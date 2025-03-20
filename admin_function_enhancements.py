# Implementierung der Admin-Funktionserweiterungen

# 1. Suchfunktion für Mitarbeiter
def implement_employee_search():
    """
    Implementierung einer erweiterten Suchfunktion für Mitarbeiter
    """
    def show_employee_search():
        """
        Zeigt die Suchfunktion für Mitarbeiter an
        """
        st.subheader("Mitarbeitersuche")
        
        # Suchfeld
        search_query = st.text_input(
            "Suche nach Name, E-Mail oder Rolle",
            key="employee_search_query"
        )
        
        # Erweiterte Filteroptionen
        with st.expander("Erweiterte Filter"):
            # Status-Filter
            status_filter = st.multiselect(
                "Status",
                ["Alle", "Anwesend", "Abwesend", "Krank", "Urlaub"],
                default=["Alle"],
                key="employee_status_filter"
            )
            
            # Rollen-Filter
            roles = list(set(emp.get("role", "Mitarbeiter") for emp in st.session_state["employees"]))
            role_filter = st.multiselect(
                "Rolle",
                ["Alle"] + roles,
                default=["Alle"],
                key="employee_role_filter"
            )
            
            # Arbeitszeitmodell-Filter (falls implementiert)
            if any("work_time_model" in emp for emp in st.session_state["employees"]):
                models = list(set(emp.get("work_time_model", "vollzeit") for emp in st.session_state["employees"]))
                model_filter = st.multiselect(
                    "Arbeitszeitmodell",
                    ["Alle"] + models,
                    default=["Alle"],
                    key="employee_model_filter"
                )
            else:
                model_filter = ["Alle"]
        
        # Sortierung
        sort_options = {
            "Name (A-Z)": lambda x: x.get("name", ""),
            "Name (Z-A)": lambda x: x.get("name", ""),
            "Status": lambda x: x.get("status", ""),
            "Rolle": lambda x: x.get("role", "")
        }
        
        sort_by = st.selectbox(
            "Sortieren nach",
            list(sort_options.keys()),
            key="employee_sort_by"
        )
        
        # Mitarbeiter filtern
        filtered_employees = st.session_state["employees"]
        
        # Textsuche
        if search_query:
            filtered_employees = [
                emp for emp in filtered_employees
                if search_query.lower() in emp.get("name", "").lower() or
                   search_query.lower() in emp.get("email", "").lower() or
                   search_query.lower() in emp.get("role", "").lower()
            ]
        
        # Status-Filter
        if "Alle" not in status_filter:
            filtered_employees = [
                emp for emp in filtered_employees
                if emp.get("status", "") in status_filter
            ]
        
        # Rollen-Filter
        if "Alle" not in role_filter:
            filtered_employees = [
                emp for emp in filtered_employees
                if emp.get("role", "Mitarbeiter") in role_filter
            ]
        
        # Arbeitszeitmodell-Filter
        if "Alle" not in model_filter and any("work_time_model" in emp for emp in st.session_state["employees"]):
            filtered_employees = [
                emp for emp in filtered_employees
                if emp.get("work_time_model", "vollzeit") in model_filter
            ]
        
        # Sortierung anwenden
        sort_func = sort_options[sort_by]
        reverse_sort = sort_by == "Name (Z-A)"
        filtered_employees.sort(key=sort_func, reverse=reverse_sort)
        
        # Ergebnisse anzeigen
        st.subheader(f"Ergebnisse ({len(filtered_employees)} Mitarbeiter)")
        
        if not filtered_employees:
            st.info("Keine Mitarbeiter gefunden, die den Suchkriterien entsprechen.")
            return
        
        # Mitarbeiterliste anzeigen
        for emp in filtered_employees:
            with st.expander(f"{emp.get('name', 'Unbekannt')} - {emp.get('role', 'Mitarbeiter')}"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**ID:** {emp.get('id', 'N/A')}")
                    st.write(f"**Name:** {emp.get('name', 'N/A')}")
                    st.write(f"**E-Mail:** {emp.get('email', 'N/A')}")
                
                with col2:
                    st.write(f"**Rolle:** {emp.get('role', 'Mitarbeiter')}")
                    st.write(f"**Status:** {emp.get('status', 'N/A')}")
                    if "work_time_model" in emp:
                        st.write(f"**Arbeitszeitmodell:** {emp.get('work_time_model', 'vollzeit')}")
                
                # Admin-Aktionen
                if st.session_state.get("is_admin", False):
                    if st.button("Bearbeiten", key=f"edit_emp_{emp.get('id', 0)}"):
                        st.session_state["edit_employee"] = emp
                        st.session_state["current_page"] = "edit_employee"
                        st.rerun()
                    
                    if st.button("Löschen", key=f"delete_emp_{emp.get('id', 0)}"):
                        if st.session_state.get("username") != emp.get("name"):  # Verhindere Selbstlöschung
                            st.session_state["employees"].remove(emp)
                            st.success(f"Mitarbeiter {emp.get('name')} wurde gelöscht.")
                            st.rerun()
                        else:
                            st.error("Sie können Ihren eigenen Account nicht löschen.")
        
        # Speichern von häufig verwendeten Filtern
        if st.button("Aktuelle Filter speichern"):
            if "saved_filters" not in st.session_state:
                st.session_state["saved_filters"] = []
            
            filter_name = st.text_input("Name für diesen Filter", key="save_filter_name")
            
            if filter_name:
                st.session_state["saved_filters"].append({
                    "name": filter_name,
                    "search_query": search_query,
                    "status_filter": status_filter,
                    "role_filter": role_filter,
                    "model_filter": model_filter,
                    "sort_by": sort_by
                })
                st.success(f"Filter '{filter_name}' wurde gespeichert.")
        
        # Gespeicherte Filter anzeigen
        if "saved_filters" in st.session_state and st.session_state["saved_filters"]:
            st.subheader("Gespeicherte Filter")
            
            for i, saved_filter in enumerate(st.session_state["saved_filters"]):
                if st.button(saved_filter["name"], key=f"load_filter_{i}"):
                    # Filter laden
                    st.session_state["employee_search_query"] = saved_filter["search_query"]
                    st.session_state["employee_status_filter"] = saved_filter["status_filter"]
                    st.session_state["employee_role_filter"] = saved_filter["role_filter"]
                    st.session_state["employee_model_filter"] = saved_filter["model_filter"]
                    st.session_state["employee_sort_by"] = saved_filter["sort_by"]
                    st.rerun()
    
    return {
        "show_employee_search": show_employee_search
    }

# 2. Filteroptionen für Arbeitszeiten
def implement_worktime_filters():
    """
    Implementierung erweiterter Filteroptionen für Arbeitszeiten
    """
    def show_worktime_filters():
        """
        Zeigt erweiterte Filteroptionen für Arbeitszeiten an
        """
        st.subheader("Arbeitszeiten filtern")
        
        # Zeitraum-Filter
        filter_type = st.radio(
            "Zeitraum",
            ["Tag", "Woche", "Monat", "Benutzerdefiniert"],
            key="worktime_filter_type"
        )
        
        if filter_type == "Tag":
            selected_date = st.date_input(
                "Datum",
                value=datetime.now().date(),
                key="worktime_day_filter"
            )
            start_date = selected_date
            end_date = selected_date
        elif filter_type == "Woche":
            selected_date = st.date_input(
                "Woche beginnend mit",
                value=datetime.now().date() - timedelta(days=datetime.now().weekday()),
                key="worktime_week_filter"
            )
            start_date = selected_date
            end_date = selected_date + timedelta(days=6)
        elif filter_type == "Monat":
            month = st.selectbox(
                "Monat",
                range(1, 13),
                index=datetime.now().month - 1,
                key="worktime_month_filter"
            )
            year = st.selectbox(
                "Jahr",
                range(2020, 2030),
                index=datetime.now().year - 2020,
                key="worktime_year_filter"
            )
            
            # Erster und letzter Tag des Monats
            first_day = datetime(year, month, 1).date()
            if month == 12:
                last_day = datetime(year + 1, 1, 1).date() - timedelta(days=1)
            else:
                last_day = datetime(year, month + 1, 1).date() - timedelta(days=1)
            
            start_date = first_day
            end_date = last_day
        else:  # Benutzerdefiniert
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input(
                    "Von",
                    value=datetime.now().date() - timedelta(days=30),
                    key="worktime_custom_start"
                )
            with col2:
                end_date = st.date_input(
                    "Bis",
                    value=datetime.now().date(),
                    key="worktime_custom_end"
                )
        
        # Mitarbeiter-Filter
        if st.session_state.get("is_admin", False):
            employee_filter = st.multiselect(
                "Mitarbeiter",
                ["Alle"] + [emp["name"] for emp in st.session_state["employees"]],
                default=["Alle"],
                key="worktime_employee_filter"
            )
        else:
            employee_filter = [st.session_state.get("username")]
        
        # Status-Filter
        status_filter = st.multiselect(
            "Status",
            ["Alle", "Offen", "In Bearbeitung", "Abgeschlossen", "Storniert"],
            default=["Alle"],
            key="worktime_status_filter"
        )
        
        # Arbeitszeitmodell-Filter (falls implementiert)
        if any("work_time_model" in emp for emp in st.session_state["employees"]):
            models = list(set(emp.get("work_time_model", "vollzeit") for emp in st.session_state["employees"]))
            model_filter = st.multiselect(
                "Arbeitszeitmodell",
                ["Alle"] + models,
                default=["Alle"],
                key="worktime_model_filter"
            )
        else:
            model_filter = ["Alle"]
        
        # Sortierung
        sort_options = {
            "Datum (neueste zuerst)": lambda x: x.get("date", datetime.now().date()),
            "Datum (älteste zuerst)": lambda x: x.get("date", datetime.now().date()),
            "Mitarbeiter": lambda x: next((emp["name"] for emp in st.session_state["employees"] if emp["id"] == x.get("employee_id")), ""),
            "Arbeitsstunden": lambda x: (x.get("check_out_time", datetime.now()) - x.get("check_in_time", datetime.now())).total_seconds() / 3600 - x.get("break_duration", 0)
        }
        
        sort_by = st.selectbox(
            "Sortieren nach",
            list(sort_options.keys()),
            key="worktime_sort_by"
        )
        
        # Filter anwenden
        if st.button("Filter anwenden", key="apply_worktime_filters"):
            # Arbeitszeiten filtern
            filtered_checkins = st.session_state["checkins"]
            
            # Zeitraum-Filter
            filtered_checkins = [
                c for c in filtered_checkins
                if start_date <= c.get("date", datetime.now().date()) <= end_date
            ]
            
            # Mitarbeiter-Filter
            if "Alle" not in employee_filter and st.session_state.get("is_admin", False):
                employee_ids = [
                    emp["id"] for emp in st.session_state["employees"]
                    if emp["name"] in employee_filter
                ]
                filtered_checkins = [
                    c for c in filtered_checkins
                    if c.get("employee_id") in employee_ids
                ]
            
            # Status-Filter
            if "Alle" not in status_filter:
                filtered_checkins = [
                    c for c in filtered_checkins
                    if c.get("status", "Offen") in status_filter
                ]
            
            # Arbeitszeitmodell-Filter
            if "Alle" not in model_filter and any("work_time_model" in emp for emp in st.session_state["employees"]):
                # Mitarbeiter nach Arbeitszeitmodell filtern
                model_employee_ids = [
                    emp["id"] for emp in st.session_state["employees"]
                    if emp.get("work_time_model", "vollzeit") in model_filter
                ]
                filtered_checkins = [
                    c for c in filtered_checkins
                    if c.get("employee_id") in model_employee_ids
                ]
            
            # Sortierung anwenden
            sort_func = sort_options[sort_by]
            reverse_sort = sort_by != "Datum (älteste zuerst)"
            filtered_checkins.sort(key=sort_func, reverse=reverse_sort)
            
            # Ergebnisse in Session-State speichern
            st.session_state["filtered_checkins"] = filtered_checkins
            st.success(f"{len(filtered_checkins)} Einträge gefunden.")
        
        # Ergebnisse anzeigen
        if "filtered_checkins" in st.session_state:
            show_filtered_worktimes(st.session_state["filtered_checkins"])
    
    def show_filtered_worktimes(checkins):
        """
        Zeigt die gefilterten Arbeitszeiten an
        """
        st.subheader(f"Gefilterte Arbeitszeiten ({len(checkins)} Einträge)")
        
        if not checkins:
            st.info("Keine Einträge gefunden, die den Filterkriterien entsprechen.")
            return
        
        # Export-Optionen
        col1, col2, col3 = st.columns(3)
        with col1:
            if st.button("Als CSV exportieren"):
                export_filtered_worktimes_as_csv(checkins)
        with col2:
            if st.button("Als PDF exportieren"):
                export_filtered_worktimes_as_pdf(checkins)
        with col3:
            if st.button("Als Excel exportieren"):
                export_filtered_worktimes_as_excel(checkins)
        
        # Arbeitszeiten anzeigen
        for checkin in checkins:
            employee = next((emp for emp in st.session_state["employees"] if emp["id"] == checkin.get("employee_id")), {"name": "Unbekannt"})
            
            with st.expander(f"{checkin.get('date')} - {employee['name']} ({checkin.get('status', 'Offen')})"):
                col1, col2 = st.columns(2)
                
                with col1:
                    st.write(f"**Mitarbeiter:** {employee['name']}")
                    st.write(f"**Datum:** {checkin.get('date')}")
                    
                    check_in_time = checkin.get("check_in_time")
                    if check_in_time:
                        st.write(f"**Check-in:** {check_in_time.strftime('%H:%M')}")
                    else:
                        st.write("**Check-in:** Nicht erfolgt")
                
                with col2:
                    st.write(f"**Status:** {checkin.get('status', 'Offen')}")
                    
                    check_out_time = checkin.get("check_out_time")
                    if check_out_time:
                        st.write(f"**Check-out:** {check_out_time.strftime('%H:%M')}")
                    else:
                        st.write("**Check-out:** Nicht erfolgt")
                    
                    # Arbeitszeit berechnen
                    if check_in_time and check_out_time:
                        work_duration = (check_out_time - check_in_time).total_seconds() / 3600
                        break_duration = checkin.get("break_duration", 0)
                        net_duration = work_duration - break_duration
                        st.write(f"**Arbeitszeit:** {net_duration:.2f} Stunden (inkl. {break_duration:.2f} Std. Pause)")
                
                # Kommentar anzeigen
                if "comment" in checkin and checkin["comment"]:
                    st.write(f"**Kommentar:** {checkin['comment']}")
                
                # Admin-Aktionen
                if st.session_state.get("is_admin", False):
                    if st.button("Bearbeiten", key=f"edit_checkin_{checkin.get('id', 0)}"):
                        st.session_state["edit_checkin"] = checkin
                        st.session_state["current_page"] = "edit_checkin"
                        st.rerun()
    
    def export_filtered_worktimes_as_csv(checkins):
        """
        Exportiert die gefilterten Arbeitszeiten als CSV
        """
        # Daten für CSV vorbereiten
        data = []
        for checkin in checkins:
            employee = next((emp for emp in st.session_state["employees"] if emp["id"] == checkin.get("employee_id")), {"name": "Unbekannt"})
            
            check_in_time = checkin.get("check_in_time")
            check_out_time = checkin.get("check_out_time")
            
            # Arbeitszeit berechnen
            work_duration = 0
            if check_in_time and check_out_time:
                work_duration = (check_out_time - check_in_time).total_seconds() / 3600 - checkin.get("break_duration", 0)
            
            data.append({
                "Datum": checkin.get("date"),
                "Mitarbeiter": employee["name"],
                "Check-in": check_in_time.strftime("%H:%M") if check_in_time else "N/A",
                "Check-out": check_out_time.strftime("%H:%M") if check_out_time else "N/A",
                "Pause (Std.)": checkin.get("break_duration", 0),
                "Arbeitszeit (Std.)": round(work_duration, 2),
                "Status": checkin.get("status", "Offen"),
                "Kommentar": checkin.get("comment", "")
            })
        
        # CSV erstellen
        df = pd.DataFrame(data)
        csv = df.to_csv(index=False)
        
        # Download-Link erstellen
        st.download_button(
            label="CSV herunterladen",
            data=csv,
            file_name=f"arbeitszeiten_{datetime.now().strftime('%Y-%m-%d')}.csv",
            mime="text/csv"
        )
    
    def export_filtered_worktimes_as_pdf(checkins):
        """
        Exportiert die gefilterten Arbeitszeiten als PDF
        """
        # Daten für PDF vorbereiten
        data = []
        for checkin in checkins:
            employee = next((emp for emp in st.session_state["employees"] if emp["id"] == checkin.get("employee_id")), {"name": "Unbekannt"})
            
            check_in_time = checkin.get("check_in_time")
            check_out_time = checkin.get("check_out_time")
            
            # Arbeitszeit berechnen
            work_duration = 0
            if check_in_time and check_out_time:
                work_duration = (check_out_time - check_in_time).total_seconds() / 3600 - checkin.get("break_duration", 0)
            
            data.append([
                checkin.get("date").strftime("%d.%m.%Y"),
                employee["name"],
                check_in_time.strftime("%H:%M") if check_in_time else "N/A",
                check_out_time.strftime("%H:%M") if check_out_time else "N/A",
                f"{checkin.get('break_duration', 0):.2f}",
                f"{round(work_duration, 2):.2f}",
                checkin.get("status", "Offen")
            ])
        
        # PDF erstellen
        buffer = io.BytesIO()
        doc = SimpleDocTemplate(buffer, pagesize=letter)
        elements = []
        
        # Titel
        styles = getSampleStyleSheet()
        elements.append(Paragraph(f"Arbeitszeiten-Bericht ({datetime.now().strftime('%d.%m.%Y')})", styles["Title"]))
        elements.append(Paragraph(f"Anzahl der Einträge: {len(checkins)}", styles["Normal"]))
        elements.append(Paragraph(" ", styles["Normal"]))  # Leerzeile
        
        # Tabelle
        table_data = [["Datum", "Mitarbeiter", "Check-in", "Check-out", "Pause (Std.)", "Arbeitszeit (Std.)", "Status"]] + data
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
            file_name=f"arbeitszeiten_{datetime.now().strftime('%Y-%m-%d')}.pdf",
            mime="application/pdf"
        )
    
    def export_filtered_worktimes_as_excel(checkins):
        """
        Exportiert die gefilterten Arbeitszeiten als Excel
        """
        # Daten für Excel vorbereiten
        data = []
        for checkin in checkins:
            employee = next((emp for emp in st.session_state["employees"] if emp["id"] == checkin.get("employee_id")), {"name": "Unbekannt"})
            
            check_in_time = checkin.get("check_in_time")
            check_out_time = checkin.get("check_out_time")
            
            # Arbeitszeit berechnen
            work_duration = 0
            if check_in_time and check_out_time:
                work_duration = (check_out_time - check_in_time).total_seconds() / 3600 - checkin.get("break_duration", 0)
            
            data.append({
                "Datum": checkin.get("date"),
                "Mitarbeiter": employee["name"],
                "Check-in": check_in_time.strftime("%H:%M") if check_in_time else "N/A",
                "Check-out": check_out_time.strftime("%H:%M") if check_out_time else "N/A",
                "Pause (Std.)": checkin.get("break_duration", 0),
                "Arbeitszeit (Std.)": round(work_duration, 2),
                "Status": checkin.get("status", "Offen"),
                "Kommentar": checkin.get("comment", "")
            })
        
        # Excel erstellen
        df = pd.DataFrame(data)
        
        # Excel-Datei in Puffer schreiben
        buffer = io.BytesIO()
        with pd.ExcelWriter(buffer, engine='xlsxwriter') as writer:
            df.to_excel(writer, sheet_name='Arbeitszeiten', index=False)
            
            # Formatierung
            workbook = writer.book
            worksheet = writer.sheets['Arbeitszeiten']
            
            # Spaltenbreiten anpassen
            for i, col in enumerate(df.columns):
                column_width = max(df[col].astype(str).map(len).max(), len(col)) + 2
                worksheet.set_column(i, i, column_width)
            
            # Überschriften-Format
            header_format = workbook.add_format({
                'bold': True,
                'text_wrap': True,
                'valign': 'top',
                'fg_color': '#D7E4BC',
                'border': 1
            })
            
            # Überschriften formatieren
            for col_num, value in enumerate(df.columns.values):
                worksheet.write(0, col_num, value, header_format)
        
        # Download-Link erstellen
        st.download_button(
            label="Excel herunterladen",
            data=buffer.getvalue(),
            file_name=f"arbeitszeiten_{datetime.now().strftime('%Y-%m-%d')}.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet"
        )
    
    return {
        "show_worktime_filters": show_worktime_filters,
        "show_filtered_worktimes": show_filtered_worktimes,
        "export_filtered_worktimes_as_csv": export_filtered_worktimes_as_csv,
        "export_filtered_worktimes_as_pdf": export_filtered_worktimes_as_pdf,
        "export_filtered_worktimes_as_excel": export_filtered_worktimes_as_excel
    }

# 3. Direkte Bearbeitung von Einträgen in der Kalenderansicht
def implement_calendar_editing():
    """
    Implementierung der direkten Bearbeitung von Einträgen in der Kalenderansicht
    """
    def show_interactive_calendar():
        """
        Zeigt einen interaktiven Kalender mit Bearbeitungsmöglichkeiten an
        """
        st.title("Kalender")
        
        # Monat und Jahr auswählen
        col1, col2 = st.columns(2)
        with col1:
            month = st.selectbox(
                "Monat",
                range(1, 13),
                index=datetime.now().month - 1,
                key="calendar_month"
            )
        with col2:
            year = st.selectbox(
                "Jahr",
                range(2020, 2030),
                index=datetime.now().year - 2020,
                key="calendar_year"
            )
        
        # Mitarbeiter auswählen (nur für Admins)
        if st.session_state.get("is_admin", False):
            employee = st.selectbox(
                "Mitarbeiter",
                [emp["name"] for emp in st.session_state["employees"]],
                key="calendar_employee"
            )
            employee_id = next(emp["id"] for emp in st.session_state["employees"] if emp["name"] == employee)
        else:
            employee = st.session_state.get("username")
            employee_id = st.session_state.get("user_id")
        
        # Kalenderansicht erstellen
        cal = calendar.monthcalendar(year, month)
        
        # Daten für den ausgewählten Monat abrufen
        month_start = datetime(year, month, 1).date()
        if month == 12:
            month_end = datetime(year + 1, 1, 1).date() - timedelta(days=1)
        else:
            month_end = datetime(year, month + 1, 1).date() - timedelta(days=1)
        
        # Arbeitszeiten für den Monat abrufen
        checkins = [c for c in st.session_state["checkins"] 
                   if c["employee_id"] == employee_id 
                   and month_start <= c["date"] <= month_end]
        
        # Krankmeldungen für den Monat abrufen
        sick_leaves = [s for s in st.session_state["sick_leaves"] 
                      if s["employee_id"] == employee_id 
                      and (
                          (s["start_date"] <= month_end and s["end_date"] >= month_start)  # Überschneidung mit dem Monat
                      )]
        
        # Urlaubsanträge für den Monat abrufen
        vacation_requests = [v for v in st.session_state["vacation_requests"] 
                            if v["employee_id"] == employee_id 
                            and (
                                (v["start_date"] <= month_end and v["end_date"] >= month_start)  # Überschneidung mit dem Monat
                            )]
        
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
                        
                        # Hintergrundfarbe basierend auf Einträgen
                        bg_color = "white"
                        if any(s["start_date"] <= current_date <= s["end_date"] for s in sick_leaves):
                            bg_color = "lightpink"  # Krank
                        elif any(v["start_date"] <= current_date <= v["end_date"] and v["status"] == "Genehmigt" for v in vacation_requests):
                            bg_color = "lightblue"  # Urlaub
                        elif any(c["date"] == current_date for c in checkins):
                            bg_color = "lightgreen"  # Arbeitszeit
                        
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
                            
                            # Einträge für diesen Tag
                            day_checkins = [c for c in checkins if c["date"] == current_date]
                            day_sick_leaves = [s for s in sick_leaves if s["start_date"] <= current_date <= s["end_date"]]
                            day_vacations = [v for v in vacation_requests if v["start_date"] <= current_date <= v["end_date"]]
                            
                            # Dropdown für Aktionen
                            if day_checkins or day_sick_leaves or day_vacations or st.session_state.get("is_admin", False):
                                action = st.selectbox(
                                    "Aktion",
                                    ["Auswählen...", "Arbeitszeit bearbeiten", "Krankmeldung bearbeiten", "Urlaub bearbeiten", "Neuer Eintrag"],
                                    key=f"action_{month}_{day}"
                                )
                                
                                if action == "Arbeitszeit bearbeiten" and day_checkins:
                                    edit_checkin_in_calendar(day_checkins[0])
                                elif action == "Krankmeldung bearbeiten" and day_sick_leaves:
                                    edit_sick_leave_in_calendar(day_sick_leaves[0])
                                elif action == "Urlaub bearbeiten" and day_vacations:
                                    edit_vacation_in_calendar(day_vacations[0])
                                elif action == "Neuer Eintrag":
                                    create_new_entry_in_calendar(current_date, employee_id)
    
    def edit_checkin_in_calendar(checkin):
        """
        Bearbeitet einen Arbeitszeit-Eintrag direkt im Kalender
        """
        st.subheader("Arbeitszeit bearbeiten")
        
        # Check-in und Check-out Zeiten
        col1, col2 = st.columns(2)
        with col1:
            check_in_time = checkin.get("check_in_time")
            if check_in_time:
                check_in = st.time_input(
                    "Check-in Zeit",
                    value=check_in_time.time() if isinstance(check_in_time, datetime) else datetime.strptime("08:00", "%H:%M").time(),
                    key=f"cal_edit_checkin_time_{checkin.get('id', 0)}"
                )
            else:
                check_in = st.time_input(
                    "Check-in Zeit",
                    value=datetime.strptime("08:00", "%H:%M").time(),
                    key=f"cal_edit_checkin_time_{checkin.get('id', 0)}"
                )
        
        with col2:
            check_out_time = checkin.get("check_out_time")
            if check_out_time:
                check_out = st.time_input(
                    "Check-out Zeit",
                    value=check_out_time.time() if isinstance(check_out_time, datetime) else datetime.strptime("17:00", "%H:%M").time(),
                    key=f"cal_edit_checkout_time_{checkin.get('id', 0)}"
                )
            else:
                check_out = st.time_input(
                    "Check-out Zeit",
                    value=datetime.strptime("17:00", "%H:%M").time(),
                    key=f"cal_edit_checkout_time_{checkin.get('id', 0)}"
                )
        
        # Pausendauer
        break_duration = st.number_input(
            "Pausendauer (Stunden)",
            min_value=0.0,
            max_value=4.0,
            value=checkin.get("break_duration", 1.0),
            step=0.25,
            key=f"cal_edit_break_duration_{checkin.get('id', 0)}"
        )
        
        # Status
        status = st.selectbox(
            "Status",
            ["Offen", "In Bearbeitung", "Abgeschlossen", "Storniert"],
            index=["Offen", "In Bearbeitung", "Abgeschlossen", "Storniert"].index(checkin.get("status", "Offen")),
            key=f"cal_edit_status_{checkin.get('id', 0)}"
        )
        
        # Kommentar
        comment = st.text_area(
            "Kommentar",
            value=checkin.get("comment", ""),
            key=f"cal_edit_comment_{checkin.get('id', 0)}"
        )
        
        # Änderungen speichern
        if st.button("Änderungen speichern", key=f"cal_save_changes_{checkin.get('id', 0)}"):
            # Originaldaten für Audit-Trail
            original_data = {
                "check_in_time": checkin.get("check_in_time"),
                "check_out_time": checkin.get("check_out_time"),
                "break_duration": checkin.get("break_duration"),
                "status": checkin.get("status"),
                "comment": checkin.get("comment")
            }
            
            # Check-in und Check-out Zeiten kombinieren
            check_in_datetime = datetime.combine(checkin["date"], check_in)
            check_out_datetime = datetime.combine(checkin["date"], check_out)
            
            # Daten aktualisieren
            checkin["check_in_time"] = check_in_datetime
            checkin["check_out_time"] = check_out_datetime
            checkin["break_duration"] = break_duration
            checkin["status"] = status
            checkin["comment"] = comment
            checkin["modified_by"] = st.session_state.get("username", "Admin")
            checkin["modified_at"] = datetime.now()
            
            st.success("Änderungen wurden gespeichert!")
            
            # Audit-Trail
            if "audit_trail" not in st.session_state:
                st.session_state["audit_trail"] = []
            
            # Änderungen für Audit-Trail erfassen
            changes = []
            if original_data["check_in_time"] != check_in_datetime:
                changes.append(f"Check-in: {original_data['check_in_time']} -> {check_in_datetime}")
            if original_data["check_out_time"] != check_out_datetime:
                changes.append(f"Check-out: {original_data['check_out_time']} -> {check_out_datetime}")
            if original_data["break_duration"] != break_duration:
                changes.append(f"Pause: {original_data['break_duration']} -> {break_duration}")
            if original_data["status"] != status:
                changes.append(f"Status: {original_data['status']} -> {status}")
            if original_data["comment"] != comment:
                changes.append("Kommentar geändert")
            
            employee = next((emp for emp in st.session_state["employees"] if emp["id"] == checkin.get("employee_id")), {"name": "Unbekannt"})
            
            st.session_state["audit_trail"].append({
                "action": "update",
                "entity": "checkin",
                "entity_id": checkin.get("id", 0),
                "user": st.session_state.get("username", "Admin"),
                "timestamp": datetime.now(),
                "details": f"Zeiteintrag für {employee['name']} am {checkin['date']} geändert: {', '.join(changes)}"
            })
    
    def edit_sick_leave_in_calendar(sick_leave):
        """
        Bearbeitet eine Krankmeldung direkt im Kalender
        """
        st.subheader("Krankmeldung bearbeiten")
        
        # Zeitraum
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Von",
                value=sick_leave["start_date"],
                key=f"cal_edit_sick_start_{sick_leave.get('id', 0)}"
            )
        with col2:
            end_date = st.date_input(
                "Bis",
                value=sick_leave["end_date"],
                key=f"cal_edit_sick_end_{sick_leave.get('id', 0)}"
            )
        
        # Begründung
        reason = st.text_area(
            "Begründung",
            value=sick_leave.get("reason", ""),
            key=f"cal_edit_sick_reason_{sick_leave.get('id', 0)}"
        )
        
        # Status
        status = st.selectbox(
            "Status",
            ["Eingereicht", "Bestätigt", "Abgelehnt"],
            index=["Eingereicht", "Bestätigt", "Abgelehnt"].index(sick_leave.get("status", "Eingereicht")),
            key=f"cal_edit_sick_status_{sick_leave.get('id', 0)}"
        )
        
        # Kommentar
        comment = st.text_area(
            "Kommentar",
            value=sick_leave.get("comment", ""),
            key=f"cal_edit_sick_comment_{sick_leave.get('id', 0)}"
        )
        
        # Änderungen speichern
        if st.button("Änderungen speichern", key=f"cal_save_sick_{sick_leave.get('id', 0)}"):
            # Originaldaten für Audit-Trail
            original_data = {
                "start_date": sick_leave.get("start_date"),
                "end_date": sick_leave.get("end_date"),
                "reason": sick_leave.get("reason", ""),
                "status": sick_leave.get("status", "Eingereicht"),
                "comment": sick_leave.get("comment", "")
            }
            
            # Daten aktualisieren
            sick_leave["start_date"] = start_date
            sick_leave["end_date"] = end_date
            sick_leave["reason"] = reason
            sick_leave["status"] = status
            sick_leave["comment"] = comment
            sick_leave["modified_by"] = st.session_state.get("username", "Admin")
            sick_leave["modified_at"] = datetime.now()
            
            st.success("Änderungen wurden gespeichert!")
            
            # Audit-Trail
            if "audit_trail" not in st.session_state:
                st.session_state["audit_trail"] = []
            
            # Änderungen für Audit-Trail erfassen
            changes = []
            if original_data["start_date"] != start_date:
                changes.append(f"Start: {original_data['start_date']} -> {start_date}")
            if original_data["end_date"] != end_date:
                changes.append(f"Ende: {original_data['end_date']} -> {end_date}")
            if original_data["reason"] != reason:
                changes.append("Begründung geändert")
            if original_data["status"] != status:
                changes.append(f"Status: {original_data['status']} -> {status}")
            if original_data["comment"] != comment:
                changes.append("Kommentar geändert")
            
            employee = next((emp for emp in st.session_state["employees"] if emp["id"] == sick_leave.get("employee_id")), {"name": "Unbekannt"})
            
            st.session_state["audit_trail"].append({
                "action": "update",
                "entity": "sick_leave",
                "entity_id": sick_leave.get("id", 0),
                "user": st.session_state.get("username", "Admin"),
                "timestamp": datetime.now(),
                "details": f"Krankmeldung für {employee['name']} vom {sick_leave['start_date']} bis {sick_leave['end_date']} geändert: {', '.join(changes)}"
            })
    
    def edit_vacation_in_calendar(vacation):
        """
        Bearbeitet einen Urlaubsantrag direkt im Kalender
        """
        st.subheader("Urlaubsantrag bearbeiten")
        
        # Zeitraum
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Von",
                value=vacation["start_date"],
                key=f"cal_edit_vac_start_{vacation.get('id', 0)}"
            )
        with col2:
            end_date = st.date_input(
                "Bis",
                value=vacation["end_date"],
                key=f"cal_edit_vac_end_{vacation.get('id', 0)}"
            )
        
        # Begründung
        reason = st.text_area(
            "Begründung",
            value=vacation.get("reason", ""),
            key=f"cal_edit_vac_reason_{vacation.get('id', 0)}"
        )
        
        # Status
        status = st.selectbox(
            "Status",
            ["Beantragt", "Genehmigt", "Abgelehnt"],
            index=["Beantragt", "Genehmigt", "Abgelehnt"].index(vacation.get("status", "Beantragt")),
            key=f"cal_edit_vac_status_{vacation.get('id', 0)}"
        )
        
        # Kommentar
        comment = st.text_area(
            "Kommentar",
            value=vacation.get("comment", ""),
            key=f"cal_edit_vac_comment_{vacation.get('id', 0)}"
        )
        
        # Änderungen speichern
        if st.button("Änderungen speichern", key=f"cal_save_vac_{vacation.get('id', 0)}"):
            # Originaldaten für Audit-Trail
            original_data = {
                "start_date": vacation.get("start_date"),
                "end_date": vacation.get("end_date"),
                "reason": vacation.get("reason", ""),
                "status": vacation.get("status", "Beantragt"),
                "comment": vacation.get("comment", "")
            }
            
            # Daten aktualisieren
            vacation["start_date"] = start_date
            vacation["end_date"] = end_date
            vacation["reason"] = reason
            vacation["status"] = status
            vacation["comment"] = comment
            vacation["modified_by"] = st.session_state.get("username", "Admin")
            vacation["modified_at"] = datetime.now()
            
            st.success("Änderungen wurden gespeichert!")
            
            # Audit-Trail
            if "audit_trail" not in st.session_state:
                st.session_state["audit_trail"] = []
            
            # Änderungen für Audit-Trail erfassen
            changes = []
            if original_data["start_date"] != start_date:
                changes.append(f"Start: {original_data['start_date']} -> {start_date}")
            if original_data["end_date"] != end_date:
                changes.append(f"Ende: {original_data['end_date']} -> {end_date}")
            if original_data["reason"] != reason:
                changes.append("Begründung geändert")
            if original_data["status"] != status:
                changes.append(f"Status: {original_data['status']} -> {status}")
            if original_data["comment"] != comment:
                changes.append("Kommentar geändert")
            
            employee = next((emp for emp in st.session_state["employees"] if emp["id"] == vacation.get("employee_id")), {"name": "Unbekannt"})
            
            st.session_state["audit_trail"].append({
                "action": "update",
                "entity": "vacation",
                "entity_id": vacation.get("id", 0),
                "user": st.session_state.get("username", "Admin"),
                "timestamp": datetime.now(),
                "details": f"Urlaubsantrag für {employee['name']} vom {vacation['start_date']} bis {vacation['end_date']} geändert: {', '.join(changes)}"
            })
            
            # Benachrichtigung senden, wenn Status geändert wurde
            if original_data["status"] != status:
                # In einer echten App würde hier eine E-Mail gesendet werden
                st.info(f"Benachrichtigung an {employee['name']} über Statusänderung des Urlaubsantrags wurde gesendet.")
    
    def create_new_entry_in_calendar(date, employee_id):
        """
        Erstellt einen neuen Eintrag direkt im Kalender
        """
        st.subheader("Neuen Eintrag erstellen")
        
        # Art des Eintrags auswählen
        entry_type = st.selectbox(
            "Art des Eintrags",
            ["Arbeitszeit", "Krankmeldung", "Urlaubsantrag"],
            key=f"cal_new_entry_type_{date}"
        )
        
        if entry_type == "Arbeitszeit":
            # Check-in und Check-out Zeiten
            col1, col2 = st.columns(2)
            with col1:
                check_in = st.time_input(
                    "Check-in Zeit",
                    value=datetime.strptime("08:00", "%H:%M").time(),
                    key=f"cal_new_checkin_time_{date}"
                )
            with col2:
                check_out = st.time_input(
                    "Check-out Zeit",
                    value=datetime.strptime("17:00", "%H:%M").time(),
                    key=f"cal_new_checkout_time_{date}"
                )
            
            # Pausendauer
            break_duration = st.number_input(
                "Pausendauer (Stunden)",
                min_value=0.0,
                max_value=4.0,
                value=1.0,
                step=0.25,
                key=f"cal_new_break_duration_{date}"
            )
            
            # Status
            status = st.selectbox(
                "Status",
                ["Offen", "In Bearbeitung", "Abgeschlossen", "Storniert"],
                index=2,  # Standardmäßig "Abgeschlossen"
                key=f"cal_new_status_{date}"
            )
            
            # Kommentar
            comment = st.text_area(
                "Kommentar",
                value="",
                key=f"cal_new_comment_{date}"
            )
            
            if st.button("Eintrag erstellen", key=f"cal_create_checkin_{date}"):
                # Check-in und Check-out Zeiten kombinieren
                check_in_datetime = datetime.combine(date, check_in)
                check_out_datetime = datetime.combine(date, check_out)
                
                # Neuen Eintrag erstellen
                new_checkin = {
                    "id": len(st.session_state["checkins"]) + 1,
                    "employee_id": employee_id,
                    "date": date,
                    "check_in_time": check_in_datetime,
                    "check_out_time": check_out_datetime,
                    "break_duration": break_duration,
                    "status": status,
                    "comment": comment,
                    "created_by": st.session_state.get("username", "Admin"),
                    "created_at": datetime.now()
                }
                
                # Zur Liste hinzufügen
                st.session_state["checkins"].append(new_checkin)
                st.success("Neuer Arbeitszeit-Eintrag wurde erstellt!")
                
                # Audit-Trail
                if "audit_trail" not in st.session_state:
                    st.session_state["audit_trail"] = []
                
                employee = next((emp for emp in st.session_state["employees"] if emp["id"] == employee_id), {"name": "Unbekannt"})
                
                st.session_state["audit_trail"].append({
                    "action": "create",
                    "entity": "checkin",
                    "entity_id": new_checkin["id"],
                    "user": st.session_state.get("username", "Admin"),
                    "timestamp": datetime.now(),
                    "details": f"Neuer Arbeitszeit-Eintrag für {employee['name']} am {date} erstellt"
                })
        
        elif entry_type == "Krankmeldung":
            # Zeitraum
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input(
                    "Von",
                    value=date,
                    key=f"cal_new_sick_start_{date}"
                )
            with col2:
                end_date = st.date_input(
                    "Bis",
                    value=date,
                    key=f"cal_new_sick_end_{date}"
                )
            
            # Begründung
            reason = st.text_area(
                "Begründung",
                value="",
                key=f"cal_new_sick_reason_{date}"
            )
            
            # Status
            status = st.selectbox(
                "Status",
                ["Eingereicht", "Bestätigt", "Abgelehnt"],
                index=1,  # Standardmäßig "Bestätigt"
                key=f"cal_new_sick_status_{date}"
            )
            
            # Kommentar
            comment = st.text_area(
                "Kommentar",
                value="",
                key=f"cal_new_sick_comment_{date}"
            )
            
            if st.button("Eintrag erstellen", key=f"cal_create_sick_{date}"):
                # Neuen Eintrag erstellen
                new_sick_leave = {
                    "id": len(st.session_state["sick_leaves"]) + 1,
                    "employee_id": employee_id,
                    "start_date": start_date,
                    "end_date": end_date,
                    "reason": reason,
                    "status": status,
                    "comment": comment,
                    "created_by": st.session_state.get("username", "Admin"),
                    "created_at": datetime.now()
                }
                
                # Zur Liste hinzufügen
                st.session_state["sick_leaves"].append(new_sick_leave)
                st.success("Neue Krankmeldung wurde erstellt!")
                
                # Mitarbeiterstatus aktualisieren
                employee = next((emp for emp in st.session_state["employees"] if emp["id"] == employee_id), None)
                if employee and status == "Bestätigt":
                    employee["status"] = "Krank"
                
                # Audit-Trail
                if "audit_trail" not in st.session_state:
                    st.session_state["audit_trail"] = []
                
                employee_name = employee["name"] if employee else "Unbekannt"
                
                st.session_state["audit_trail"].append({
                    "action": "create",
                    "entity": "sick_leave",
                    "entity_id": new_sick_leave["id"],
                    "user": st.session_state.get("username", "Admin"),
                    "timestamp": datetime.now(),
                    "details": f"Neue Krankmeldung für {employee_name} vom {start_date} bis {end_date} erstellt"
                })
        
        elif entry_type == "Urlaubsantrag":
            # Zeitraum
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input(
                    "Von",
                    value=date,
                    key=f"cal_new_vac_start_{date}"
                )
            with col2:
                end_date = st.date_input(
                    "Bis",
                    value=date,
                    key=f"cal_new_vac_end_{date}"
                )
            
            # Begründung
            reason = st.text_area(
                "Begründung",
                value="",
                key=f"cal_new_vac_reason_{date}"
            )
            
            # Status
            status = st.selectbox(
                "Status",
                ["Beantragt", "Genehmigt", "Abgelehnt"],
                index=1,  # Standardmäßig "Genehmigt"
                key=f"cal_new_vac_status_{date}"
            )
            
            # Kommentar
            comment = st.text_area(
                "Kommentar",
                value="",
                key=f"cal_new_vac_comment_{date}"
            )
            
            if st.button("Eintrag erstellen", key=f"cal_create_vac_{date}"):
                # Neuen Eintrag erstellen
                new_vacation = {
                    "id": len(st.session_state["vacation_requests"]) + 1,
                    "employee_id": employee_id,
                    "start_date": start_date,
                    "end_date": end_date,
                    "reason": reason,
                    "status": status,
                    "comment": comment,
                    "created_by": st.session_state.get("username", "Admin"),
                    "created_at": datetime.now()
                }
                
                # Zur Liste hinzufügen
                st.session_state["vacation_requests"].append(new_vacation)
                st.success("Neuer Urlaubsantrag wurde erstellt!")
                
                # Mitarbeiterstatus aktualisieren
                employee = next((emp for emp in st.session_state["employees"] if emp["id"] == employee_id), None)
                if employee and status == "Genehmigt":
                    employee["status"] = "Urlaub"
                
                # Audit-Trail
                if "audit_trail" not in st.session_state:
                    st.session_state["audit_trail"] = []
                
                employee_name = employee["name"] if employee else "Unbekannt"
                
                st.session_state["audit_trail"].append({
                    "action": "create",
                    "entity": "vacation",
                    "entity_id": new_vacation["id"],
                    "user": st.session_state.get("username", "Admin"),
                    "timestamp": datetime.now(),
                    "details": f"Neuer Urlaubsantrag für {employee_name} vom {start_date} bis {end_date} erstellt"
                })
    
    return {
        "show_interactive_calendar": show_interactive_calendar,
        "edit_checkin_in_calendar": edit_checkin_in_calendar,
        "edit_sick_leave_in_calendar": edit_sick_leave_in_calendar,
        "edit_vacation_in_calendar": edit_vacation_in_calendar,
        "create_new_entry_in_calendar": create_new_entry_in_calendar
    }

# Hauptfunktion zur Integration aller Admin-Funktionserweiterungen
def integrate_admin_function_enhancements(app):
    """
    Integriert alle Admin-Funktionserweiterungen in die App
    """
    # Suchfunktion für Mitarbeiter implementieren
    employee_search = implement_employee_search()
    
    # Filteroptionen für Arbeitszeiten implementieren
    worktime_filters = implement_worktime_filters()
    
    # Direkte Bearbeitung von Einträgen in der Kalenderansicht implementieren
    calendar_editing = implement_calendar_editing()
    
    # Funktionen in die App integrieren
    # (Hier würde die tatsächliche Integration in die App erfolgen)
    
    # Beispiel für die Integration in die Hauptapp
    def extended_main():
        # Seitenauswahl erweitern
        if st.session_state.get("is_admin", False):
            # Admin-Seiten
            if page == "Mitarbeitersuche":
                employee_search["show_employee_search"]()
            elif page == "Arbeitszeiten filtern":
                worktime_filters["show_worktime_filters"]()
            elif page == "Kalender":
                calendar_editing["show_interactive_calendar"]()
            # ... andere Seiten
    
    # Rückgabe der erweiterten App-Funktionalität
    return {
        "extended_main": extended_main,
        "employee_search": employee_search,
        "worktime_filters": worktime_filters,
        "calendar_editing": calendar_editing
    }
