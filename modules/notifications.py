import streamlit as st
import json
import os
from datetime import datetime

# Datei für Benachrichtigungen
NOTIFICATIONS_FILE = "data/notifications.json"

def initialize_notifications():
    """Initialisiert die Benachrichtigungsdatei, falls sie nicht existiert."""
    if not os.path.exists(NOTIFICATIONS_FILE):
        with open(NOTIFICATIONS_FILE, "w", encoding="utf-8") as f:
            json.dump([], f)

def save_notification(notification):
    """Speichert eine neue Benachrichtigung in der Datei."""
    initialize_notifications()
    
    with open(NOTIFICATIONS_FILE, "r", encoding="utf-8") as f:
        notifications = json.load(f)
    
    # Füge Zeitstempel hinzu
    notification["timestamp"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    notification["read"] = False
    
    notifications.append(notification)
    
    with open(NOTIFICATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(notifications, f, indent=4, ensure_ascii=False)

def load_notifications(user_id=None, admin_only=False):
    """Lädt Benachrichtigungen aus der Datei."""
    initialize_notifications()
    
    with open(NOTIFICATIONS_FILE, "r", encoding="utf-8") as f:
        notifications = json.load(f)
    
    # Filtere nach Benutzer-ID, falls angegeben
    if user_id and not admin_only:
        notifications = [n for n in notifications if n.get("recipient_id") == user_id or n.get("recipient_id") == "all"]
    
    # Filtere nach Admin-Benachrichtigungen, falls angefordert
    if admin_only:
        notifications = [n for n in notifications if n.get("admin_notification", False)]
    
    # Sortiere nach Zeitstempel (neueste zuerst)
    notifications.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
    
    return notifications

def mark_notification_as_read(notification_id):
    """Markiert eine Benachrichtigung als gelesen."""
    initialize_notifications()
    
    with open(NOTIFICATIONS_FILE, "r", encoding="utf-8") as f:
        notifications = json.load(f)
    
    for notification in notifications:
        if notification.get("id") == notification_id:
            notification["read"] = True
            break
    
    with open(NOTIFICATIONS_FILE, "w", encoding="utf-8") as f:
        json.dump(notifications, f, indent=4, ensure_ascii=False)

def create_vacation_notification(employee_name, start_date, end_date, status="eingereicht"):
    """Erstellt eine Benachrichtigung für einen Urlaubsantrag."""
    notification = {
        "id": f"vacation_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "type": "vacation",
        "title": f"Urlaubsantrag {status}",
        "message": f"{employee_name} hat einen Urlaubsantrag vom {start_date} bis {end_date} {status}.",
        "admin_notification": True,
        "recipient_id": "admin"  # Für Admins
    }
    save_notification(notification)

def create_sick_leave_notification(employee_name, start_date, end_date):
    """Erstellt eine Benachrichtigung für eine Krankmeldung."""
    notification = {
        "id": f"sick_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "type": "sick_leave",
        "title": "Neue Krankmeldung",
        "message": f"{employee_name} hat eine Krankmeldung vom {start_date} bis {end_date} eingereicht.",
        "admin_notification": True,
        "recipient_id": "admin"  # Für Admins
    }
    save_notification(notification)

def create_vacation_status_notification(user_id, employee_name, start_date, end_date, status):
    """Erstellt eine Benachrichtigung über den Status eines Urlaubsantrags."""
    status_text = "genehmigt" if status == "approved" else "abgelehnt"
    notification = {
        "id": f"vacation_status_{datetime.now().strftime('%Y%m%d%H%M%S')}",
        "type": "vacation_status",
        "title": f"Urlaubsantrag {status_text}",
        "message": f"Dein Urlaubsantrag vom {start_date} bis {end_date} wurde {status_text}.",
        "admin_notification": False,
        "recipient_id": user_id
    }
    save_notification(notification)

def show_notifications():
    """Zeigt Benachrichtigungen für den aktuellen Benutzer an."""
    st.title("🔔 Benachrichtigungen")
    
    # Prüfe, ob Benutzer angemeldet ist
    if "user" not in st.session_state:
        st.warning("Bitte melde dich an, um deine Benachrichtigungen zu sehen.")
        return
    
    user = st.session_state.user
    user_id = user.get("id")
    is_admin = user.get("role") == "Admin"
    
    # Lade Benachrichtigungen
    if is_admin:
        # Admins sehen ihre eigenen und Admin-Benachrichtigungen
        admin_notifications = load_notifications(admin_only=True)
        user_notifications = load_notifications(user_id=user_id, admin_only=False)
        
        # Tabs für verschiedene Benachrichtigungstypen
        tab1, tab2 = st.tabs(["Admin-Benachrichtigungen", "Meine Benachrichtigungen"])
        
        with tab1:
            display_notification_list(admin_notifications, "Admin")
        
        with tab2:
            display_notification_list(user_notifications, "Benutzer")
    else:
        # Normale Benutzer sehen nur ihre eigenen Benachrichtigungen
        user_notifications = load_notifications(user_id=user_id)
        display_notification_list(user_notifications, "Benutzer")

def display_notification_list(notifications, notification_type):
    """Zeigt eine Liste von Benachrichtigungen an."""
    if not notifications:
        st.info(f"Keine {notification_type}-Benachrichtigungen vorhanden.")
        return
    
    for notification in notifications:
        with st.expander(
            f"{notification.get('title')} - {notification.get('timestamp', 'Unbekannt')}"
            + (" 🆕" if not notification.get("read", False) else "")
        ):
            st.write(notification.get("message", ""))
            
            # Markiere als gelesen, wenn expandiert
            if not notification.get("read", False):
                if st.button("Als gelesen markieren", key=f"read_{notification.get('id')}"):
                    mark_notification_as_read(notification.get("id"))
                    st.rerun()

def show_notification_badge():
    """Zeigt ein Benachrichtigungs-Badge an, wenn ungelesene Benachrichtigungen vorhanden sind."""
    if "user" not in st.session_state:
        return ""
    
    user_id = st.session_state.user.get("id")
    is_admin = st.session_state.user.get("role") == "Admin"
    
    # Lade Benachrichtigungen
    if is_admin:
        admin_notifications = load_notifications(admin_only=True)
        user_notifications = load_notifications(user_id=user_id, admin_only=False)
        notifications = admin_notifications + user_notifications
    else:
        notifications = load_notifications(user_id=user_id)
    
    # Zähle ungelesene Benachrichtigungen
    unread_count = sum(1 for n in notifications if not n.get("read", False))
    
    if unread_count > 0:
        return f" 🔴 {unread_count}"
    return ""
