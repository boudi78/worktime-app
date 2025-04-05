import streamlit as st

def set_page(page_name):
    """
    Verbesserte Navigationsfunktion, die die Seite wechselt und automatisch ein Rerun auslöst.
    
    Args:
        page_name (str): Name der Zielseite
    """
    st.session_state.current_page = page_name
    # Automatisches Rerun nach Seitenwechsel, um doppeltes Klicken zu vermeiden
    st.rerun()
