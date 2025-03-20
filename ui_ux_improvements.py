# Implementierung der UI/UX-Verbesserungen

# 1. Dashboard mit Diagrammen
def implement_enhanced_dashboard():
    """
    Implementierung eines erweiterten Dashboards mit interaktiven Diagrammen
    """
    def show_enhanced_dashboard():
        """
        Zeigt das erweiterte Dashboard mit interaktiven Diagrammen an
        """
        st.title("Dashboard")
        
        # Zeitraum für Datenanalyse auswählen
        time_period = st.selectbox(
            "Zeitraum",
            ["Heute", "Diese Woche", "Dieser Monat", "Dieses Jahr", "Benutzerdefiniert"],
            key="dashboard_time_period"
        )
        
        # Zeitraum berechnen
        today = datetime.now().date()
        if time_period == "Heute":
            start_date = today
            end_date = today
        elif time_period == "Diese Woche":
            start_date = today - timedelta(days=today.weekday())
            end_date = start_date + timedelta(days=6)
        elif time_period == "Dieser Monat":
            start_date = today.replace(day=1)
            if today.month == 12:
                end_date = today.replace(year=today.year + 1, month=1, day=1) - timedelta(days=1)
            else:
                end_date = today.replace(month=today.month + 1, day=1) - timedelta(days=1)
        elif time_period == "Dieses Jahr":
            start_date = today.replace(month=1, day=1)
            end_date = today.replace(month=12, day=31)
        else:  # Benutzerdefiniert
            col1, col2 = st.columns(2)
            with col1:
                start_date = st.date_input(
                    "Von",
                    value=today - timedelta(days=30),
                    key="dashboard_custom_start"
                )
            with col2:
                end_date = st.date_input(
                    "Bis",
                    value=today,
                    key="dashboard_custom_end"
                )
        
        # Übersichtskarten
        st.subheader("Übersicht")
        
        # Anwesende Mitarbeiter zählen
        present_count = sum(1 for emp in st.session_state["employees"] if emp["status"] == "Anwesend")
        sick_count = sum(1 for emp in st.session_state["employees"] if emp["status"] == "Krank")
        vacation_count = sum(1 for emp in st.session_state["employees"] if emp["status"] == "Urlaub")
        
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            st.metric("Mitarbeiter anwesend", f"{present_count}/{len(st.session_state['employees'])}")
        with col2:
            st.metric("Krankmeldungen", sick_count)
        with col3:
            st.metric("Im Urlaub", vacation_count)
        with col4:
            # Aktive Check-ins heute
            active_checkins = sum(1 for c in st.session_state["checkins"] 
                                 if c.get("date") == today and 
                                 c.get("check_in_time") and not c.get("check_out_time"))
            st.metric("Aktive Check-ins", active_checkins)
        
        # Arbeitszeiten-Analyse
        st.subheader("Arbeitszeiten-Analyse")
        
        # Arbeitszeiten für den ausgewählten Zeitraum abrufen
        checkins = [c for c in st.session_state["checkins"] 
                   if start_date <= c.get("date", today) <= end_date and
                   c.get("status") == "Abgeschlossen"]
        
        if not checkins:
            st.info(f"Keine abgeschlossenen Arbeitszeiten im Zeitraum {start_date} bis {end_date} gefunden.")
        else:
            # Arbeitszeiten nach Mitarbeiter gruppieren
            employee_hours = {}
            for checkin in checkins:
                employee = next((emp["name"] for emp in st.session_state["employees"] if emp["id"] == checkin.get("employee_id")), "Unbekannt")
                
                # Arbeitszeit berechnen
                if checkin.get("check_in_time") and checkin.get("check_out_time"):
                    work_duration = (checkin["check_out_time"] - checkin["check_in_time"]).total_seconds() / 3600
                    break_duration = checkin.get("break_duration", 0)
                    net_duration = work_duration - break_duration
                    
                    if employee in employee_hours:
                        employee_hours[employee] += net_duration
                    else:
                        employee_hours[employee] = net_duration
            
            # Diagramm erstellen
            if employee_hours:
                # Nach Stunden sortieren
                sorted_employees = sorted(employee_hours.items(), key=lambda x: x[1], reverse=True)
                employees = [e[0] for e in sorted_employees]
                hours = [round(e[1], 2) for e in sorted_employees]
                
                fig = px.bar(
                    x=employees,
                    y=hours,
                    title=f"Arbeitsstunden pro Mitarbeiter ({start_date} bis {end_date})",
                    labels={"x": "Mitarbeiter", "y": "Stunden"}
                )
                st.plotly_chart(fig)
            
            # Arbeitszeiten nach Tag gruppieren
            daily_hours = {}
            for checkin in checkins:
                date_str = checkin.get("date").strftime("%Y-%m-%d")
                
                # Arbeitszeit berechnen
                if checkin.get("check_in_time") and checkin.get("check_out_time"):
                    work_duration = (checkin["check_out_time"] - checkin["check_in_time"]).total_seconds() / 3600
                    break_duration = checkin.get("break_duration", 0)
                    net_duration = work_duration - break_duration
                    
                    if date_str in daily_hours:
                        daily_hours[date_str] += net_duration
                    else:
                        daily_hours[date_str] = net_duration
            
            # Diagramm erstellen
            if daily_hours:
                # Nach Datum sortieren
                sorted_days = sorted(daily_hours.items())
                days = [datetime.strptime(d[0], "%Y-%m-%d").strftime("%d.%m") for d in sorted_days]
                hours = [round(d[1], 2) for d in sorted_days]
                
                fig = px.line(
                    x=days,
                    y=hours,
                    title=f"Arbeitsstunden pro Tag ({start_date} bis {end_date})",
                    labels={"x": "Datum", "y": "Stunden"}
                )
                st.plotly_chart(fig)
        
        # Überstunden-Analyse
        st.subheader("Überstunden-Analyse")
        
        # Standardarbeitszeit pro Tag (8 Stunden)
        standard_hours = 8
        
        # Überstunden berechnen
        overtime_data = []
        for employee in st.session_state["employees"]:
            employee_checkins = [c for c in checkins if c.get("employee_id") == employee["id"]]
            
            # Arbeitstage zählen
            workdays = len(set(c.get("date") for c in employee_checkins))
            
            # Gesamtarbeitszeit berechnen
            total_hours = sum(
                (c["check_out_time"] - c["check_in_time"]).total_seconds() / 3600 - c.get("break_duration", 0)
                for c in employee_checkins
                if c.get("check_in_time") and c.get("check_out_time")
            )
            
            # Überstunden berechnen
            expected_hours = workdays * standard_hours
            overtime = total_hours - expected_hours
            
            overtime_data.append({
                "employee": employee["name"],
                "workdays": workdays,
                "total_hours": round(total_hours, 2),
                "expected_hours": expected_hours,
                "overtime": round(overtime, 2)
            })
        
        # Nach Überstunden sortieren
        overtime_data.sort(key=lambda x: x["overtime"], reverse=True)
        
        # Diagramm erstellen
        if overtime_data:
            employees = [d["employee"] for d in overtime_data]
            overtime_hours = [d["overtime"] for d in overtime_data]
            
            fig = px.bar(
                x=employees,
                y=overtime_hours,
                title=f"Überstunden pro Mitarbeiter ({start_date} bis {end_date})",
                labels={"x": "Mitarbeiter", "y": "Überstunden"},
                color=overtime_hours,
                color_continuous_scale=["green", "yellow", "red"]
            )
            st.plotly_chart(fig)
            
            # Detaillierte Überstundentabelle
            st.subheader("Detaillierte Überstundenanalyse")
            
            overtime_df = pd.DataFrame(overtime_data)
            overtime_df.columns = ["Mitarbeiter", "Arbeitstage", "Gesamtstunden", "Sollstunden", "Überstunden"]
            st.dataframe(overtime_df)
        else:
            st.info("Keine Daten für Überstundenanalyse verfügbar.")
        
        # Krankmeldungs- und Urlaubsanalyse
        st.subheader("Abwesenheitsanalyse")
        
        # Tabs für verschiedene Analysen
        tab1, tab2, tab3 = st.tabs(["Krankmeldungen", "Urlaub", "Vergleich"])
        
        with tab1:
            # Krankmeldungen für den ausgewählten Zeitraum abrufen
            sick_leaves = [s for s in st.session_state["sick_leaves"] 
                          if s.get("status") == "Bestätigt" and
                          not (s["end_date"] < start_date or s["start_date"] > end_date)]
            
            if not sick_leaves:
                st.info(f"Keine bestätigten Krankmeldungen im Zeitraum {start_date} bis {end_date} gefunden.")
            else:
                # Krankmeldungen nach Mitarbeiter gruppieren
                employee_sick_days = {}
                for sick_leave in sick_leaves:
                    employee = next((emp["name"] for emp in st.session_state["employees"] if emp["id"] == sick_leave["employee_id"]), "Unbekannt")
                    days = (min(sick_leave["end_date"], end_date) - max(sick_leave["start_date"], start_date)).days + 1
                    
                    if employee in employee_sick_days:
                        employee_sick_days[employee] += days
                    else:
                        employee_sick_days[employee] = days
                
                # Diagramm erstellen
                if employee_sick_days:
                    # Nach Tagen sortieren
                    sorted_employees = sorted(employee_sick_days.items(), key=lambda x: x[1], reverse=True)
                    employees = [e[0] for e in sorted_employees]
                    days = [e[1] for e in sorted_employees]
                    
                    fig = px.bar(
                        x=employees,
                        y=days,
                        title=f"Krankheitstage pro Mitarbeiter ({start_date} bis {end_date})",
                        labels={"x": "Mitarbeiter", "y": "Tage"}
                    )
                    st.plotly_chart(fig)
                
                # Krankmeldungen nach Kategorie gruppieren
                if any("category" in s for s in sick_leaves):
                    category_counts = {}
                    for sick_leave in sick_leaves:
                        category = sick_leave.get("category", "Sonstiges")
                        days = (min(sick_leave["end_date"], end_date) - max(sick_leave["start_date"], start_date)).days + 1
                        
                        if category in category_counts:
                            category_counts[category] += days
                        else:
                            category_counts[category] = days
                    
                    # Diagramm erstellen
                    if category_counts:
                        fig = px.pie(
                            names=list(category_counts.keys()),
                            values=list(category_counts.values()),
                            title=f"Krankheitstage nach Kategorie ({start_date} bis {end_date})"
                        )
                        st.plotly_chart(fig)
        
        with tab2:
            # Urlaubsanträge für den ausgewählten Zeitraum abrufen
            vacation_requests = [v for v in st.session_state["vacation_requests"] 
                                if v.get("status") == "Genehmigt" and
                                not (v["end_date"] < start_date or v["start_date"] > end_date)]
            
            if not vacation_requests:
                st.info(f"Keine genehmigten Urlaubsanträge im Zeitraum {start_date} bis {end_date} gefunden.")
            else:
                # Urlaubstage nach Mitarbeiter gruppieren
                employee_vacation_days = {}
                for vacation in vacation_requests:
                    employee = next((emp["name"] for emp in st.session_state["employees"] if emp["id"] == vacation["employee_id"]), "Unbekannt")
                    days = (min(vacation["end_date"], end_date) - max(vacation["start_date"], start_date)).days + 1
                    
                    if employee in employee_vacation_days:
                        employee_vacation_days[employee] += days
                    else:
                        employee_vacation_days[employee] = days
                
                # Diagramm erstellen
                if employee_vacation_days:
                    # Nach Tagen sortieren
                    sorted_employees = sorted(employee_vacation_days.items(), key=lambda x: x[1], reverse=True)
                    employees = [e[0] for e in sorted_employees]
                    days = [e[1] for e in sorted_employees]
                    
                    fig = px.bar(
                        x=employees,
                        y=days,
                        title=f"Urlaubstage pro Mitarbeiter ({start_date} bis {end_date})",
                        labels={"x": "Mitarbeiter", "y": "Tage"}
                    )
                    st.plotly_chart(fig)
                
                # Urlaubsanträge nach Typ gruppieren
                if any("type" in v for v in vacation_requests):
                    type_counts = {}
                    for vacation in vacation_requests:
                        vacation_type = vacation.get("type", "Erholungsurlaub")
                        days = (min(vacation["end_date"], end_date) - max(vacation["start_date"], start_date)).days + 1
                        
                        if vacation_type in type_counts:
                            type_counts[vacation_type] += days
                        else:
                            type_counts[vacation_type] = days
                    
                    # Diagramm erstellen
                    if type_counts:
                        fig = px.pie(
                            names=list(type_counts.keys()),
                            values=list(type_counts.values()),
                            title=f"Urlaubstage nach Typ ({start_date} bis {end_date})"
                        )
                        st.plotly_chart(fig)
        
        with tab3:
            # Vergleich von Arbeitszeit, Krankmeldungen und Urlaub
            
            # Daten sammeln
            all_employees = set(emp["name"] for emp in st.session_state["employees"])
            
            comparison_data = []
            for employee_name in all_employees:
                employee = next((emp for emp in st.session_state["employees"] if emp["name"] == employee_name), None)
                if not employee:
                    continue
                
                # Arbeitsstunden
                work_hours = sum(
                    (c["check_out_time"] - c["check_in_time"]).total_seconds() / 3600 - c.get("break_duration", 0)
                    for c in checkins
                    if c.get("employee_id") == employee["id"] and c.get("check_in_time") and c.get("check_out_time")
                )
                
                # Krankheitstage
                sick_days = sum(
                    (min(s["end_date"], end_date) - max(s["start_date"], start_date)).days + 1
                    for s in sick_leaves
                    if s.get("employee_id") == employee["id"]
                )
                
                # Urlaubstage
                vacation_days = sum(
                    (min(v["end_date"], end_date) - max(v["start_date"], start_date)).days + 1
                    for v in vacation_requests
                    if v.get("employee_id") == employee["id"]
                )
                
                comparison_data.append({
                    "employee": employee_name,
                    "work_hours": round(work_hours, 2),
                    "sick_days": sick_days,
                    "vacation_days": vacation_days
                })
            
            # Nach Arbeitsstunden sortieren
            comparison_data.sort(key=lambda x: x["work_hours"], reverse=True)
            
            # Diagramm erstellen
            if comparison_data:
                # Daten für Plotly vorbereiten
                employees = [d["employee"] for d in comparison_data]
                work_hours = [d["work_hours"] for d in comparison_data]
                sick_days = [d["sick_days"] for d in comparison_data]
                vacation_days = [d["vacation_days"] for d in comparison_data]
                
                # Gruppiertes Balkendiagramm
                fig = px.bar(
                    x=employees,
                    y=[work_hours, sick_days, vacation_days],
                    title=f"Vergleich: Arbeitsstunden, Krankheits- und Urlaubstage ({start_date} bis {end_date})",
                    labels={"x": "Mitarbeiter", "value": "Stunden/Tage", "variable": "Kategorie"},
                    barmode="group",
                    color_discrete_sequence=["blue", "red", "green"]
                )
                
                # Legendenbeschriftungen anpassen
                fig.update_layout(
                    legend_title_text="Kategorie",
                    legend=dict(
                        orientation="h",
                        yanchor="bottom",
                        y=1.02,
                        xanchor="right",
                        x=1
                    )
                )
                
                # Achsenbeschriftungen anpassen
                fig.update_layout(
                    xaxis_title="Mitarbeiter",
                    yaxis_title="Stunden/Tage"
                )
                
                st.plotly_chart(fig)
                
                # Detaillierte Vergleichstabelle
                st.subheader("Detaillierter Vergleich")
                
                comparison_df = pd.DataFrame(comparison_data)
                comparison_df.columns = ["Mitarbeiter", "Arbeitsstunden", "Krankheitstage", "Urlaubstage"]
                st.dataframe(comparison_df)
            else:
                st.info("Keine Daten für Vergleichsanalyse verfügbar.")
        
        # Anpassbare Dashboard-Widgets
        st.subheader("Dashboard anpassen")
        
        # Widget-Einstellungen
        if "dashboard_widgets" not in st.session_state:
            st.session_state["dashboard_widgets"] = {
                "show_overtime": True,
                "show_sick_leave": True,
                "show_vacation": True,
                "show_comparison": True
            }
        
        # Widget-Einstellungen bearbeiten
        with st.expander("Widget-Einstellungen"):
            col1, col2 = st.columns(2)
            with col1:
                st.session_state["dashboard_widgets"]["show_overtime"] = st.checkbox(
                    "Überstunden anzeigen",
                    value=st.session_state["dashboard_widgets"]["show_overtime"],
                    key="widget_overtime"
                )
                st.session_state["dashboard_widgets"]["show_sick_leave"] = st.checkbox(
                    "Krankmeldungen anzeigen",
                    value=st.session_state["dashboard_widgets"]["show_sick_leave"],
                    key="widget_sick_leave"
                )
            with col2:
                st.session_state["dashboard_widgets"]["show_vacation"] = st.checkbox(
                    "Urlaub anzeigen",
                    value=st.session_state["dashboard_widgets"]["show_vacation"],
                    key="widget_vacation"
                )
                st.session_state["dashboard_widgets"]["show_comparison"] = st.checkbox(
                    "Vergleich anzeigen",
                    value=st.session_state["dashboard_widgets"]["show_comparison"],
                    key="widget_comparison"
                )
            
            if st.button("Dashboard aktualisieren"):
                st.success("Dashboard-Einstellungen wurden aktualisiert.")
                st.rerun()
    
    return {
        "show_enhanced_dashboard": show_enhanced_dashboard
    }

# 2. Dark Mode
def implement_dark_mode():
    """
    Implementierung eines umschaltbaren Dark Mode
    """
    def initialize_theme():
        """
        Initialisiert das Theme in der Session
        """
        if "theme" not in st.session_state:
            # Standardmäßig System-Theme verwenden
            st.session_state["theme"] = "auto"
    
    def show_theme_selector():
        """
        Zeigt den Theme-Selector in der Sidebar an
        """
        st.sidebar.write("### Erscheinungsbild")
        
        theme = st.sidebar.radio(
            "Theme",
            ["Hell", "Dunkel", "System"],
            index=["Hell", "Dunkel", "System"].index(
                "Hell" if st.session_state["theme"] == "light" else
                "Dunkel" if st.session_state["theme"] == "dark" else
                "System"
            ),
            key="theme_selector"
        )
        
        # Theme aktualisieren
        if theme == "Hell" and st.session_state["theme"] != "light":
            st.session_state["theme"] = "light"
            st.rerun()
        elif theme == "Dunkel" and st.session_state["theme"] != "dark":
            st.session_state["theme"] = "dark"
            st.rerun()
        elif theme == "System" and st.session_state["theme"] != "auto":
            st.session_state["theme"] = "auto"
            st.rerun()
    
    def apply_theme():
        """
        Wendet das ausgewählte Theme auf die App an
        """
        # CSS für Light Mode
        light_mode_css = """
        [data-testid="stSidebar"] {
            background-color: #f8f9fa;
        }
        .stApp {
            background-color: white;
            color: #262730;
        }
        .stTabs [data-baseweb="tab-list"] {
            background-color: #f1f3f6;
        }
        .stTabs [data-baseweb="tab"] {
            color: #262730;
        }
        .stTabs [aria-selected="true"] {
            background-color: white;
            color: #0068c9;
        }
        """
        
        # CSS für Dark Mode
        dark_mode_css = """
        [data-testid="stSidebar"] {
            background-color: #262730;
        }
        .stApp {
            background-color: #0e1117;
            color: white;
        }
        .stTabs [data-baseweb="tab-list"] {
            background-color: #1a1c24;
        }
        .stTabs [data-baseweb="tab"] {
            color: white;
        }
        .stTabs [aria-selected="true"] {
            background-color: #0e1117;
            color: #83c9ff;
        }
        """
        
        # System-Theme-Erkennung mit JavaScript
        system_theme_js = """
        <script>
        const prefersDark = window.matchMedia && window.matchMedia('(prefers-color-scheme: dark)').matches;
        const theme = localStorage.getItem('theme') || (prefersDark ? 'dark' : 'light');
        localStorage.setItem('theme', theme);
        document.documentElement.setAttribute('data-theme', theme);
        </script>
        """
        
        # Theme anwenden
        if st.session_state["theme"] == "light":
            st.markdown(f"<style>{light_mode_css}</style>", unsafe_allow_html=True)
        elif st.session_state["theme"] == "dark":
            st.markdown(f"<style>{dark_mode_css}</style>", unsafe_allow_html=True)
        else:  # auto
            st.markdown(system_theme_js, unsafe_allow_html=True)
            st.markdown(
                f"""
                <style>
                @media (prefers-color-scheme: light) {{
                    {light_mode_css}
                }}
                @media (prefers-color-scheme: dark) {{
                    {dark_mode_css}
                }}
                </style>
                """,
                unsafe_allow_html=True
            )
    
    return {
        "initialize_theme": initialize_theme,
        "show_theme_selector": show_theme_selector,
        "apply_theme": apply_theme
    }

# 3. Mobile-optimierte Ansicht
def implement_mobile_optimization():
    """
    Implementierung einer mobile-optimierten Ansicht
    """
    def detect_mobile():
        """
        Erkennt, ob die App auf einem mobilen Gerät aufgerufen wird
        """
        # In einer echten App würde hier eine User-Agent-Erkennung stattfinden
        # Für die Demo simulieren wir das mit einer Checkbox
        if "is_mobile" not in st.session_state:
            st.session_state["is_mobile"] = False
        
        # Nur für Demo-Zwecke: Mobile-Ansicht simulieren
        st.sidebar.write("### Geräteansicht")
        is_mobile = st.sidebar.checkbox(
            "Mobile-Ansicht simulieren",
            value=st.session_state["is_mobile"],
            key="mobile_view_toggle"
        )
        
        if is_mobile != st.session_state["is_mobile"]:
            st.session_state["is_mobile"] = is_mobile
            st.rerun()
        
        return is_mobile
    
    def apply_mobile_optimization():
        """
        Wendet mobile-optimierte Styles auf die App an
        """
        # CSS für mobile Optimierung
        mobile_css = """
        @media (max-width: 768px) {
            .stApp {
                padding: 1rem 0.5rem;
            }
            
            /* Kleinere Überschriften */
            h1 {
                font-size: 1.5rem !important;
            }
            h2 {
                font-size: 1.3rem !important;
            }
            h3 {
                font-size: 1.1rem !important;
            }
            
            /* Kompaktere Widgets */
            .stButton button {
                width: 100%;
                margin: 0.2rem 0;
            }
            
            /* Verbesserte Touch-Ziele */
            .stSelectbox, .stMultiselect {
                min-height: 40px;
            }
            
            /* Bessere Lesbarkeit für Tabellen */
            .dataframe {
                font-size: 0.8rem !important;
            }
        }
        """
        
        # Styles anwenden
        st.markdown(f"<style>{mobile_css}</style>", unsafe_allow_html=True)
    
    def show_mobile_optimized_login():
        """
        Zeigt eine mobile-optimierte Login-Seite an
        """
        st.title("Login")
        
        # Einfaches Layout für mobile Geräte
        login_id = st.text_input("Email oder Benutzername", key="login_id")
        password = st.text_input("Passwort", type="password", key="login_password")
        
        # Volle Breite für den Button
        if st.button("Login", key="login_button", use_container_width=True):
            # Login-Logik hier...
            pass
        
        # Links untereinander statt nebeneinander
        if st.button("Registrieren", key="register_link", use_container_width=True):
            st.session_state["current_page"] = "register"
            st.rerun()
        
        if st.button("Passwort vergessen?", key="forgot_password_link", use_container_width=True):
            st.session_state["current_page"] = "forgot_password"
            st.rerun()
    
    def show_mobile_optimized_dashboard():
        """
        Zeigt ein mobile-optimiertes Dashboard an
        """
        st.title("Dashboard")
        
        # Übersichtskarten untereinander statt nebeneinander
        present_count = sum(1 for emp in st.session_state["employees"] if emp["status"] == "Anwesend")
        sick_count = sum(1 for emp in st.session_state["employees"] if emp["status"] == "Krank")
        vacation_count = sum(1 for emp in st.session_state["employees"] if emp["status"] == "Urlaub")
        
        st.metric("Mitarbeiter anwesend", f"{present_count}/{len(st.session_state['employees'])}")
        st.metric("Krankmeldungen", sick_count)
        st.metric("Im Urlaub", vacation_count)
        
        # Aktuelle Anwesenheit
        st.subheader("Aktuelle Anwesenheit")
        
        # Kompakte Darstellung der anwesenden Mitarbeiter
        present_employees = [emp for emp in st.session_state["employees"] if emp["status"] == "Anwesend"]
        if present_employees:
            for emp in present_employees:
                st.write(f"✅ {emp['name']}")
        else:
            st.info("Keine Mitarbeiter anwesend.")
        
        # Kompakte Darstellung der abwesenden Mitarbeiter
        st.subheader("Abwesende Mitarbeiter")
        
        absent_employees = [emp for emp in st.session_state["employees"] if emp["status"] != "Anwesend"]
        if absent_employees:
            for emp in absent_employees:
                icon = "🤒" if emp["status"] == "Krank" else "🏖️" if emp["status"] == "Urlaub" else "❓"
                st.write(f"{icon} {emp['name']} ({emp['status']})")
        else:
            st.info("Keine Mitarbeiter abwesend.")
        
        # Schnellzugriff-Buttons
        st.subheader("Schnellzugriff")
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Check-in", use_container_width=True):
                st.session_state["current_page"] = "checkin"
                st.rerun()
        with col2:
            if st.button("Arbeitszeiten", use_container_width=True):
                st.session_state["current_page"] = "worktimes"
                st.rerun()
        
        col1, col2 = st.columns(2)
        with col1:
            if st.button("Krankmeldung", use_container_width=True):
                st.session_state["current_page"] = "sick_leave"
                st.rerun()
        with col2:
            if st.button("Urlaub", use_container_width=True):
                st.session_state["current_page"] = "vacation"
                st.rerun()
    
    def show_mobile_optimized_checkin():
        """
        Zeigt eine mobile-optimierte Check-in-Seite an
        """
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
        today = datetime.now().date()
        today_checkin = next((c for c in st.session_state["checkins"] 
                             if c["employee_id"] == employee_id and c["date"] == today), None)
        
        # Status-Anzeige
        if today_checkin:
            if "check_out_time" in today_checkin and today_checkin["check_out_time"]:
                st.success(f"✅ Check-out um {today_checkin['check_out_time'].strftime('%H:%M')} Uhr")
                
                # Arbeitszeit berechnen
                work_duration = (today_checkin["check_out_time"] - today_checkin["check_in_time"]).total_seconds() / 3600
                break_duration = today_checkin.get("break_duration", 0)
                net_duration = work_duration - break_duration
                
                st.info(f"Arbeitszeit heute: {net_duration:.2f} Stunden (inkl. {break_duration:.2f} Std. Pause)")
                
                # Neuer Check-in für denselben Tag
                if st.button("Neuer Check-in", use_container_width=True):
                    # Neuen Check-in erstellen
                    new_checkin = {
                        "id": len(st.session_state["checkins"]) + 1,
                        "employee_id": employee_id,
                        "date": today,
                        "check_in_time": datetime.now(),
                        "status": "In Bearbeitung"
                    }
                    st.session_state["checkins"].append(new_checkin)
                    st.success(f"Check-in um {new_checkin['check_in_time'].strftime('%H:%M')} Uhr erfolgreich!")
                    st.rerun()
            else:
                st.info(f"✅ Check-in um {today_checkin['check_in_time'].strftime('%H:%M')} Uhr")
                
                # Check-out Button
                if st.button("Check-out", use_container_width=True):
                    today_checkin["check_out_time"] = datetime.now()
                    today_checkin["status"] = "Abgeschlossen"
                    
                    # Automatische Pausenberechnung
                    work_duration = (today_checkin["check_out_time"] - today_checkin["check_in_time"]).total_seconds() / 3600
                    
                    if work_duration > 9:
                        today_checkin["break_duration"] = 1.0  # 60 Minuten Pause
                    elif work_duration > 6:
                        today_checkin["break_duration"] = 0.5  # 30 Minuten Pause
                    elif work_duration > 4:
                        today_checkin["break_duration"] = 0.25  # 15 Minuten Pause
                    else:
                        today_checkin["break_duration"] = 0.0  # Keine Pause
                    
                    st.success(f"Check-out um {today_checkin['check_out_time'].strftime('%H:%M')} Uhr erfolgreich!")
                    st.rerun()
        else:
            st.warning("Heute noch kein Check-in.")
            
            # Check-in Button
            if st.button("Check-in", use_container_width=True):
                new_checkin = {
                    "id": len(st.session_state["checkins"]) + 1,
                    "employee_id": employee_id,
                    "date": today,
                    "check_in_time": datetime.now(),
                    "status": "In Bearbeitung"
                }
                st.session_state["checkins"].append(new_checkin)
                st.success(f"Check-in um {new_checkin['check_in_time'].strftime('%H:%M')} Uhr erfolgreich!")
                st.rerun()
        
        # Letzte Check-ins anzeigen
        st.subheader("Letzte Check-ins")
        
        recent_checkins = [c for c in st.session_state["checkins"] 
                          if c["employee_id"] == employee_id and c["date"] != today]
        recent_checkins.sort(key=lambda x: x["date"], reverse=True)
        
        if recent_checkins:
            for i, checkin in enumerate(recent_checkins[:5]):  # Nur die letzten 5 anzeigen
                with st.expander(f"{checkin['date']} - {checkin.get('status', 'Offen')}"):
                    st.write(f"**Datum:** {checkin['date']}")
                    
                    if "check_in_time" in checkin:
                        st.write(f"**Check-in:** {checkin['check_in_time'].strftime('%H:%M')} Uhr")
                    
                    if "check_out_time" in checkin:
                        st.write(f"**Check-out:** {checkin['check_out_time'].strftime('%H:%M')} Uhr")
                    
                    if "check_in_time" in checkin and "check_out_time" in checkin:
                        work_duration = (checkin["check_out_time"] - checkin["check_in_time"]).total_seconds() / 3600
                        break_duration = checkin.get("break_duration", 0)
                        net_duration = work_duration - break_duration
                        st.write(f"**Arbeitszeit:** {net_duration:.2f} Stunden (inkl. {break_duration:.2f} Std. Pause)")
        else:
            st.info("Keine früheren Check-ins gefunden.")
    
    def adapt_layout_for_mobile(is_mobile):
        """
        Passt das Layout basierend auf dem Gerätetyp an
        """
        if is_mobile:
            # Mobile-optimierte Ansichten anzeigen
            if not st.session_state.get("logged_in", False):
                if st.session_state.get("current_page") == "login":
                    show_mobile_optimized_login()
                # Weitere Login-bezogene Seiten...
            else:
                # Hauptseiten
                page = st.session_state.get("current_page", "dashboard")
                
                if page == "dashboard":
                    show_mobile_optimized_dashboard()
                elif page == "checkin":
                    show_mobile_optimized_checkin()
                # Weitere Seiten...
            
            return True
        else:
            # Standard-Desktop-Ansicht verwenden
            return False
    
    return {
        "detect_mobile": detect_mobile,
        "apply_mobile_optimization": apply_mobile_optimization,
        "show_mobile_optimized_login": show_mobile_optimized_login,
        "show_mobile_optimized_dashboard": show_mobile_optimized_dashboard,
        "show_mobile_optimized_checkin": show_mobile_optimized_checkin,
        "adapt_layout_for_mobile": adapt_layout_for_mobile
    }

# Hauptfunktion zur Integration aller UI/UX-Verbesserungen
def integrate_ui_ux_improvements(app):
    """
    Integriert alle UI/UX-Verbesserungen in die App
    """
    # Dashboard mit Diagrammen implementieren
    enhanced_dashboard = implement_enhanced_dashboard()
    
    # Dark Mode implementieren
    dark_mode = implement_dark_mode()
    
    # Mobile-optimierte Ansicht implementieren
    mobile_optimization = implement_mobile_optimization()
    
    # Funktionen in die App integrieren
    # (Hier würde die tatsächliche Integration in die App erfolgen)
    
    # Beispiel für die Integration in die Hauptapp
    def extended_main():
        # Theme initialisieren
        dark_mode["initialize_theme"]()
        
        # Theme anwenden
        dark_mode["apply_theme"]()
        
        # Mobile-Optimierung anwenden
        mobile_optimization["apply_mobile_optimization"]()
        
        # Geräteerkennung
        is_mobile = mobile_optimization["detect_mobile"]()
        
        # Theme-Selector in der Sidebar anzeigen
        dark_mode["show_theme_selector"]()
        
        # Layout basierend auf Gerätetyp anpassen
        if mobile_optimization["adapt_layout_for_mobile"](is_mobile):
            # Mobile-Layout wurde angewendet, Funktion hier beenden
            return
        
        # Standard-Desktop-Layout
        if st.session_state.get("current_page") == "dashboard":
            enhanced_dashboard["show_enhanced_dashboard"]()
        # Weitere Seiten...
    
    # Rückgabe der erweiterten App-Funktionalität
    return {
        "extended_main": extended_main,
        "enhanced_dashboard": enhanced_dashboard,
        "dark_mode": dark_mode,
        "mobile_optimization": mobile_optimization
    }
