from sqlalchemy import Column, Integer, String, DateTime, Boolean, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class User(Base):
    __tablename__ = "users"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, unique=True, index=True)
    email = Column(String, unique=True, index=True)
    demographic_data = Column(JSON)
    created_at = Column(DateTime, default=datetime.utcnow)

class UserConsent(Base):
    __tablename__ = "user_consents"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    consent_type = Column(String)  # data_collection, learning, analytics
    granted = Column(Boolean)
    expires_at = Column(DateTime)
    created_at = Column(DateTime, default=datetime.utcnow)
