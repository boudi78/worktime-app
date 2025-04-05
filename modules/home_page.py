import streamlit as st
import datetime
import plotly.graph_objects as go
from plotly.subplots import make_subplots
try:
    from sqlalchemy import func, extract
    from modules.models import CheckIn, SickLeave, VacationRequest, User, get_db_session
except ImportError:
    # If SQLAlchemy import fails, we're using the JSON implementation
    from modules.models import CheckIn, SickLeave, VacationRequest, User, get_db_session
from fpdf import FPDF

def show_home_page():
    """Displays the home page content."""
    
    try:
        # Using the context manager to handle session lifecycle
        with get_db_session() as session:
            # Try to use SQLAlchemy style querying first
            try:
                mitarbeiter_list = [u.name for u in session.query(User).all()]
            except (AttributeError, TypeError):
                # If that fails, assume we're using JSON implementation
                mitarbeiter_list = [u.get('name', '') for u in session.users]
            
            # Just to confirm the list is being retrieved
            print(mitarbeiter_list)
        
        # Zeitraum-Filter
        start_date = st.date_input("Startdatum", datetime.date(2023, 1, 1))
        end_date = st.date_input("Enddatum", datetime.date(2023, 12, 31))
        
        # Mitarbeiter-Filter
        with get_db_session() as session:
            try:
                # Try SQLAlchemy style
                mitarbeiter_list = [u.name for u in session.query(User).all()]
            except (AttributeError, TypeError):
                # JSON implementation
                mitarbeiter_list = [u.get('name', '') for u in session.users]
                
            if mitarbeiter_list:
                selected_user = st.selectbox("Mitarbeiter auswählen", mitarbeiter_list)
            else:
                st.warning("Keine Mitarbeiter gefunden.")
                selected_user = None
        
        # Daten aus der Datenbank holen
        with get_db_session() as session:
            try:
                # Try SQLAlchemy style first
                min_check_in = session.query(func.min(CheckIn.check_in_time)).filter(
                    CheckIn.check_in_time.isnot(None)).scalar()
                
                # Wenn keine Daten vorhanden sind, auf 0 setzen
                if not min_check_in:
                    min_check_in = 0
                
                # Überprüfung auf None und sicherstellen, dass Berechnung möglich ist
                if min_check_in and min_check_in != 0:
                    total_hours = session.query(
                        func.sum(func.extract('epoch', CheckIn.check_out_time - CheckIn.check_in_time) / 3600)
                    ).scalar()
                else:
                    total_hours = 0
                    
            except (AttributeError, TypeError, NameError):
                # JSON implementation
                total_hours = 0
                for entry in session.checkins:
                    if entry.get('check_in_time') and entry.get('check_out_time'):
                        try:
                            check_in = datetime.datetime.fromisoformat(entry['check_in_time'])
                            check_out = datetime.datetime.fromisoformat(entry['check_out_time'])
                            hours = (check_out - check_in).total_seconds() / 3600
                            total_hours += hours
                        except (ValueError, TypeError):
                            pass
            
            # Ergebnis anzeigen
            st.metric("Gesamtstunden", f"{total_hours:.2f} Std." if total_hours else "0 Std.")
        
        # Diagramme
        st.subheader("📅 Arbeitszeiten pro Woche")
        
        # Beispiel für ein Diagramm mit Plotly (Arbeitsstunden pro Woche)
        with get_db_session() as session:
            try:
                # Try SQLAlchemy style first
                weekly_hours = session.query(
                    extract('week', CheckIn.check_in_time).label('week'),
                    func.sum(func.extract('epoch', CheckIn.check_out_time - CheckIn.check_in_time) / 3600).label('hours')
                ).group_by('week').order_by('week').all()
                
                weeks = [f"KW {int(week)}" for week, _ in weekly_hours]
                hours = [round(hour, 2) for _, hour in weekly_hours]
                
            except (AttributeError, TypeError, NameError):
                # JSON implementation
                weekly_data = {}
                for entry in session.checkins:
                    if entry.get('check_in_time') and entry.get('check_out_time'):
                        try:
                            check_in = datetime.datetime.fromisoformat(entry['check_in_time'])
                            check_out = datetime.datetime.fromisoformat(entry['check_out_time'])
                            week_num = check_in.isocalendar()[1]  # Get ISO week number
                            hours = (check_out - check_in).total_seconds() / 3600
                            
                            if week_num in weekly_data:
                                weekly_data[week_num] += hours
                            else:
                                weekly_data[week_num] = hours
                        except (ValueError, TypeError):
                            pass
                
                # Sort by week number
                sorted_weeks = sorted(weekly_data.keys())
                weeks = [f"KW {week}" for week in sorted_weeks]
                hours = [round(weekly_data[week], 2) for week in sorted_weeks]
        
        if weeks and hours:
            fig = go.Figure(data=[go.Bar(x=weeks, y=hours)])
            st.plotly_chart(fig)
        else:
            st.info("Keine Daten für das Diagramm verfügbar.")
            
    except Exception as e:
        st.error(f"Ein Fehler ist aufgetreten: {str(e)}")
        import traceback
        st.code(traceback.format_exc())
