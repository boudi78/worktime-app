import streamlit as st
from modules.home_page import show_home_page
from modules.checkin_page import show_checkin_page
from modules.vacation_request_page import show_vacation_page
from modules.sick_leave_page import show_sick_leave_page
from modules.admin_page import show_admin_page
from modules.calendar_page import show_calendar_page
from modules.work_hours_page import show_statistics_page
from modules.make_admin import make_first_user_admin
from modules.navigation import set_page  # Import the improved navigation function


# -----------------------------
# App Konfiguration
# -----------------------------
st.set_page_config(
    page_title="WorkTime App",
    page_icon="⏱️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# -----------------------------
# Initialisieren (z. B. Daten laden)
# -----------------------------
initialize_app()
make_first_user_admin()

# -----------------------------
# Session State Standardwerte
# -----------------------------
def ensure_session_keys():
    default_values = {
        "page": "Home",
        "user": None,
        "is_admin": False
    }
    for key, value in default_values.items():
        if key not in st.session_state:
            st.session_state[key] = value

ensure_session_keys()

# -----------------------------
# Sidebar Navigation mit Icons
# -----------------------------
def sidebar_navigation():
    menu_items = {
        "Home": "🏠",
        "Checkin": "⏰",
        "Vacation": "🏝️",
        "Stats": "📊",
        "Calendar": "📅",
    }
    
    # Admin-spezifische Menüpunkte
    if st.session_state.is_admin:
        menu_items["Admin"] = "⚙️"
    
    # Erstelle für jeden Menüpunkt einen Button mit Icon
    for page, icon in menu_items.items():
        if st.sidebar.button(f"{icon} {page}"):
            st.session_state.page = page
            st.rerun()  # Automatisches Rerun nach Seitenwechsel
    
    st.sidebar.markdown("---")
    if st.sidebar.button("🚪 Abmelden"):
        st.session_state.user = None
        st.session_state.is_admin = False
        st.session_state.page = "Home"
        st.rerun()

# -----------------------------
# Sidebar Navigation
# -----------------------------
with st.sidebar:
    st.title("WorkTime App")

    if st.session_state.user:
        st.markdown(f"👤 **Angemeldet als:** {st.session_state.user['name']}")
        st.markdown("---")
        
        # Verwende die neue Sidebar-Navigation mit Icons
        sidebar_navigation()
    else:
        st.info("Bitte melde dich an, um fortzufahren.")

# -----------------------------
# Seiteninhalt je nach Auswahl
# -----------------------------
if not st.session_state.user:
    show_home_page()
else:
    if st.session_state.page == "Home":
        show_home_page()
    elif st.session_state.page == "Checkin":
        show_checkin_page()
    elif st.session_state.page == "Vacation":
        show_vacation_page()
    elif st.session_state.page == "Stats":
        show_statistics_page()
    elif st.session_state.page == "Calendar":
        show_calendar_page()
    elif st.session_state.page == "Admin":
        show_admin_page()
