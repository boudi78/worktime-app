import streamlit as st

def load_global_css():
    """
    Lädt globales CSS für einheitliches Styling der gesamten App
    """
    st.markdown("""
    <style>
    /* Grundlegende Variablen für Farbschema */
    :root {
        --primary-color: #3366cc;
        --primary-color-light: #5588ee;
        --primary-color-dark: #1a4a99;
        --secondary-color: #4CAF50;
        --secondary-color-light: #80c883;
        --secondary-color-dark: #2e7d32;
        --background-color: #ffffff;
        --secondary-background: #f5f7fa;
        --text-color: #333333;
        --light-text: #666666;
        --border-color: #e0e0e0;
        --error-color: #f44336;
        --warning-color: #ff9800;
        --success-color: #4CAF50;
    }

    /* Allgemeine Styles */
    body {
        font-family: 'Arial', sans-serif;
        color: var(--text-color);
        background-color: var(--background-color);
    }

    /* Header Styles */
    h1 {
        color: var(--primary-color);
        font-size: 2.2rem;
        font-weight: 700;
        margin-bottom: 1.5rem;
        padding-bottom: 0.5rem;
        border-bottom: 2px solid var(--primary-color-light);
    }

    h2 {
        color: var(--primary-color);
        font-size: 1.8rem;
        font-weight: 600;
        margin-top: 1.5rem;
        margin-bottom: 1rem;
    }

    h3 {
        color: var(--primary-color-dark);
        font-size: 1.4rem;
        font-weight: 600;
        margin-top: 1.2rem;
        margin-bottom: 0.8rem;
    }

    /* Paragraph Styles */
    p {
        line-height: 1.6;
        margin-bottom: 1rem;
    }

    /* Link Styles */
    a {
        color: var(--primary-color);
        text-decoration: none;
    }

    a:hover {
        color: var(--primary-color-light);
        text-decoration: underline;
    }

    /* Button Styles */
    .stButton > button {
        background-color: var(--primary-color);
        color: white;
        border: none;
        border-radius: 4px;
        padding: 0.5rem 1rem;
        font-weight: 600;
        transition: all 0.3s ease;
    }

    .stButton > button:hover {
        background-color: var(--primary-color-light);
        box-shadow: 0 2px 5px rgba(0,0,0,0.2);
    }

    /* Success Button */
    .success-button > button {
        background-color: var(--success-color);
    }

    .success-button > button:hover {
        background-color: var(--secondary-color-light);
    }

    /* Warning Button */
    .warning-button > button {
        background-color: var(--warning-color);
    }

    .warning-button > button:hover {
        background-color: #ffb74d;
    }

    /* Danger Button */
    .danger-button > button {
        background-color: var(--error-color);
    }

    .danger-button > button:hover {
        background-color: #f77066;
    }

    /* Input Styles */
    .stTextInput > div > div > input {
        border-radius: 4px;
        border: 1px solid var(--border-color);
        padding: 0.5rem;
    }

    .stTextInput > div > div > input:focus {
        border-color: var(--primary-color);
        box-shadow: 0 0 0 2px rgba(51, 102, 204, 0.2);
    }

    /* Select Box Styles */
    .stSelectbox > div > div > div {
        border-radius: 4px;
        border: 1px solid var(--border-color);
    }

    .stSelectbox > div > div > div:focus {
        border-color: var(--primary-color);
    }

    /* Checkbox Styles */
    .stCheckbox > div > div > label > div {
        background-color: var(--primary-color) !important;
    }

    /* Dataframe/Table Styles */
    .dataframe {
        border-collapse: collapse;
        width: 100%;
        border-radius: 8px;
        overflow: hidden;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    .dataframe th {
        background-color: var(--primary-color);
        color: white;
        padding: 12px;
        text-align: left;
        font-weight: 600;
    }

    .dataframe td {
        padding: 10px;
        border-bottom: 1px solid var(--border-color);
    }

    .dataframe tr:nth-child(even) {
        background-color: var(--secondary-background);
    }

    .dataframe tr:hover {
        background-color: rgba(51, 102, 204, 0.1);
    }

    /* Card Styles */
    .card {
        background-color: white;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
    }

    .card-header {
        border-bottom: 1px solid var(--border-color);
        padding-bottom: 10px;
        margin-bottom: 15px;
        font-weight: 600;
        color: var(--primary-color);
    }

    /* Status Indicator Styles */
    .status-indicator {
        display: inline-block;
        width: 10px;
        height: 10px;
        border-radius: 50%;
        margin-right: 5px;
    }

    .status-active {
        background-color: var(--success-color);
    }

    .status-inactive {
        background-color: var(--light-text);
    }

    .status-warning {
        background-color: var(--warning-color);
    }

    .status-error {
        background-color: var(--error-color);
    }

    /* Alert/Info Box Styles */
    .info-box {
        background-color: rgba(51, 102, 204, 0.1);
        border-left: 4px solid var(--primary-color);
        padding: 15px;
        margin: 15px 0;
        border-radius: 4px;
    }

    .success-box {
        background-color: rgba(76, 175, 80, 0.1);
        border-left: 4px solid var(--success-color);
        padding: 15px;
        margin: 15px 0;
        border-radius: 4px;
    }

    .warning-box {
        background-color: rgba(255, 152, 0, 0.1);
        border-left: 4px solid var(--warning-color);
        padding: 15px;
        margin: 15px 0;
        border-radius: 4px;
    }

    .error-box {
        background-color: rgba(244, 67, 54, 0.1);
        border-left: 4px solid var(--error-color);
        padding: 15px;
        margin: 15px 0;
        border-radius: 4px;
    }

    /* Sidebar Styling */
    .css-1d391kg {
        background-color: var(--secondary-background);
    }

    .css-1d391kg .stButton > button {
        width: 100%;
        margin-bottom: 10px;
    }

    /* Expander Styling */
    .streamlit-expanderHeader {
        background-color: var(--secondary-background);
        border-radius: 4px;
        padding: 10px !important;
    }

    .streamlit-expanderHeader:hover {
        background-color: rgba(51, 102, 204, 0.1);
    }

    /* Progress Bar Styling */
    .stProgress > div > div > div > div {
        background-color: var(--primary-color);
    }

    /* Metric Styling */
    .stMetric label {
        color: var(--primary-color);
    }

    /* Dashboard Specific Styles */
    .dashboard-card {
        background-color: white;
        border-radius: 8px;
        padding: 20px;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
        margin-bottom: 20px;
        text-align: center;
    }

    .dashboard-card h3 {
        color: var(--primary-color);
        margin-bottom: 10px;
    }

    .dashboard-card .value {
        font-size: 2.5rem;
        font-weight: 700;
        color: var(--text-color);
    }

    .dashboard-card .label {
        color: var(--light-text);
        font-size: 0.9rem;
    }

    /* Zeiterfassung Specific Styles */
    .timer-display {
        font-size: 3rem;
        font-weight: 700;
        text-align: center;
        color: var(--primary-color);
        font-family: 'Courier New', monospace;
        background-color: var(--secondary-background);
        padding: 20px;
        border-radius: 8px;
        margin: 20px 0;
        box-shadow: 0 4px 8px rgba(0,0,0,0.1);
    }

    .timer-controls {
        display: flex;
        justify-content: center;
        gap: 10px;
        margin: 20px 0;
    }

    /* Projektauswahl Styling */
    .project-selector {
        margin: 20px 0;
        padding: 15px;
        background-color: var(--secondary-background);
        border-radius: 8px;
    }

    /* Urlaub & Krankheit Specific Styles */
    .calendar-day {
        width: 40px;
        height: 40px;
        display: inline-flex;
        align-items: center;
        justify-content: center;
        margin: 2px;
        border-radius: 50%;
        cursor: pointer;
    }

    .calendar-day.selected {
        background-color: var(--primary-color);
        color: white;
    }

    .calendar-day.vacation {
        background-color: var(--primary-color-light);
        color: white;
    }

    .calendar-day.sick {
        background-color: var(--error-color);
        color: white;
    }

    .calendar-day.weekend {
        background-color: var(--secondary-background);
        color: var(--light-text);
    }

    .calendar-day.holiday {
        background-color: var(--warning-color);
        color: white;
    }

    /* Responsive Design Anpassungen */
    @media (max-width: 768px) {
        h1 {
            font-size: 1.8rem;
        }
        
        h2 {
            font-size: 1.5rem;
        }
        
        h3 {
            font-size: 1.2rem;
        }
        
        .timer-display {
            font-size: 2.5rem;
        }
        
        .dashboard-card .value {
            font-size: 2rem;
        }
    }
    </style>
    """, unsafe_allow_html=True)

def apply_card_style(title, content):
    """
    Wendet Card-Styling auf einen Inhalt an
    
    Args:
        title: Titel der Card
        content: Inhalt der Card
    
    Returns:
        HTML-String mit Card-Styling
    """
    return f"""
    <div class="card">
        <div class="card-header">{title}</div>
        {content}
    </div>
    """

def apply_status_indicator(status, text):
    """
    Erstellt einen Statusindikator
    
    Args:
        status: Status (active, inactive, warning, error)
        text: Begleittext
    
    Returns:
        HTML-String mit Statusindikator
    """
    return f"""
    <div>
        <span class="status-indicator status-{status}"></span>
        {text}
    </div>
    """

def apply_info_box(content, box_type="info"):
    """
    Erstellt eine Info-Box
    
    Args:
        content: Inhalt der Box
        box_type: Typ der Box (info, success, warning, error)
    
    Returns:
        HTML-String mit Info-Box
    """
    return f"""
    <div class="{box_type}-box">
        {content}
    </div>
    """

def apply_dashboard_card(title, value, label):
    """
    Erstellt eine Dashboard-Card
    
    Args:
        title: Titel der Card
        value: Hauptwert
        label: Beschriftung des Werts
    
    Returns:
        HTML-String mit Dashboard-Card
    """
    return f"""
    <div class="dashboard-card">
        <h3>{title}</h3>
        <div class="value">{value}</div>
        <div class="label">{label}</div>
    </div>
    """

def apply_timer_display(time_str):
    """
    Erstellt eine Timer-Anzeige
    
    Args:
        time_str: Zeit als String (z.B. "00:00:00")
    
    Returns:
        HTML-String mit Timer-Anzeige
    """
    return f"""
    <div class="timer-display">
        {time_str}
    </div>
    """

# Exportiere die Funktionen
__all__ = [
    'load_global_css',
    'apply_card_style',
    'apply_status_indicator',
    'apply_info_box',
    'apply_dashboard_card',
    'apply_timer_display'
]
