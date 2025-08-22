from sqlalchemy import Column, String, DateTime, Text, Integer, Boolean, JSON, Float
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import uuid

Base = declarative_base()

class Conversation(Base):
    __tablename__ = "conversations"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = Column(String, nullable=False, index=True)
    title = Column(String, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    is_active = Column(Boolean, default=True)
    conversation_metadata = Column(JSON, default=dict)

class Message(Base):
    __tablename__ = "messages"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, nullable=False, index=True)
    role = Column(String, nullable=False)  # user, assistant, system
    content_encrypted = Column(Text, nullable=False)
    content_hash = Column(String, nullable=False)
    token_count = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    pii_detected = Column(Boolean, default=False)
    pii_classification = Column(JSON, default=dict)
    compression_level = Column(Integer, default=0)

class ContextWindow(Base):
    __tablename__ = "context_windows"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    conversation_id = Column(String, nullable=False, index=True)
    window_data_encrypted = Column(Text, nullable=False)
    token_count = Column(Integer, nullable=False)
    compression_ratio = Column(Float, default=1.0)
    created_at = Column(DateTime, default=datetime.utcnow)
    relevance_score = Column(Float, default=1.0)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(String, primary_key=True, default=lambda: str(uuid.uuid4()))
    event_type = Column(String, nullable=False, index=True)
    user_id = Column(String, nullable=True, index=True)
    conversation_id = Column(String, nullable=True, index=True)
    event_data = Column(JSON, nullable=False)
    security_level = Column(String, default="INFO")  # INFO, WARNING, CRITICAL
    timestamp = Column(DateTime, default=datetime.utcnow)
    ip_address = Column(String, nullable=True)
    user_agent = Column(String, nullable=True)
