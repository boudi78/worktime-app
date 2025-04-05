"""
models.py - Wrapper module that imports from models_json.py
This module provides a compatibility layer to switch from SQLAlchemy to JSON-based storage
to avoid SQLite DLL loading issues in Anaconda environments.
"""

try:
    # First try to import the original SQLAlchemy models
    from typing import Optional
    from datetime import datetime
    from sqlalchemy import create_engine, Column, String, DateTime, Boolean
    from sqlalchemy.ext.declarative import declarative_base
    from sqlalchemy.orm import sessionmaker
    from sqlalchemy import Column, String, DateTime, Boolean, Integer

    # Database Configuration (SQLite Example)
    DATABASE_URL = "sqlite:///./test.db"
    engine = create_engine(DATABASE_URL, connect_args={"check_same_thread": False})

    Base = declarative_base()

    # Define the User model
    class User(Base):
        __tablename__ = "users"

        id = Column(Integer, primary_key=True, index=True)
        user_id = Column(String, unique=True, index=True)
        name = Column(String)
        email = Column(String, unique=True, index=True)
        password = Column(String)
        role = Column(String, default="Mitarbeiter")

    # Define the CheckIn model
    class CheckIn(Base):
        __tablename__ = "checkins"

        id = Column(Integer, primary_key=True, index=True)
        user_id = Column(String)
        check_in_time = Column(DateTime)
        check_out_time = Column(DateTime)
        location = Column(String)
        action = Column(String)
        notes = Column(String, nullable=True)

    # Define the VacationRequest model
    class VacationRequest(Base):
        __tablename__ = "vacation_requests"

        id = Column(Integer, primary_key=True, index=True)
        user_id = Column(String)
        start_date = Column(DateTime)
        end_date = Column(DateTime)
        reason = Column(String)
        approved = Column(Boolean, default=False)

    # Define the SickLeave model
    class SickLeave(Base):
        __tablename__ = "sick_leaves"

        id = Column(Integer, primary_key=True, index=True)
        user_id = Column(String)
        date = Column(DateTime)
        note = Column(String, nullable=True)

    # Create the database tables
    Base.metadata.create_all(bind=engine)

    # Session Maker
    SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)

    # Dependency to get the database session
    def get_db_session():
        db = SessionLocal()
        try:
            yield db
        finally:
            db.close()

    print("Using SQLAlchemy with SQLite database")

except ImportError as e:
    # If SQLite import fails, use the JSON-based alternative
    print(f"SQLite import failed: {e}")
    print("Switching to JSON-based storage as fallback")
    
    # Import from the JSON-based implementation
    from modules.models_json import User, CheckIn, VacationRequest, SickLeave, get_db_session
