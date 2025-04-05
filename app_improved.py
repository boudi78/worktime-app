import streamlit as st
import os
import sys
from PIL import Image

# Set page config first - must be the first Streamlit command
st.set_page_config(page_title="Worktime App", page_icon="⏰", layout="wide")

# Get the absolute path to the directory containing app.py
app_dir = os.path.dirname(os.path.abspath(__file__))

# Construct the absolute path to the 'modules' directory
modules_dir = os.path.join(app_dir, 'modules')

# Add the 'modules' directory to sys.path
sys.path.insert(0, modules_dir)

# Import necessary modules
try:
    from modules.login import show_login, show_admin_dashboard, show_change_password
    from modules.utils import logout, calculate_remaining_vacation
    from modules.data_loader import load_employees, save_employees, hash_password, check_password
    from modules.checkin_page import show_checkin_checkout
    from modules.calendar import show_calendar
    from modules.home_page import show_home_page
    from modules.vacation import display_vacation_page
    from modules.sick_leave import show_sick_leave
    from modules.navigation import set_page  # Import the improved navigation function
except ImportError as e:
    st.error(f"Fehler beim Importieren der Module: {e}")
    # Continue with basic functionality

# Initialize session state at the top level
if "initialized" not in st.session_state:
    st.session_state.initialized = True
    st.session_state.user = None
    st.session_state.current_page = "Login"  # Default page

# ----------------------------------------------------------
# Branding Header Function
# ----------------------------------------------------------
def render_branding_header():
    logo_path = os.path.join(os.path.dirname(__file__), "grafik.png")
    cols = st.columns([1, 4])  # links: logo, rechts: text
    with cols[0]:  # Zugriff auf das erste Element der Liste
        if os.path.exists(logo_path):
            logo = Image.open(logo_path)
            st.image(logo, width=80)
        else:
            st.warning("Logo fehlt: " + logo_path)
    with cols[1]:  # Zugriff auf das zweite Element der Liste
        st.markdown("""
        <div style='line-height:1.2'>
            <h2 style='margin-bottom:0;'>Team-sped Seehafenspedition GmbH</h2>
            <p style='font-size:16px; color:gray;'>Effiziente Zeiterfassung für Ihr Logistik-Team</p>
        </div>
        """, unsafe_allow_html=True)

# ----------------------------------------------------------
# Benutzerregistrierungsfunktion
# ----------------------------------------------------------
def register_user(email, password, name, role):
    employees = load_employees()
    # Überprüfe, ob die E-Mail bereits existiert
    if any(employee.get('email') == email for employee in employees):
        st.error("E-Mail-Adresse ist bereits registriert.")
        return None

    # Hash das Passwort und speichere den Benutzer
    hashed_password = hash_password(password)
    new_user = {
        "id": str(len(employees) + 1),  # Einfache ID-Generierung
        "name": name,
        "email": email,
        "password": hashed_password,
        "role": role,
        "username": email.split('@')[0]  # Standardmäßig Username aus E-Mail
    }
    employees.append(new_user)
    save_employees(employees)
    st.success("Benutzer erfolgreich registriert! Bitte loggen Sie sich ein.")
    set_page("Login")  # Verwenden der verbesserten Navigation
    return new_user

# ----------------------------------------------------------
# Sidebar Navigation mit Icons
# ----------------------------------------------------------
def sidebar_navigation():
    menu_items = {
        "Home": "🏠",
        "Check-in/Check-out": "⏰",
        "Calendar": "📅",
        "Stats": "📊",
        "Vacation": "🏝️",
        "Sick Leave": "🤧",
        "Change Password": "🔑",
        "Logout": "🚪",
    }
    
    # Admin-spezifische Menüpunkte
    if st.session_state.user and st.session_state.user['role'] == "Admin":
        menu_items["Admin Dashboard"] = "⚙️"
    
    # Erstelle für jeden Menüpunkt einen Button mit Icon
    for page, icon in menu_items.items():
        if st.sidebar.button(f"{icon} {page}"):
            if page == "Logout":
                logout()
            else:
                set_page(page)

# ----------------------------------------------------------
# Streamlit App Starts Here
# ----------------------------------------------------------

render_branding_header()  # <-- Display Branding

# Sidebar for navigation
with st.sidebar:
    st.title("Worktime App")
    if st.session_state.user:
        st.write(f"Logged in as {st.session_state.user['name']} ({st.session_state.user['role']})")
        # Verwende die neue Sidebar-Navigation mit Icons
        sidebar_navigation()
    else:
        # For non-logged in users, show login/register options
        if st.button("🔐 Registrieren", key="sidebar_register"):
            set_page("Register")

# Main content area
if st.session_state.current_page == "Login":
    show_login()
    # Add an additional registration button in the main area
    st.write("Noch kein Konto?")
    if st.button("🔐 Registrieren", key="main_register"):
        set_page("Register")

elif st.session_state.current_page == "Register":
    st.title("Worktime App - Registrierung")

    name = st.text_input("Vollständiger Name")
    email = st.text_input("E-Mail-Adresse")
    password = st.text_input("Passwort", type="password")
    password_confirm = st.text_input("Passwort bestätigen", type="password")
    role = st.selectbox("Rolle", ["Mitarbeiter", "Admin"])

    if password == password_confirm and password:
        if st.button("Registrieren"):
            register_user(email, password, name, role)
    else:
        if password != password_confirm:
            st.error("Die Passwörter stimmen nicht überein.")
    # Add a back button
    if st.button("Zurück zum Login"):
        set_page("Login")

elif st.session_state.user:
    if st.session_state.current_page == "Home":
        show_home_page()

        # Display Vacation Balance
        user_id = st.session_state.user["id"]
        # Load employee data so we can retrieve `vacation_days_entitled` in `calculate_remaining_vacation` function
        employees = load_employees()
        employee = next((emp for emp in employees if emp["id"] == user_id), None)

        if not employee:
            st.error(f"Mitarbeiter mit ID {user_id} nicht gefunden.")
        else:
            if employee["role"] == "buero":  # Assuming you have "role" field
                vacation_days_entitled = 27
            else:  # Default to "lager" or any other role
                vacation_days_entitled = 26

            remaining_days = calculate_remaining_vacation(user_id)  # CALLING A FUNCTION IN UTILS!
            st.subheader("Urlaubsübersicht")
            st.write(f"Zustehende Urlaubstage: {vacation_days_entitled}")
            st.write(f"Verbleibende Urlaubstage: {remaining_days}")

    elif st.session_state.current_page == "Check-in/Check-out":
        show_checkin_checkout()
    elif st.session_state.current_page == "Calendar":
        show_calendar()
    elif st.session_state.current_page == "Stats":
        try:
            from modules.stats import show_stats
            show_stats()
        except ImportError:
            st.error("Die Seite 'Stats' ist nicht implementiert.")
    elif st.session_state.current_page == "Vacation":
        display_vacation_page()
    elif st.session_state.current_page == "Sick Leave":
        show_sick_leave()
    elif st.session_state.current_page == "Admin Dashboard":
        show_admin_dashboard()
    elif st.session_state.current_page == "Change Password":
        show_change_password()
    else:
        st.write("Page not found.")
else:
    st.write("Please login or register.")
