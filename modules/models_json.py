"""
models_json.py - JSON-based data model replacement for SQLAlchemy models
This module provides a JSON-based alternative to the SQLAlchemy models
to avoid SQLite DLL loading issues in Anaconda environments.
"""

import os
import json
from datetime import datetime
from typing import List, Dict, Optional, Generator, Any
import contextlib

# Data folder and file paths
DATA_FOLDER = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
USERS_FILE = os.path.join(DATA_FOLDER, "users.json")
CHECKINS_FILE = os.path.join(DATA_FOLDER, "time_entries.json")
VACATION_REQUESTS_FILE = os.path.join(DATA_FOLDER, "vacation_requests.json")
SICK_LEAVES_FILE = os.path.join(DATA_FOLDER, "sick_leaves.json")

# Ensure data folder exists
os.makedirs(DATA_FOLDER, exist_ok=True)

# Helper functions for JSON operations
def _load_json(file_path: str) -> List[Dict]:
    """Load data from a JSON file."""
    if not os.path.exists(file_path):
        return []
    try:
        with open(file_path, 'r', encoding='utf-8') as f:
            return json.load(f)
    except (json.JSONDecodeError, FileNotFoundError):
        return []

def _save_json(file_path: str, data: List[Dict]):
    """Save data to a JSON file."""
    with open(file_path, 'w', encoding='utf-8') as f:
        json.dump(data, f, indent=4, ensure_ascii=False)

# Session class to mimic SQLAlchemy session behavior
class JSONSession:
    def __init__(self):
        self.users = _load_json(USERS_FILE)
        self.checkins = _load_json(CHECKINS_FILE)
        self.vacation_requests = _load_json(VACATION_REQUESTS_FILE)
        self.sick_leaves = _load_json(SICK_LEAVES_FILE)
        self.changes = False
    
    def query(self, model_class):
        """Simulate SQLAlchemy query functionality."""
        if model_class == User:
            return UserQuery(self.users)
        elif model_class == CheckIn:
            return CheckInQuery(self.checkins)
        elif model_class == VacationRequest:
            return VacationRequestQuery(self.vacation_requests)
        elif model_class == SickLeave:
            return SickLeaveQuery(self.sick_leaves)
        return None
    
    def add(self, obj):
        """Add a new object to the session."""
        if isinstance(obj, User):
            self.users.append(obj.to_dict())
        elif isinstance(obj, CheckIn):
            self.checkins.append(obj.to_dict())
        elif isinstance(obj, VacationRequest):
            self.vacation_requests.append(obj.to_dict())
        elif isinstance(obj, SickLeave):
            self.sick_leaves.append(obj.to_dict())
        self.changes = True
    
    def commit(self):
        """Commit changes to JSON files."""
        if self.changes:
            _save_json(USERS_FILE, self.users)
            _save_json(CHECKINS_FILE, self.checkins)
            _save_json(VACATION_REQUESTS_FILE, self.vacation_requests)
            _save_json(SICK_LEAVES_FILE, self.sick_leaves)
            self.changes = False
    
    def close(self):
        """Close the session."""
        pass

# Base query classes to mimic SQLAlchemy query behavior
class BaseQuery:
    def __init__(self, data):
        self.data = data
        self.filters = []
    
    def filter(self, condition):
        """Add a filter condition."""
        self.filters.append(condition)
        return self
    
    def all(self):
        """Return all matching items."""
        result = self.data
        # Apply filters (simplified)
        return result
    
    def first(self):
        """Return first matching item or None."""
        items = self.all()
        return items[0] if items else None

# Query classes for each model
class UserQuery(BaseQuery):
    pass

class CheckInQuery(BaseQuery):
    pass

class VacationRequestQuery(BaseQuery):
    pass

class SickLeaveQuery(BaseQuery):
    pass

# Model classes to mimic SQLAlchemy models
class User:
    def __init__(self, id=None, user_id=None, name=None, email=None, password=None, role="Mitarbeiter"):
        self.id = id
        self.user_id = user_id
        self.name = name
        self.email = email
        self.password = password
        self.role = role
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "name": self.name,
            "email": self.email,
            "password": self.password,
            "role": self.role
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            user_id=data.get("user_id"),
            name=data.get("name"),
            email=data.get("email"),
            password=data.get("password"),
            role=data.get("role", "Mitarbeiter")
        )

class CheckIn:
    def __init__(self, id=None, user_id=None, check_in_time=None, check_out_time=None, location=None, action=None, notes=None):
        self.id = id
        self.user_id = user_id
        self.check_in_time = check_in_time
        self.check_out_time = check_out_time
        self.location = location
        self.action = action
        self.notes = notes
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "check_in_time": self.check_in_time.isoformat() if self.check_in_time else None,
            "check_out_time": self.check_out_time.isoformat() if self.check_out_time else None,
            "location": self.location,
            "action": self.action,
            "notes": self.notes
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            user_id=data.get("user_id"),
            check_in_time=datetime.fromisoformat(data["check_in_time"]) if data.get("check_in_time") else None,
            check_out_time=datetime.fromisoformat(data["check_out_time"]) if data.get("check_out_time") else None,
            location=data.get("location"),
            action=data.get("action"),
            notes=data.get("notes")
        )

class VacationRequest:
    def __init__(self, id=None, user_id=None, start_date=None, end_date=None, reason=None, approved=False):
        self.id = id
        self.user_id = user_id
        self.start_date = start_date
        self.end_date = end_date
        self.reason = reason
        self.approved = approved
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "start_date": self.start_date.isoformat() if self.start_date else None,
            "end_date": self.end_date.isoformat() if self.end_date else None,
            "reason": self.reason,
            "approved": self.approved
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            user_id=data.get("user_id"),
            start_date=datetime.fromisoformat(data["start_date"]) if data.get("start_date") else None,
            end_date=datetime.fromisoformat(data["end_date"]) if data.get("end_date") else None,
            reason=data.get("reason"),
            approved=data.get("approved", False)
        )

class SickLeave:
    def __init__(self, id=None, user_id=None, date=None, note=None):
        self.id = id
        self.user_id = user_id
        self.date = date
        self.note = note
    
    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "date": self.date.isoformat() if self.date else None,
            "note": self.note
        }
    
    @classmethod
    def from_dict(cls, data):
        return cls(
            id=data.get("id"),
            user_id=data.get("user_id"),
            date=datetime.fromisoformat(data["date"]) if data.get("date") else None,
            note=data.get("note")
        )

# Session management
@contextlib.contextmanager
def get_db_session():
    """Context manager to get a database session."""
    session = JSONSession()
    try:
        yield session
        session.commit()
    finally:
        session.close()

# Create empty JSON files if they don't exist
for file_path in [USERS_FILE, CHECKINS_FILE, VACATION_REQUESTS_FILE, SICK_LEAVES_FILE]:
    if not os.path.exists(file_path):
        _save_json(file_path, [])
