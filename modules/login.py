import streamlit as st
import bcrypt
import json
import os
from datetime import datetime, timedelta
import uuid
import re
from modules.navigation import set_page

# (Die restlichen Imports und globalen Variablen bleiben gleich)

def reset_registration_form():
    st.session_state.reg_name = ""
    st.session_state.reg_email = ""
    st.session_state.reg_username = ""
    st.session_state.reg_password = ""
    st.session_state.reg_confirm_password = ""
    st.session_state.reg_location = "Werner Siemens Strasse 107" # Setze einen Standardwert, falls gewünscht
    st.session_state.reg_team = ""
    st.session_state.reg_phone = ""
    st.session_state.terms_agreed = False

def show_login():
    """Zeigt die Login-Seite an."""
    # (Der Code für das Initialisieren der Datenverzeichnisse und das Anzeigen des Logos bleibt gleich)

    st.title("🔐 Anmeldung & Registrierung")

    # (Der CSS-Code bleibt gleich)

    # Tabs für Login und Registrierung
    login_tab, register_tab = st.tabs(["Anmelden", "Registrieren"])

    with login_tab:
        with st.container():
            st.markdown('<div class="login-container">', unsafe_allow_html=True)

            st.subheader("Anmelden")
            username = st.text_input("Benutzername", key="login_username")
            password = st.text_input("Passwort", type="password", key="login_password")

            login_attempts = get_login_attempts(username)

            if login_attempts.get("lockout_until"):
                lockout_until = datetime.fromisoformat(login_attempts["lockout_until"])
                if datetime.now() < lockout_until:
                    remaining_time = lockout_until - datetime.now()
                    minutes = remaining_time.seconds // 60
                    seconds = remaining_time.seconds % 60
                    st.error(f"Konto gesperrt. Bitte versuchen Sie es in {minutes} Minuten und {seconds} Sekunden erneut.")
                    if st.button("Anmeldeversuche zurücksetzen"):
                        if reset_login_attempts(username):
                            st.success("Anmeldeversuche wurden zurückgesetzt. Sie können es jetzt erneut versuchen.")
                            st.rerun()

            col1, col2 = st.columns([1, 1])
            with col1:
                login_button = st.button("Anmelden", key="login_button", use_container_width=True)

            with col2:
                demo_button = st.button("Demo-Zugang", key="demo_button", use_container_width=True)

            if login_button:
                if not username or not password:
                    st.error("Bitte geben Sie Benutzername und Passwort ein.")
                else:
                    employees = load_employees()
                    user = next((emp for emp in employees if emp.get("username") == username), None)

                    if user and verify_password(password, user["password"]):
                        # Erfolgreiche Anmeldung
                        update_login_attempts(username, success=True)

                        st.session_state.user = {
                            "id": user["id"],
                            "name": user["name"],
                            "role": user["role"],
                            "location": user.get("location", "Home Office")
                        }
                        st.success("Anmeldung erfolgreich!")
                        set_page("Home")
                    else:
                        # Fehlgeschlagene Anmeldung
                        update_login_attempts(username)
                        st.error("Ungültige Anmeldedaten.")

                        login_attempts = get_login_attempts(username)
                        if login_attempts["attempts"] >= MAX_LOGIN_ATTEMPTS:
                            st.warning("Zu viele fehlgeschlagene Anmeldeversuche. Konto wurde gesperrt.")
                            if st.button("Anmeldeversuche zurücksetzen"):
                                if reset_login_attempts(username):
                                    st.success("Anmeldeversuche wurden zurückgesetzt. Sie können es jetzt erneut versuchen.")
                                    st.rerun()

            if demo_button:
                # Demo-Zugang für einfachen Zugriff
                st.session_state.user = {
                    "id": "demo_user",
                    "name": "Demo Benutzer",
                    "role": "Admin",
                    "location": "Home Office"
                }
                st.success("Demo-Zugang aktiviert!")
                set_page("Home")

            st.markdown('</div>', unsafe_allow_html=True)

    with register_tab:
        with st.container():
            st.markdown('<div class="login-container">', unsafe_allow_html=True)

            st.subheader("Neues Konto erstellen")

            # Persönliche Informationen
            st.markdown("##### Persönliche Informationen")
            col1, col2 = st.columns(2)

            with col1:
                reg_name = st.text_input("Vollständiger Name *", key="reg_name")

            with col2:
                reg_email = st.text_input("E-Mail *", key="reg_email")

            # Anmeldeinformationen
            st.markdown("##### Anmeldeinformationen")
            col1, col2 = st.columns(2)

            with col1:
                reg_username = st.text_input("Benutzername *", key="reg_username")

            with col2:
                reg_password = st.text_input("Passwort *", type="password", key="reg_password")

            reg_confirm_password = st.text_input("Passwort bestätigen *", type="password", key="reg_confirm_password")

            # Arbeitsinformationen
            st.markdown("##### Arbeitsinformationen")
            col1, col2 = st.columns(2)

            with col1:
                reg_location = st.selectbox(
                    "Standort *",
                    ["Werner Siemens Strasse 107", "Werner Siemens Strasse 39", "Home Office"],
                    key="reg_location"
                )

            with col2:
                reg_team = st.text_input("Team", key="reg_team")

            reg_phone = st.text_input("Telefonnummer", key="reg_phone")

            # Datenschutz und Nutzungsbedingungen
            st.markdown("##### Zustimmung")
            terms_agreed = st.checkbox("Ich stimme den Datenschutzbestimmungen und Nutzungsbedingungen zu *", key="terms_agreed")

            # Registrierungsbutton
            register_button = st.button("Registrieren", key="register_button", use_container_width=True)

            if register_button:
                # Validierung
                validation_errors = []

                if not reg_name:
                    validation_errors.append("Name ist erforderlich.")

                if not reg_email:
                    validation_errors.append("E-Mail ist erforderlich.")
                elif not re.match(r"[^@]+@[^@]+\.[^@]+", reg_email):
                    validation_errors.append("Bitte geben Sie eine gültige E-Mail-Adresse ein.")

                if not reg_username:
                    validation_errors.append("Benutzername ist erforderlich.")
                elif len(reg_username) < 4:
                    validation_errors.append("Benutzername muss mindestens 4 Zeichen lang sein.")

                if not reg_password:
                    validation_errors.append("Passwort ist erforderlich.")
                elif len(reg_password) < 6:
                    validation_errors.append("Passwort muss mindestens 6 Zeichen lang sein.")

                if reg_password != reg_confirm_password:
                    validation_errors.append("Passwörter stimmen nicht überein.")

                if not terms_agreed:
                    validation_errors.append("Sie müssen den Datenschutzbestimmungen und Nutzungsbedingungen zustimmen.")

                # Überprüfen, ob Benutzername oder E-Mail bereits existiert
                employees = load_employees()
                if any(emp.get("username") == st.session_state.reg_username for emp in employees):
                    validation_errors.append("Dieser Benutzername ist bereits vergeben.")

                if any(emp.get("email") == st.session_state.reg_email for emp in employees):
                    validation_errors.append("Diese E-Mail-Adresse ist bereits registriert.")

                if validation_errors:
                    for error in validation_errors:
                        st.error(error)
                else:
                    # Neuen Benutzer erstellen
                    new_user = {
                        "id": str(uuid.uuid4()),
                        "name": st.session_state.reg_name,
                        "email": st.session_state.reg_email,
                        "username": st.session_state.reg_username,
                        "password": hash_password(st.session_state.reg_password),
                        "role": "Mitarbeiter",  # Standardrolle
                        "location": st.session_state.reg_location,
                        "team": st.session_state.reg_team,
                        "phone": st.session_state.reg_phone,
                        "created_at": datetime.now().isoformat()
                    }

                    employees.append(new_user)
                    if save_employees(employees):
                        st.success("Registrierung erfolgreich! Sie können sich jetzt anmelden.")
                        st.button("Registrierungsformular zurücksetzen", on_click=reset_registration_form)
                    else:
                        st.error("Fehler beim Speichern der Registrierung. Bitte versuchen Sie es später erneut.")

            st.markdown('</div>', unsafe_allow_html=True)

# (Der Aufruf von show_login() im Hauptskript bleibt wahrscheinlich gleich)