from sqlalchemy import Column, Integer, String, DateTime, JSON, Boolean, Text, Enum as SQLEnum
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime
import enum

Base = declarative_base()

class RequestStatus(str, enum.Enum):
    PENDING = "pending"
    PROCESSING = "processing"
    COMPLETED = "completed"
    FAILED = "failed"
    CIRCUIT_OPEN = "circuit_open"

class IntegrationRequest(Base):
    __tablename__ = "integration_requests"
    
    id = Column(Integer, primary_key=True, index=True)
    correlation_id = Column(String(100), unique=True, index=True)
    request_type = Column(String(50), index=True)
    source_system = Column(String(50))
    target_system = Column(String(50))
    request_data = Column(JSON)
    transformed_data = Column(JSON)
    response_data = Column(JSON)
    status = Column(SQLEnum(RequestStatus), default=RequestStatus.PENDING)
    error_message = Column(Text, nullable=True)
    processing_time_ms = Column(Integer, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow, index=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    retry_count = Column(Integer, default=0)
    circuit_breaker_trips = Column(Integer, default=0)

class Event(Base):
    __tablename__ = "events"
    
    id = Column(Integer, primary_key=True, index=True)
    event_id = Column(String(100), unique=True, index=True)
    event_type = Column(String(100), index=True)
    aggregate_id = Column(String(100), index=True)
    aggregate_type = Column(String(50))
    event_data = Column(JSON)
    event_metadata = Column(JSON)
    user_id = Column(String(100), nullable=True)
    correlation_id = Column(String(100), index=True)
    sequence_number = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    signature = Column(Text)
    is_deleted = Column(Boolean, default=False)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    audit_id = Column(String(100), unique=True, index=True)
    action = Column(String(100), index=True)
    resource_type = Column(String(50))
    resource_id = Column(String(100))
    user_id = Column(String(100), index=True)
    ip_address = Column(String(50))
    user_agent = Column(Text)
    request_data = Column(JSON)
    response_data = Column(JSON)
    status_code = Column(Integer)
    timestamp = Column(DateTime, default=datetime.utcnow, index=True)
    correlation_id = Column(String(100), index=True)

class CircuitBreakerState(Base):
    __tablename__ = "circuit_breaker_states"
    
    id = Column(Integer, primary_key=True, index=True)
    service_name = Column(String(100), unique=True, index=True)
    state = Column(String(20))  # CLOSED, OPEN, HALF_OPEN
    failure_count = Column(Integer, default=0)
    success_count = Column(Integer, default=0)
    last_failure_time = Column(DateTime, nullable=True)
    last_success_time = Column(DateTime, nullable=True)
    opened_at = Column(DateTime, nullable=True)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
