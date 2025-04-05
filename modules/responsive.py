import streamlit as st
from modules.navigation import set_page
import streamlit.components.v1 as components

def create_responsive_sidebar():
    """
    Erstellt eine responsive Sidebar mit Icons, die auf verschiedenen Geräten gut aussieht.
    """
    # CSS für responsive Sidebar
    st.markdown("""
    <style>
    /* Basis-Styling für die Sidebar */
    .sidebar-item {
        display: flex;
        align-items: center;
        padding: 10px;
        margin: 5px 0;
        border-radius: 5px;
        cursor: pointer;
        transition: background-color 0.3s;
    }
    
    .sidebar-item:hover {
        background-color: rgba(255, 255, 255, 0.1);
    }
    
    .sidebar-item.active {
        background-color: rgba(255, 255, 255, 0.2);
        font-weight: bold;
    }
    
    .sidebar-icon {
        margin-right: 10px;
        font-size: 1.2rem;
    }
    
    /* Responsive Anpassungen */
    @media (max-width: 768px) {
        /* Tablet und Smartphone */
        .sidebar-item {
            padding: 12px 8px;
            margin: 3px 0;
        }
        
        .sidebar-text {
            font-size: 0.9rem;
        }
    }
    
    @media (max-width: 576px) {
        /* Kleine Smartphones */
        .sidebar .sidebar-content {
            padding: 5px;
        }
        
        .sidebar-item {
            padding: 10px 5px;
        }
        
        .sidebar-icon {
            margin-right: 5px;
        }
    }
    </style>
    """, unsafe_allow_html=True)
    
    # Prüfe, ob Benutzer angemeldet ist
    if "user" not in st.session_state:
        return
    
    # Importiere Benachrichtigungsfunktionen
    try:
        from modules.notifications import show_notification_badge
        notification_badge = show_notification_badge()
    except ImportError:
        notification_badge = ""
    
    # Aktuelle Seite
    current_page = st.session_state.get("current_page", "Home")
    
    # Benutzerrolle
    user_role = st.session_state.user.get("role", "User")
    
    # Sidebar-Menüpunkte mit Icons
    menu_items = [
        {"icon": "🏠", "text": "Home", "page": "Home"},
        {"icon": "⏱️", "text": "Check-in/Check-out", "page": "Check-in/Check-out"},
        {"icon": "📅", "text": "Kalender", "page": "Calendar"},
        {"icon": "📊", "text": "Statistiken", "page": "Stats"},
        {"icon": "🟡", "text": "Urlaub", "page": "Vacation"},
        {"icon": "🔴", "text": "Krankmeldung", "page": "Sick Leave"},
        {"icon": "🔔", "text": f"Benachrichtigungen{notification_badge}", "page": "Notifications"},
        {"icon": "🔑", "text": "Passwort ändern", "page": "Change Password"},
    ]
    
    # Admin-Menüpunkte
    if user_role == "Admin":
        menu_items.append({"icon": "⚙️", "text": "Admin", "page": "Admin"})
    
    # Logout-Option
    menu_items.append({"icon": "🚪", "text": "Abmelden", "page": "Logout"})
    
    # Sidebar-Menü rendern
    for item in menu_items:
        is_active = current_page == item["page"]
        active_class = "active" if is_active else ""
        
        # HTML für Menüpunkt
        menu_html = f"""
        <div class="sidebar-item {active_class}" onclick="handleClick('{item['page']}')">
            <span class="sidebar-icon">{item['icon']}</span>
            <span class="sidebar-text">{item['text']}</span>
        </div>
        """
        
        # Menüpunkt anzeigen
        st.markdown(menu_html, unsafe_allow_html=True)
    
    # JavaScript für Klick-Handler
    js_code = """
    <script>
    function handleClick(page) {
        // Sende Nachricht an Streamlit
        window.parent.postMessage({
            type: 'streamlit:setComponentValue',
            value: page
        }, '*');
    }
    </script>
    """
    components.html(js_code, height=0)
    
    # Empfange Klick-Events
    selected_page = st.session_state.get("selected_page", None)
    if selected_page and selected_page != current_page:
        set_page(selected_page)
        st.session_state.selected_page = None

def add_responsive_meta_tags():
    """
    Fügt Meta-Tags für responsives Design hinzu.
    """
    meta_tags = """
    <meta name="viewport" content="width=device-width, initial-scale=1.0, maximum-scale=1.0, user-scalable=no">
    <style>
    /* Kalender-Farbcodierung */
    .holiday { color: #FF5733; background-color: #FFF1F1; }
    .vacation { color: #33FF57; background-color: #E6FFEC; }
    .sick { color: #FF5733; background-color: #FFEBE5; }
    .overtime { color: #FFC300; background-color: #FFF5CC; }
    .weekend { color: #8C8C8C; background-color: #F0F0F0; }
    .today { background-color: #2C3E50; color: white; }
    
    /* Allgemeine responsive Anpassungen */
    @media (max-width: 768px) {
        /* Tablet */
        .stButton button {
            width: 100%;
            padding: 0.5rem;
            font-size: 1rem;
        }
        
        .stTextInput input, .stTextArea textarea, .stSelectbox, .stDateInput {
            font-size: 1rem;
        }
        
        h1 {
            font-size: 1.8rem !important;
        }
        
        h2 {
            font-size: 1.5rem !important;
        }
        
        h3 {
            font-size: 1.2rem !important;
        }
    }
    
    @media (max-width: 576px) {
        /* Smartphone */
        .stButton button {
            padding: 0.4rem;
            font-size: 0.9rem;
        }
        
        .stTextInput input, .stTextArea textarea, .stSelectbox, .stDateInput {
            font-size: 0.9rem;
        }
        
        h1 {
            font-size: 1.5rem !important;
        }
        
        h2 {
            font-size: 1.3rem !important;
        }
        
        h3 {
            font-size: 1.1rem !important;
        }
        
        /* Verbesserte Lesbarkeit auf kleinen Bildschirmen */
        p, li, .stMarkdown {
            font-size: 0.9rem !important;
        }
        
        /* Tabellen auf kleinen Bildschirmen */
        .stDataFrame {
            font-size: 0.8rem !important;
        }
    }
    
    /* Touch-freundliche Elemente */
    button, select, input[type="checkbox"], input[type="radio"] {
        min-height: 44px;
        min-width: 44px;
    }
    
    /* Verbesserte Kontraste */
    .stButton button {
        font-weight: bold;
    }
    </style>
    """
    st.markdown(meta_tags, unsafe_allow_html=True)

def make_app_responsive():
    """
    Macht die App responsive für verschiedene Geräte.
    """
    # Meta-Tags hinzufügen
    add_responsive_meta_tags()
    
    # Responsive Sidebar erstellen
    with st.sidebar:
        create_responsive_sidebar()
