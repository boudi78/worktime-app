import streamlit as st
from data_persistence import save_all_data

def delete_employee(employee_id):
    """
    Löscht einen Mitarbeiter aus der Liste der Mitarbeiter
    
    Args:
        employee_id: ID des zu löschenden Mitarbeiters
    
    Returns:
        True, wenn der Mitarbeiter erfolgreich gelöscht wurde, sonst False
    """
    if "employees" not in st.session_state:
        return False
    
    # Mitarbeiter finden und löschen
    for i, employee in enumerate(st.session_state["employees"]):
        if employee["id"] == employee_id:
            # Mitarbeiter aus der Liste entfernen
            st.session_state["employees"].pop(i)
            
            # Daten speichern
            save_all_data(st.session_state["employees"])
            
            return True
    
    return False

def show_employees_page():
    """
    Zeigt die Mitarbeiterseite an
    """
    st.title("Mitarbeiterverwaltung")
    
    # Prüfen, ob der Benutzer Admin ist
    if not st.session_state.get("is_admin", False):
        st.warning("Sie haben keine Berechtigung, diese Seite zu sehen.")
        return
    
    # Mitarbeiterdaten laden
    if "employees" not in st.session_state:
        st.error("Keine Mitarbeiterdaten gefunden!")
        return
    
    # Mitarbeiterliste anzeigen
    st.subheader("Mitarbeiterliste")
    
    for employee in st.session_state["employees"]:
        with st.expander(f"{employee['name']} ({employee['username']})"):
            st.write(f"ID: {employee['id']}")
            st.write(f"Status: {employee['status']}")
            st.write(f"Admin: {'Ja' if employee.get('is_admin', False) else 'Nein'}")
            
            # Löschen-Button
            if employee["id"] != st.session_state.get("user_id"):
                if st.button(f"Mitarbeiter löschen", key=f"delete_{employee['id']}"):
                    # Bestätigungsdialog
                    st.warning(f"Möchten Sie den Mitarbeiter {employee['name']} wirklich löschen?")
                    
                    col1, col2 = st.columns(2)
                    with col1:
                        if st.button("Ja, löschen", key=f"confirm_delete_{employee['id']}"):
                            if delete_employee(employee["id"]):
                                st.success(f"Mitarbeiter {employee['name']} wurde erfolgreich gelöscht!")
                                st.experimental_rerun()
                            else:
                                st.error("Fehler beim Löschen des Mitarbeiters!")
                    with col2:
                        if st.button("Abbrechen", key=f"cancel_delete_{employee['id']}"):
                            st.experimental_rerun()
            else:
                st.info("Sie können Ihren eigenen Account nicht löschen.")
