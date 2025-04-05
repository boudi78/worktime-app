# modules/utils.py
import streamlit as st
import os
import json
from datetime import datetime
import pandas as pd  # Import pandas
import bcrypt  # Import bcrypt for password hashing
import logging  # Import logging

# Configure logging (optional)
logging.basicConfig(filename='app.log', level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')

DATA_FOLDER = "data"
TIME_ENTRIES_FILE = os.path.join(DATA_FOLDER, "time_entries.json")
VACATION_FILE = os.path.join(DATA_FOLDER, "vacation_requests.json")
SICK_FILE = os.path.join(DATA_FOLDER, "sick_leaves.json")
EMPLOYEE_FILE = os.path.join(DATA_FOLDER, "employees.json")  # Define the employee file path
LOCATION_CODES = {
    "Werner Siemens Strasse 107": "WS107", 
    "Werner Siemens Strasse 39": "WS39", 
    "Home Office": "HOME"
}

# --- SESSION STATE ---
def init_session_state():
    if "user" not in st.session_state:
        st.session_state["user"] = None
    if "username" not in st.session_state:
        st.session_state.username = None
    if "is_admin" not in st.session_state:
        st.session_state.is_admin = False
    if "show_notifications" not in st.session_state:
        st.session_state.show_notifications = False
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Login"
    if "admin_page" not in st.session_state:
        st.session_state.admin_page = None
    if "user" not in st.session_state:
        st.session_state.user = None
    if "current_page" not in st.session_state:
        st.session_state.current_page = "Login"

    # Also initialize checkin_time and location
    if "checkin_time" not in st.session_state:
        st.session_state.checkin_time = None
    if "location" not in st.session_state:
        st.session_state.location = None

# --- DATABASE (JSON FILE) UTILS ---
def load_time_entries():
    if not os.path.exists(TIME_ENTRIES_FILE):
        return []
    try:
        with open(TIME_ENTRIES_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {TIME_ENTRIES_FILE}. Returning empty list.")
        return []

def save_time_entries(entries):
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)

    with open(TIME_ENTRIES_FILE, "w", encoding="utf-8") as f:
        json.dump(entries, f, indent=4, ensure_ascii=False)

def save_time_entry(entry):
    entries = load_time_entries()
    entries.append(entry)
    save_time_entries(entries)

#Employee loader
def load_employees():
    """Loads employee data from the JSON file."""
    if os.path.exists(EMPLOYEE_FILE):
        try:
            with open(EMPLOYEE_FILE, "r", encoding="utf-8") as f:
                return json.load(f)
        except json.JSONDecodeError:
            print(f"Warning: Could not decode JSON from {EMPLOYEE_FILE}. Returning an empty list.")
            return []
    else:
        print(f"Warning: Employee file not found at {EMPLOYEE_FILE}. Returning an empty list.")
        return []

# --- EMPLOYEE MANAGEMENT ---
def add_employee(employee):
    employees = load_employees()
    employees.append(employee)
    with open(EMPLOYEE_FILE, "w", encoding="utf-8") as f:
        json.dump(employees, f, indent=4, ensure_ascii=False)
    logging.info(f"Added employee: {employee['name']} ({employee['id']})")

def update_employee_password(user_id, new_password):
    employees = load_employees()
    for emp in employees:
        if emp["id"] == user_id:
            hashed_pw = bcrypt.hashpw(new_password.encode("utf-8"), bcrypt.gensalt()).decode("utf-8")
            emp["password"] = hashed_pw
            logging.info(f"Updated password for user: {user_id}")
            break
    with open(EMPLOYEE_FILE, "w", encoding="utf-8") as f:
        json.dump(employees, f, indent=4, ensure_ascii=False)

def check_password(user_id, input_password):
    employees = load_employees()
    for emp in employees:
        if emp["id"] == user_id:
            return bcrypt.checkpw(input_password.encode("utf-8"), emp["password"].encode("utf-8"))
    return False

def delete_employee(user_id):
    employees = load_employees()
    updated = [emp for emp in employees if emp["id"] != user_id]
    with open(EMPLOYEE_FILE, "w", encoding="utf-8") as f:
        json.dump(updated, f, indent=4, ensure_ascii=False)
    logging.info(f"Deleted employee with ID: {user_id}")

def update_employee_info(user_id, field, new_value):
    employees = load_employees()
    for emp in employees:
        if emp["id"] == user_id:
            emp[field] = new_value
            logging.info(f"Updated {field} for user {user_id} to {new_value}")
            break
    with open(EMPLOYEE_FILE, "w", encoding="utf-8") as f:
        json.dump(employees, f, indent=4, ensure_ascii=False)

# --- VACATION REQUEST UTILS ---
def load_vacation_requests():
    if not os.path.exists(VACATION_FILE):
        return []
    try:
        with open(VACATION_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {VACATION_FILE}. Returning empty list.")
        return []

def save_vacation_requests(requests):
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
    with open(VACATION_FILE, "w", encoding="utf-8") as f:
        json.dump(requests, f, indent=4, ensure_ascii=False)

def calculate_vacation_days(start_date, end_date):
    """Berechne die Anzahl der Urlaubstage (inklusive Start- und Enddatum)"""
    return (end_date - start_date).days + 1

def calculate_remaining_vacation(user_id: str, vacation_days_entitled: int = 30) -> int:
    """Berechnet verbleibenden Urlaub basierend auf gespeicherten Anträgen"""

    entries = load_vacation_requests() #To avoid code changes.
    total_days_taken = 0

    for entry in entries:
        if entry.get("user_id") == user_id and entry.get("status") == "approved":
            try:
                start = datetime.strptime(entry["start_date"], "%Y-%m-%d").date()
                end = datetime.strptime(entry["end_date"], "%Y-%m-%d").date()
                days = calculate_vacation_days(start, end)
                total_days_taken += days
            except Exception as e:
                print(f"Error processing vacation entry: {e}")
                continue

    remaining = vacation_days_entitled - total_days_taken
    return max(0, remaining)

def save_vacation(entry):
    requests = load_vacation_requests()
    requests.append(entry)
    save_vacation_requests(requests)

# --- VACATION STATUS ---
def update_vacation_status(request_id, new_status):
    requests = load_vacation_requests()
    for request in requests:
        if request.get("id") == request_id:
            request["status"] = new_status
            logging.info(f"Updated vacation status for request {request_id} to {new_status} for vacation id: {request_id}")
            break
    save_vacation_requests(requests)

def delete_vacation_request(request_id):
    """Deletes a vacation request based on its unique request ID."""
    requests = load_vacation_requests()
    initial_length = len(requests)  # For checking if deletion occurred
    requests = [req for req in requests if req.get("id") != request_id]
    if len(requests) < initial_length:
        save_vacation_requests(requests)
        logging.info(f"Deleted vacation request with ID: {request_id}")
        return True  # Indicate success
    else:
        logging.warning(f"Vacation request with ID {request_id} not found.")
        return False  # Indicate not found

def update_vacation_status_by_data(user_id, start_date, end_date, new_status):
    """Updates vacation status based on user_id, start_date, and end_date."""
    requests = load_vacation_requests()
    updated = False
    for req in requests:
        if (req.get("user_id") == user_id and
            req.get("start_date") == start_date and
            req.get("end_date") == end_date):
            req["status"] = new_status
            logging.info(f"Updated vacation status for user {user_id} from {start_date} to {end_date} to {new_status}")
            updated = True
            break
    if updated:
        save_vacation_requests(requests)
    return updated

# --- SICK LEAVE UTILS --- # ADD THIS SECTION

def load_sick_leaves():
    if not os.path.exists(SICK_FILE):
        return []
    try:
        with open(SICK_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    except FileNotFoundError:
        return []
    except json.JSONDecodeError:
        print(f"Error decoding JSON from {SICK_FILE}. Returning empty list.")
        return []

def save_sick_leaves(sick_leaves):
    if not os.path.exists(DATA_FOLDER):
        os.makedirs(DATA_FOLDER)
    with open(SICK_FILE, "w", encoding="utf-8") as f:
        json.dump(sick_leaves, f, indent=4, ensure_ascii=False)


def calculate_absence_statistics(employees, vacation_requests, sick_leaves):
    """Aggregiert Urlaubs- und Kranktage pro Monat & Mitarbeiter"""
    data = []

    for emp in employees:
        user_id = emp["id"]
        name = emp["name"]
        stats = {"Name": name}

        for month in range(1, 13):
            urlaubstage = 0
            kranktage = 0

            for urlaub in vacation_requests:
                if urlaub["user_id"] == user_id and urlaub.get("status") == "approved":
                    try:
                        start = datetime.strptime(urlaub["start_date"], "%Y-%m-%d").date()
                        end = datetime.strptime(urlaub["end_date"], "%Y-%m-%d").date()
                        for d in pd.date_range(start, end):
                            if d.month == month:
                                urlaubstage += 1
                    except ValueError:
                        print(f"Skipping invalid date in vacation request: {urlaub}")

            for krank in sick_leaves:
                if krank["user_id"] == user_id:
                    try:
                        start = datetime.strptime(krank["start_date"], "%Y-%m-%d").date()
                        end = datetime.strptime(krank["end_date"], "%Y-%m-%d").date()
                        for d in pd.date_range(start, end):
                            if d.month == month:
                                kranktage += 1
                    except ValueError:
                        print(f"Skipping invalid date in sick leave: {krank}")

            stats[f"{month:02d}_Urlaub"] = urlaubstage
            stats[f"{month:02d}_Krank"] = kranktage

        data.append(stats)

    return pd.DataFrame(data)

# --- OVERTIME STATISTICS ---
def calculate_overtime_hours(time_entries, employee_id, year, month):
    """Calculates total overtime hours for a given employee id, year, and month."""
    total_overtime = 0
    for entry in time_entries:
        try:
            #Parse date from string
            entry_date = datetime.strptime(entry["check_in"], "%Y-%m-%d %H:%M:%S")
            if (
                entry["user_id"] == employee_id
                and entry_date.year == year
                and entry_date.month == month
                and entry.get("overtime", False) # Use .get() to handle missing overtime key
            ):
                total_overtime += entry["duration_hours"]
        except ValueError as e:
            print(f"Error processing time entry: {e}.  Skipping.") #Handle errors
            continue
    return round(total_overtime, 2)


def display_overtime_statistics(time_entries, employees):
    """Displays overtime statistics per employee and month in a table."""
    st.header("📊 Überstunden Statistik")

    # Year selection
    current_year = datetime.now().year
    year = st.selectbox("Jahr auswählen", list(range(2023, current_year + 2)), index=current_year - 2023)

    # Prepare data for DataFrame
    data = []
    for employee in employees:
        employee_id = employee["id"]
        employee_name = employee["name"]
        monthly_overtime = {}
        for month in range(1, 13):
            overtime_hours = calculate_overtime_hours(time_entries, employee_id, year, month)
            monthly_overtime[datetime(year, month, 1).strftime("%B")] = overtime_hours  # Month name as key

        # Include the year in the data
        employee_data = {"Employee Name": employee_name, **monthly_overtime}
        data.append(employee_data)

    # Create Pandas DataFrame
    df = pd.DataFrame(data)

    # Display the DataFrame
    st.dataframe(df)

def get_vacation_stats(year=datetime.now().year):
    """Calculate vacation statistics for each month of a given year."""
    vacation_requests = load_vacation_requests()
    stats = {}
    for month in range(1, 13):
        stats[month] = 0

    for request in vacation_requests:
        try:
            start_date = datetime.strptime(request["start_date"], "%Y-%m-%d")
            if start_date.year == year and request["status"] == "approved":
                stats[start_date.month] += 1 #count each vacation entry.
        except (ValueError, KeyError):
            continue
    return stats


def get_sick_leave_stats(year=datetime.now().year):
    """Calculate sick leave statistics for each month of a given year."""
    sick_leaves = load_sick_leaves()
    stats = {}
    for month in range(1, 13):
        stats[month] = 0

    for sick_leave in sick_leaves:
        try:
            start_date = datetime.strptime(sick_leave["start_date"], "%Y-%m-%d")
            if start_date.year == year:
                stats[start_date.month] += 1 #count each sick leave entry
        except (ValueError, KeyError):
            continue
    return stats

def update_time_entry(user_id, date_str, new_checkin, new_checkout):
    """Updates an existing time entry"""
    entries = load_time_entries()
    updated = False
    for e in entries:
        if e["user_id"] == user_id and e["check_in"].startswith(date_str):
            e["check_in"] = new_checkin
            e["check_out"] = new_checkout
            logging.info(f"Updated checkin/checkout times for user: {user_id} on date {date_str} to {new_checkin}/{new_checkout}")
            updated = True
            break
    if updated:
        save_time_entries(entries)
        return True
    return False

# --- LOGOUT ---
def logout():
    st.session_state.user = None
    st.session_state.current_page = "Login"
    st.rerun()

def get_db_session():
    # Placeholder for database access, not needed with JSON
    return None
