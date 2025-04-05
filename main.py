import streamlit as st
from modules.navigation import set_page
from modules.responsive import make_app_responsive, add_responsive_meta_tags
from modules.notifications import show_notifications

def show_main_page():
    # Füge Meta-Tags für responsives Design hinzu
    add_responsive_meta_tags()
    
    # Prüfe, ob Benutzer angemeldet ist
    if "user" not in st.session_state:
        from modules.login import show_login
        show_login()
        return
    
    # Mache die App responsive
    make_app_responsive()
    
    # Zeige die aktuelle Seite an
    current_page = st.session_state.get("current_page", "Home")
    
    if current_page == "Home":
        from modules.home_page import show_home_page
        show_home_page()
    elif current_page == "Check-in/Check-out":
        from modules.checkin_page import show_checkin_checkout
        show_checkin_checkout()
    elif current_page == "Calendar":
        from modules.calendar import show_calendar
        show_calendar()
    elif current_page == "Stats":
        from modules.stats import show_stats
        show_stats()
    elif current_page == "Vacation":
        from modules.vacation import display_vacation_page
        display_vacation_page()
    elif current_page == "Sick Leave":
        from modules.sick_leave import show_sick_leave
        show_sick_leave()
    elif current_page == "Notifications":
        show_notifications()
    elif current_page == "Change Password":
        from modules.login import show_change_password
        show_change_password()
    elif current_page == "Admin":
        from modules.admin_page import show
        show()
    elif current_page == "Logout":
        st.session_state.pop("user", None)
        st.session_state.pop("current_page", None)
        st.success("Erfolgreich abgemeldet!")
        st.rerun()
    else:
        st.error(f"Die Seite '{current_page}' ist nicht implementiert.")
        set_page("Home")
