import streamlit as st
from supabase import create_client
st.write(st.secrets)  # This will display the contents of your secrets in the app


# Supabase-Client initialisieren
def init_supabase():
    try:
        url = st.secrets["connections"]["supabase"]["url"]
        key = st.secrets["connections"]["supabase"]["key"]
        return create_client(url, key)
    except Exception as e:
        st.error(f"Fehler bei der Verbindung zu Supabase: {str(e)}")
        return None

# Benutzer aus Supabase laden
def load_employees_from_supabase():
    supabase = init_supabase()
    if not supabase:
        return []
    
    try:
        response = supabase.table("employees").select("*").execute()
        return response.data
    except Exception as e:
        st.error(f"Fehler beim Laden der Mitarbeiter: {str(e)}")
        return []

# Benutzer in Supabase speichern
def save_employees_to_supabase(employees):
    supabase = init_supabase()
    if not supabase:
        return False
    
    try:
        # Lösche alle vorhandenen Einträge
        supabase.table("employees").delete().neq("id", 0).execute()
        
        # Füge neue Einträge hinzu
        for employee in employees:
            supabase.table("employees").insert(employee).execute()
        return True
    except Exception as e:
        st.error(f"Fehler beim Speichern der Mitarbeiter: {str(e)}")
        return False

# Benutzeranmeldung mit Supabase
def login_user(username, password):
    supabase = init_supabase()
    if not supabase:
        return None
    
    try:
        # Suche nach dem Benutzer in der employees-Tabelle
        response = supabase.table("employees").select("*").eq("username", username).execute()
        users = response.data
        
        if users and len(users) > 0:
            user = users[0]
            if user["password"] == password:  # In Produktion solltest du Passwörter hashen!
                return user
        return None
    except Exception as e:
        st.error(f"Login-Fehler: {str(e)}")
        return None
