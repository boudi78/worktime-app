# Implementierung der Zeiterfassungsverbesserungen

# 1. Unterstützung für Teilzeit- und Schichtarbeiter (flexible Arbeitszeiten)
def implement_flexible_work_times():
    """
    Erweiterungen für die Unterstützung flexibler Arbeitszeiten
    """
    # Arbeitszeitmodelle definieren
    work_time_models = {
        "vollzeit": {
            "name": "Vollzeit",
            "hours_per_week": 40,
            "default_start": "08:00",
            "default_end": "17:00",
            "break_duration": 1.0,
            "days": ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]
        },
        "teilzeit_50": {
            "name": "Teilzeit 50%",
            "hours_per_week": 20,
            "default_start": "08:00",
            "default_end": "12:00",
            "break_duration": 0.0,
            "days": ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]
        },
        "teilzeit_75": {
            "name": "Teilzeit 75%",
            "hours_per_week": 30,
            "default_start": "08:00",
            "default_end": "14:00",
            "break_duration": 0.5,
            "days": ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]
        },
        "fruehschicht": {
            "name": "Frühschicht",
            "hours_per_week": 40,
            "default_start": "06:00",
            "default_end": "14:00",
            "break_duration": 0.5,
            "days": ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]
        },
        "spaetschicht": {
            "name": "Spätschicht",
            "hours_per_week": 40,
            "default_start": "14:00",
            "default_end": "22:00",
            "break_duration": 0.5,
            "days": ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]
        },
        "wochenendschicht": {
            "name": "Wochenendschicht",
            "hours_per_week": 16,
            "default_start": "08:00",
            "default_end": "16:00",
            "break_duration": 0.5,
            "days": ["Samstag", "Sonntag"]
        },
        "individuell": {
            "name": "Individuell",
            "hours_per_week": 40,
            "default_start": "08:00",
            "default_end": "17:00",
            "break_duration": 1.0,
            "days": ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]
        }
    }
    
    # Arbeitszeitmodell zum Mitarbeiterprofil hinzufügen
    def extend_employee_profile():
        """
        Erweitert das Mitarbeiterprofil um Arbeitszeitmodell-Informationen
        """
        # Beispiel für die Erweiterung des Mitarbeiterprofils
        for employee in st.session_state["employees"]:
            if "work_time_model" not in employee:
                employee["work_time_model"] = "vollzeit"
            if "custom_schedule" not in employee:
                employee["custom_schedule"] = {}
    
    # Arbeitszeitmodell-Auswahl im Profil
    def add_work_time_model_selection_to_profile():
        """
        Fügt die Arbeitszeitmodell-Auswahl zum Profil hinzu
        """
        st.subheader("Arbeitszeitmodell")
        
        # Arbeitszeitmodell auswählen
        model_options = [model["name"] for model in work_time_models.values()]
        selected_model = st.selectbox(
            "Arbeitszeitmodell", 
            model_options,
            index=model_options.index(work_time_models[st.session_state["current_employee"]["work_time_model"]]["name"]),
            key="work_time_model_select"
        )
        
        # Modell-ID aus dem Namen ermitteln
        model_id = next((key for key, model in work_time_models.items() 
                         if model["name"] == selected_model), "vollzeit")
        
        # Wenn individuelles Modell ausgewählt wurde, zusätzliche Einstellungen anzeigen
        if model_id == "individuell":
            st.subheader("Individuelle Arbeitszeiten")
            
            # Wochentage auswählen
            days = st.multiselect(
                "Arbeitstage",
                ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag", "Samstag", "Sonntag"],
                default=st.session_state["current_employee"].get("custom_schedule", {}).get("days", 
                                                                                          ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"]),
                key="custom_days_select"
            )
            
            # Wochenstunden festlegen
            hours_per_week = st.number_input(
                "Wochenstunden",
                min_value=1.0,
                max_value=60.0,
                value=st.session_state["current_employee"].get("custom_schedule", {}).get("hours_per_week", 40.0),
                step=0.5,
                key="custom_hours_input"
            )
            
            # Standardzeiten festlegen
            col1, col2 = st.columns(2)
            with col1:
                default_start = st.time_input(
                    "Standard-Beginn",
                    value=datetime.strptime(
                        st.session_state["current_employee"].get("custom_schedule", {}).get("default_start", "08:00"),
                        "%H:%M"
                    ).time(),
                    key="custom_start_input"
                )
            with col2:
                default_end = st.time_input(
                    "Standard-Ende",
                    value=datetime.strptime(
                        st.session_state["current_employee"].get("custom_schedule", {}).get("default_end", "17:00"),
                        "%H:%M"
                    ).time(),
                    key="custom_end_input"
                )
            
            # Pausendauer festlegen
            break_duration = st.slider(
                "Pausendauer (Stunden)",
                min_value=0.0,
                max_value=2.0,
                value=st.session_state["current_employee"].get("custom_schedule", {}).get("break_duration", 1.0),
                step=0.25,
                key="custom_break_input"
            )
            
            # Individuelle Einstellungen speichern
            if st.button("Individuelle Einstellungen speichern", key="save_custom_schedule"):
                st.session_state["current_employee"]["custom_schedule"] = {
                    "days": days,
                    "hours_per_week": hours_per_week,
                    "default_start": default_start.strftime("%H:%M"),
                    "default_end": default_end.strftime("%H:%M"),
                    "break_duration": break_duration
                }
                st.success("Individuelle Arbeitszeiten gespeichert!")
        
        # Arbeitszeitmodell speichern
        if st.button("Arbeitszeitmodell speichern", key="save_work_time_model"):
            st.session_state["current_employee"]["work_time_model"] = model_id
            st.success("Arbeitszeitmodell gespeichert!")
    
    # Anpassung der Check-in/Check-out-Logik
    def adapt_checkin_logic():
        """
        Passt die Check-in/Check-out-Logik an flexible Arbeitszeiten an
        """
        # Beispiel für die Anpassung der Check-in-Seite
        def show_checkin_page_with_flexible_times():
            st.title("Check-in/Check-out")
            
            # Mitarbeiter auswählen (in einer echten App wäre dies der angemeldete Benutzer)
            if st.session_state.get("is_admin", False):
                employee = st.selectbox("Mitarbeiter auswählen", 
                                      [emp["name"] for emp in st.session_state["employees"] if emp["status"] == "Anwesend"],
                                      key="checkin_employee_select")
                employee_id = next(emp["id"] for emp in st.session_state["employees"] if emp["name"] == employee)
                employee_data = next(emp for emp in st.session_state["employees"] if emp["name"] == employee)
            else:
                employee = st.session_state.get("username")
                employee_id = st.session_state.get("user_id")
                employee_data = next(emp for emp in st.session_state["employees"] if emp["id"] == employee_id)
            
            # Arbeitszeitmodell des Mitarbeiters abrufen
            model_id = employee_data.get("work_time_model", "vollzeit")
            
            # Wenn individuelles Modell, dann benutzerdefinierte Einstellungen verwenden
            if model_id == "individuell" and "custom_schedule" in employee_data:
                work_model = {
                    "name": "Individuell",
                    "hours_per_week": employee_data["custom_schedule"].get("hours_per_week", 40),
                    "default_start": employee_data["custom_schedule"].get("default_start", "08:00"),
                    "default_end": employee_data["custom_schedule"].get("default_end", "17:00"),
                    "break_duration": employee_data["custom_schedule"].get("break_duration", 1.0),
                    "days": employee_data["custom_schedule"].get("days", ["Montag", "Dienstag", "Mittwoch", "Donnerstag", "Freitag"])
                }
            else:
                work_model = work_time_models[model_id]
            
            # Aktuellen Wochentag ermitteln
            today = datetime.now().date()
            weekday = calendar.day_name[today.weekday()]
            weekday_de = {
                "Monday": "Montag",
                "Tuesday": "Dienstag",
                "Wednesday": "Mittwoch",
                "Thursday": "Donnerstag",
                "Friday": "Freitag",
                "Saturday": "Samstag",
                "Sunday": "Sonntag"
            }.get(weekday, weekday)
            
            # Prüfen, ob heute ein Arbeitstag ist
            is_workday = weekday_de in work_model["days"]
            
            # Informationen zum Arbeitszeitmodell anzeigen
            st.info(f"Arbeitszeitmodell: {work_model['name']}")
            if is_workday:
                st.info(f"Reguläre Arbeitszeit heute: {work_model['default_start']} - {work_model['default_end']} (Pause: {work_model['break_duration']} Std.)")
            else:
                st.warning(f"Heute ({weekday_de}) ist kein regulärer Arbeitstag laut Arbeitszeitmodell.")
            
            # Rest der Check-in-Logik...
            # (Hier würde der bestehende Code für die Check-in-Funktionalität folgen)
    
    # Rückgabe der Funktionen für die Integration
    return {
        "work_time_models": work_time_models,
        "extend_employee_profile": extend_employee_profile,
        "add_work_time_model_selection_to_profile": add_work_time_model_selection_to_profile,
        "adapt_checkin_logic": adapt_checkin_logic
    }

# 2. Automatische Pausenregelung
def implement_automatic_breaks():
    """
    Implementierung der automatischen Pausenregelung
    """
    # Konfiguration für Pausenregeln
    break_rules = {
        "short_break": {
            "min_work_hours": 4.0,
            "duration": 0.25  # 15 Minuten
        },
        "lunch_break": {
            "min_work_hours": 6.0,
            "duration": 0.5  # 30 Minuten
        },
        "long_break": {
            "min_work_hours": 9.0,
            "duration": 1.0  # 60 Minuten
        }
    }
    
    # Funktion zur Berechnung der automatischen Pausen
    def calculate_automatic_breaks(check_in_time, check_out_time, employee_id):
        """
        Berechnet automatische Pausen basierend auf der Arbeitsdauer
        """
        if not check_in_time or not check_out_time:
            return 0.0
        
        # Arbeitszeitmodell des Mitarbeiters abrufen
        employee = next((emp for emp in st.session_state["employees"] if emp["id"] == employee_id), None)
        if not employee:
            return 0.0
        
        model_id = employee.get("work_time_model", "vollzeit")
        
        # Wenn individuelles Modell, dann benutzerdefinierte Einstellungen verwenden
        if model_id == "individuell" and "custom_schedule" in employee:
            break_duration = employee["custom_schedule"].get("break_duration", 1.0)
        else:
            # Arbeitszeitmodell aus der Implementierung für flexible Arbeitszeiten abrufen
            work_time_models = implement_flexible_work_times()["work_time_models"]
            break_duration = work_time_models[model_id]["break_duration"]
        
        # Arbeitsdauer berechnen (in Stunden)
        work_duration = (check_out_time - check_in_time).total_seconds() / 3600
        
        # Pausendauer basierend auf Arbeitsdauer und Regeln bestimmen
        if work_duration >= break_rules["long_break"]["min_work_hours"]:
            return break_rules["long_break"]["duration"]
        elif work_duration >= break_rules["lunch_break"]["min_work_hours"]:
            return break_rules["lunch_break"]["duration"]
        elif work_duration >= break_rules["short_break"]["min_work_hours"]:
            return break_rules["short_break"]["duration"]
        else:
            return 0.0
    
    # Funktion zur Anzeige und Bearbeitung von Pausen
    def show_break_management(check_in_time, check_out_time, employee_id):
        """
        Zeigt die Pausenverwaltung an und ermöglicht die manuelle Eingabe
        """
        if not check_in_time:
            return 0.0
        
        st.subheader("Pausenverwaltung")
        
        # Automatische Pausenberechnung
        auto_break = calculate_automatic_breaks(check_in_time, check_out_time, employee_id)
        
        # Option zur manuellen Überschreibung
        use_auto_break = st.checkbox(
            "Automatische Pausenberechnung verwenden", 
            value=True,
            key=f"use_auto_break_{employee_id}"
        )
        
        if use_auto_break:
            st.info(f"Automatisch berechnete Pause: {auto_break:.2f} Stunden ({int(auto_break * 60)} Minuten)")
            break_duration = auto_break
        else:
            break_duration = st.number_input(
                "Pausendauer (Stunden)",
                min_value=0.0,
                max_value=4.0,
                value=auto_break,
                step=0.25,
                key=f"manual_break_{employee_id}"
            )
        
        return break_duration
    
    # Funktion zur Integration der Pausenberechnung in die Arbeitszeitberechnung
    def calculate_work_hours_with_breaks(check_in_time, check_out_time, break_duration):
        """
        Berechnet die Arbeitszeit unter Berücksichtigung der Pausen
        """
        if not check_in_time or not check_out_time:
            return 0.0
        
        # Gesamtdauer berechnen (in Stunden)
        total_duration = (check_out_time - check_in_time).total_seconds() / 3600
        
        # Arbeitszeit = Gesamtdauer - Pause
        work_hours = total_duration - break_duration
        
        # Negative Arbeitszeit verhindern
        return max(0.0, work_hours)
    
    # Rückgabe der Funktionen für die Integration
    return {
        "break_rules": break_rules,
        "calculate_automatic_breaks": calculate_automatic_breaks,
        "show_break_management": show_break_management,
        "calculate_work_hours_with_breaks": calculate_work_hours_with_breaks
    }

# 3. Admin-Korrekturmöglichkeiten für Check-in/Check-out
def implement_admin_corrections():
    """
    Implementierung der Admin-Korrekturmöglichkeiten für Check-in/Check-out
    """
    # Funktion zur Anzeige der Korrekturseite
    def show_time_correction_page():
        """
        Zeigt die Seite zur Korrektur von Arbeitszeiten an
        """
        st.title("Arbeitszeiten korrigieren")
        
        # Nur für Admins zugänglich
        if not st.session_state.get("is_admin", False):
            st.error("Sie haben keine Berechtigung für diese Seite.")
            return
        
        # Mitarbeiter auswählen
        employee = st.selectbox(
            "Mitarbeiter auswählen", 
            [emp["name"] for emp in st.session_state["employees"]],
            key="correction_employee_select"
        )
        employee_id = next(emp["id"] for emp in st.session_state["employees"] if emp["name"] == employee)
        
        # Zeitraum auswählen
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Von", 
                value=datetime.now().date() - timedelta(days=7),
                key="correction_start_date"
            )
        with col2:
            end_date = st.date_input(
                "Bis", 
                value=datetime.now().date(),
                key="correction_end_date"
            )
        
        # Arbeitszeiten für den ausgewählten Zeitraum abrufen
        checkins = [c for c in st.session_state["checkins"] 
                   if c["employee_id"] == employee_id 
                   and start_date <= c["date"] <= end_date]
        
        # Nach Datum sortieren
        checkins.sort(key=lambda x: x["date"], reverse=True)
        
        if not checkins:
            st.info(f"Keine Arbeitszeiten für {employee} im ausgewählten Zeitraum gefunden.")
            
            # Option zum Hinzufügen eines neuen Eintrags
            st.subheader("Neuen Eintrag hinzufügen")
            
            new_date = st.date_input(
                "Datum",
                value=datetime.now().date(),
                key="new_checkin_date"
            )
            
            col1, col2 = st.columns(2)
            with col1:
                new_check_in = st.time_input(
                    "Check-in Zeit",
                    value=datetime.strptime("08:00", "%H:%M").time(),
                    key="new_checkin_time"
                )
            with col2:
                new_check_out = st.time_input(
                    "Check-out Zeit",
                    value=datetime.strptime("17:00", "%H:%M").time(),
                    key="new_checkout_time"
                )
            
            # Pausendauer
            break_duration = st.number_input(
                "Pausendauer (Stunden)",
                min_value=0.0,
                max_value=4.0,
                value=1.0,
                step=0.25,
                key="new_break_duration"
            )
            
            # Kommentar
            comment = st.text_area(
                "Kommentar",
                value="Manuell hinzugefügt durch Administrator",
                key="new_checkin_comment"
            )
            
            if st.button("Eintrag hinzufügen", key="add_new_checkin"):
                # Check-in und Check-out Zeiten kombinieren
                check_in_datetime = datetime.combine(new_date, new_check_in)
                check_out_datetime = datetime.combine(new_date, new_check_out)
                
                # Neuen Eintrag erstellen
                new_checkin = {
                    "id": len(st.session_state["checkins"]) + 1,
                    "employee_id": employee_id,
                    "date": new_date,
                    "check_in_time": check_in_datetime,
                    "check_out_time": check_out_datetime,
                    "break_duration": break_duration,
                    "status": "Abgeschlossen",
                    "comment": comment,
                    "modified_by": st.session_state.get("username", "Admin"),
                    "modified_at": datetime.now()
                }
                
                # Zur Liste hinzufügen
                st.session_state["checkins"].append(new_checkin)
                st.success("Neuer Eintrag wurde hinzugefügt!")
                
                # Audit-Trail
                if "audit_trail" not in st.session_state:
                    st.session_state["audit_trail"] = []
                
                st.session_state["audit_trail"].append({
                    "action": "create",
                    "entity": "checkin",
                    "entity_id": new_checkin["id"],
                    "user": st.session_state.get("username", "Admin"),
                    "timestamp": datetime.now(),
                    "details": f"Neuer Zeiteintrag für {employee} am {new_date} erstellt"
                })
                
                # Benachrichtigung an Mitarbeiter (simuliert)
                st.info(f"Benachrichtigung an {employee} wurde gesendet.")
            
            return
        
        # Bestehende Einträge anzeigen und bearbeiten
        st.subheader("Bestehende Einträge")
        
        for i, checkin in enumerate(checkins):
            with st.expander(f"{checkin['date']} - {checkin.get('status', 'Unbekannt')}"):
                # ID des Eintrags
                checkin_id = checkin.get("id", i)
                
                # Datum (nicht editierbar)
                st.text(f"Datum: {checkin['date']}")
                
                # Check-in und Check-out Zeiten
                col1, col2 = st.columns(2)
                with col1:
                    check_in_time = checkin.get("check_in_time")
                    if check_in_time:
                        check_in = st.time_input(
                            "Check-in Zeit",
                            value=check_in_time.time() if isinstance(check_in_time, datetime) else datetime.strptime("08:00", "%H:%M").time(),
                            key=f"edit_checkin_time_{checkin_id}"
                        )
                    else:
                        check_in = st.time_input(
                            "Check-in Zeit",
                            value=datetime.strptime("08:00", "%H:%M").time(),
                            key=f"edit_checkin_time_{checkin_id}"
                        )
                
                with col2:
                    check_out_time = checkin.get("check_out_time")
                    if check_out_time:
                        check_out = st.time_input(
                            "Check-out Zeit",
                            value=check_out_time.time() if isinstance(check_out_time, datetime) else datetime.strptime("17:00", "%H:%M").time(),
                            key=f"edit_checkout_time_{checkin_id}"
                        )
                    else:
                        check_out = st.time_input(
                            "Check-out Zeit",
                            value=datetime.strptime("17:00", "%H:%M").time(),
                            key=f"edit_checkout_time_{checkin_id}"
                        )
                
                # Pausendauer
                break_duration = st.number_input(
                    "Pausendauer (Stunden)",
                    min_value=0.0,
                    max_value=4.0,
                    value=checkin.get("break_duration", 1.0),
                    step=0.25,
                    key=f"edit_break_duration_{checkin_id}"
                )
                
                # Status
                status = st.selectbox(
                    "Status",
                    ["Offen", "In Bearbeitung", "Abgeschlossen", "Storniert"],
                    index=["Offen", "In Bearbeitung", "Abgeschlossen", "Storniert"].index(checkin.get("status", "Offen")),
                    key=f"edit_status_{checkin_id}"
                )
                
                # Kommentar
                comment = st.text_area(
                    "Kommentar",
                    value=checkin.get("comment", ""),
                    key=f"edit_comment_{checkin_id}"
                )
                
                # Änderungen speichern
                if st.button("Änderungen speichern", key=f"save_changes_{checkin_id}"):
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
                    
                    st.session_state["audit_trail"].append({
                        "action": "update",
                        "entity": "checkin",
                        "entity_id": checkin_id,
                        "user": st.session_state.get("username", "Admin"),
                        "timestamp": datetime.now(),
                        "details": f"Zeiteintrag für {employee} am {checkin['date']} geändert: {', '.join(changes)}"
                    })
                    
                    # Benachrichtigung an Mitarbeiter (simuliert)
                    st.info(f"Benachrichtigung an {employee} wurde gesendet.")
    
    # Funktion zur Anzeige des Audit-Trails
    def show_audit_trail():
        """
        Zeigt den Audit-Trail für Änderungen an
        """
        st.title("Audit-Trail")
        
        # Nur für Admins zugänglich
        if not st.session_state.get("is_admin", False):
            st.error("Sie haben keine Berechtigung für diese Seite.")
            return
        
        # Prüfen, ob Audit-Trail existiert
        if "audit_trail" not in st.session_state or not st.session_state["audit_trail"]:
            st.info("Keine Audit-Trail-Einträge vorhanden.")
            return
        
        # Filteroptionen
        col1, col2 = st.columns(2)
        with col1:
            filter_action = st.selectbox(
                "Aktion",
                ["Alle", "create", "update", "delete"],
                key="audit_filter_action"
            )
        with col2:
            filter_entity = st.selectbox(
                "Entität",
                ["Alle", "checkin", "employee", "sick_leave", "vacation"],
                key="audit_filter_entity"
            )
        
        # Zeitraum
        col1, col2 = st.columns(2)
        with col1:
            start_date = st.date_input(
                "Von", 
                value=datetime.now().date() - timedelta(days=30),
                key="audit_start_date"
            )
        with col2:
            end_date = st.date_input(
                "Bis", 
                value=datetime.now().date(),
                key="audit_end_date"
            )
        
        # Audit-Trail filtern
        filtered_trail = st.session_state["audit_trail"]
        
        if filter_action != "Alle":
            filtered_trail = [entry for entry in filtered_trail if entry["action"] == filter_action]
        
        if filter_entity != "Alle":
            filtered_trail = [entry for entry in filtered_trail if entry["entity"] == filter_entity]
        
        # Nach Zeitraum filtern
        start_datetime = datetime.combine(start_date, datetime.min.time())
        end_datetime = datetime.combine(end_date, datetime.max.time())
        
        filtered_trail = [
            entry for entry in filtered_trail 
            if start_datetime <= entry["timestamp"] <= end_datetime
        ]
        
        # Nach Zeitstempel sortieren (neueste zuerst)
        filtered_trail.sort(key=lambda x: x["timestamp"], reverse=True)
        
        # Audit-Trail anzeigen
        if not filtered_trail:
            st.info("Keine Einträge für die ausgewählten Filter gefunden.")
            return
        
        st.subheader(f"Audit-Trail ({len(filtered_trail)} Einträge)")
        
        for entry in filtered_trail:
            with st.expander(f"{entry['timestamp']} - {entry['action']} {entry['entity']}"):
                st.text(f"Benutzer: {entry['user']}")
                st.text(f"Aktion: {entry['action']}")
                st.text(f"Entität: {entry['entity']} (ID: {entry['entity_id']})")
                st.text(f"Zeitpunkt: {entry['timestamp']}")
                st.text(f"Details: {entry['details']}")
    
    # Rückgabe der Funktionen für die Integration
    return {
        "show_time_correction_page": show_time_correction_page,
        "show_audit_trail": show_audit_trail
    }

# Hauptfunktion zur Integration aller Verbesserungen
def integrate_time_tracking_improvements(app):
    """
    Integriert alle Zeiterfassungsverbesserungen in die App
    """
    # Flexible Arbeitszeiten implementieren
    flexible_work_times = implement_flexible_work_times()
    
    # Automatische Pausenregelung implementieren
    automatic_breaks = implement_automatic_breaks()
    
    # Admin-Korrekturmöglichkeiten implementieren
    admin_corrections = implement_admin_corrections()
    
    # Funktionen in die App integrieren
    # (Hier würde die tatsächliche Integration in die App erfolgen)
    
    # Beispiel für die Integration in die Hauptapp
    def extended_main():
        # Initialisierung der Session-State-Erweiterungen
        if "audit_trail" not in st.session_state:
            st.session_state["audit_trail"] = []
        
        # Arbeitszeitmodelle zum Mitarbeiterprofil hinzufügen
        flexible_work_times["extend_employee_profile"]()
        
        # Seitenauswahl erweitern
        if st.session_state.get("is_admin", False):
            # Admin-Seiten
            if page == "Arbeitszeiten korrigieren":
                admin_corrections["show_time_correction_page"]()
            elif page == "Audit-Trail":
                admin_corrections["show_audit_trail"]()
            # ... andere Seiten
        
        # Bestehende Seiten erweitern
        if page == "Check-in/Check-out":
            # Angepasste Check-in-Seite mit flexiblen Arbeitszeiten
            flexible_work_times["adapt_checkin_logic"]()
        elif page == "Mein Profil":
            # Arbeitszeitmodell-Auswahl zum Profil hinzufügen
            flexible_work_times["add_work_time_model_selection_to_profile"]()
        # ... andere Seiten
    
    # Rückgabe der erweiterten App-Funktionalität
    return {
        "extended_main": extended_main,
        "flexible_work_times": flexible_work_times,
        "automatic_breaks": automatic_breaks,
        "admin_corrections": admin_corrections
    }
