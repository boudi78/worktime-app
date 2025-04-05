import streamlit as st
import bcrypt
import json
import os
from datetime import datetime, timedelta
import uuid
import re
from modules.navigation import set_page

# Dateipfade
DATA_DIR = "data"
EMPLOYEES_FILE = os.path.join(DATA_DIR, "employees.json")
LOGIN_ATTEMPTS_FILE = os.path.join(DATA_DIR, "login_attempts.json")

# Konstanten
MAX_LOGIN_ATTEMPTS = 5
LOCKOUT_DURATION = timedelta(minutes=15)

# Hilfsfunktionen
def load_employees():
    """Lädt Mitarbeiterdaten aus der JSON-Datei."""
    if os.path.exists(EMPLOYEES_FILE):
        try:
            with open(EMPLOYEES_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Warnung: Konnte JSON aus {EMPLOYEES_FILE} nicht dekodieren. Gebe leere Liste zurück.")
            return []
    else:
        # Erstelle Verzeichnis, falls es nicht existiert
        os.makedirs(os.path.dirname(EMPLOYEES_FILE), exist_ok=True)
        # Erstelle leere Datei
        with open(EMPLOYEES_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)
        return []

def save_employees(employees):
    """Speichert Mitarbeiterdaten in der JSON-Datei."""
    os.makedirs(os.path.dirname(EMPLOYEES_FILE), exist_ok=True)
    with open(EMPLOYEES_FILE, "w", encoding="utf-8") as f:
        json.dump(employees, f, indent=4, ensure_ascii=False)

def hash_password(password):
    """Hasht ein Passwort mit bcrypt."""
    hashed = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())
    return hashed.decode('utf-8')

def verify_password(password, hashed_password):
    """Überprüft, ob ein Passwort mit dem gespeicherten Hash übereinstimmt."""
    hashed_bytes = hashed_password.encode('utf-8')
    password_bytes = password.encode('utf-8')
    return bcrypt.checkpw(password_bytes, hashed_bytes)

def get_login_attempts(username):
    """Lädt die Anmeldeversuche für einen Benutzer."""
    if os.path.exists(LOGIN_ATTEMPTS_FILE):
        try:
            with open(LOGIN_ATTEMPTS_FILE, "r", encoding="utf-8") as f:
                attempts = json.load(f)
                return attempts.get(username, {"attempts": 0, "lockout_until": None})
        except json.JSONDecodeError:
            return {"attempts": 0, "lockout_until": None}
    return {"attempts": 0, "lockout_until": None}

def update_login_attempts(username, success=False):
    """Aktualisiert die Anmeldeversuche für einen Benutzer."""
    if os.path.exists(LOGIN_ATTEMPTS_FILE):
        try:
            with open(LOGIN_ATTEMPTS_FILE, "r", encoding="utf-8") as f:
                attempts = json.load(f)
        except json.JSONDecodeError:
            attempts = {}
    else:
        attempts = {}
    
    user_attempts = attempts.get(username, {"attempts": 0, "lockout_until": None})
    now = datetime.now()
    
    if user_attempts["lockout_until"] and now < datetime.fromisoformat(user_attempts["lockout_until"]):
        # Noch gesperrt
        return
    
    if success:
        # Zurücksetzen bei erfolgreicher Anmeldung
        user_attempts["attempts"] = 0
        user_attempts["lockout_until"] = None
    else:
        # Erhöhen der Versuche
        user_attempts["attempts"] += 1
        if user_attempts["attempts"] >= MAX_LOGIN_ATTEMPTS:
            user_attempts["lockout_until"] = (now + LOCKOUT_DURATION).isoformat()
    
    attempts[username] = user_attempts
    os.makedirs(os.path.dirname(LOGIN_ATTEMPTS_FILE), exist_ok=True)
    with open(LOGIN_ATTEMPTS_FILE, "w", encoding="utf-8") as f:
        json.dump(attempts, f, indent=4, ensure_ascii=False)

def show_login():
    """Zeigt die Login-Seite an."""
    # Logo und Firmenname anzeigen
    col1, col2 = st.columns([1, 3])
    with col1:
        st.image("grafik.png", width=100)
    with col2:
        st.title("Team-sped Seehafenspedition GmbH")
    
    st.title("🔐 Anmeldung & Registrierung")
    
    # CSS für Login-Seite
    st.markdown("""
    <style>
    .login-container {
        max-width: 500px;
        margin: 0 auto;
        padding: 20px;
        border-radius: 10px;
        background-color: #f8f9fa;
        box-shadow: 0 4px 6px rgba(0, 0, 0, 0.1);
    }
    .stTabs [data-baseweb="tab-list"] {
        gap: 24px;
    }
    .stTabs [data-baseweb="tab"] {
        height: 50px;
        white-space: pre-wrap;
        border-radius: 4px 4px 0 0;
        font-weight: 500;
    }
    </style>
    """, unsafe_allow_html=True)
    
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
                if any(emp.get("username") == reg_username for emp in employees):
                    validation_errors.append("Dieser Benutzername ist bereits vergeben.")
                
                if any(emp.get("email") == reg_email for emp in employees):
                    validation_errors.append("Diese E-Mail-Adresse ist bereits registriert.")
                
                if validation_errors:
                    for error in validation_errors:
                        st.error(error)
                else:
                    # Neuen Benutzer erstellen
                    new_user = {
                        "id": str(uuid.uuid4()),
                        "name": reg_name,
                        "email": reg_email,
                        "username": reg_username,
                        "password": hash_password(reg_password),
                        "role": "Mitarbeiter",  # Standardrolle
                        "location": reg_location,
                        "team": reg_team,
                        "phone": reg_phone,
                        "created_at": datetime.now().isoformat()
                    }
                    
                    employees.append(new_user)
                    save_employees(employees)
                    
                    st.success("Registrierung erfolgreich! Sie können sich jetzt anmelden.")
                    
                    # Felder zurücksetzen
                    st.session_state.reg_name = ""
                    st.session_state.reg_email = ""
                    st.session_state.reg_username = ""
                    st.session_state.reg_password = ""
                    st.session_state.reg_confirm_password = ""
                    st.session_state.reg_team = ""
                    st.session_state.reg_phone = ""
                    st.session_state.terms_agreed = False
            
            st.markdown('</div>', unsafe_allow_html=True)
