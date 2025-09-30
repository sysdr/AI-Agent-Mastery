from sqlalchemy import Column, Integer, String, Float, DateTime, Text, Boolean, ForeignKey, JSON
from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime
from enum import Enum
from typing import Dict, List, Any, Optional
from pydantic import BaseModel

Base = declarative_base()

class ExpertiseLevel(str, Enum):
    NOVICE = "novice"
    INTERMEDIATE = "intermediate"
    EXPERT = "expert"
    SPECIALIST = "specialist"

class ValidationStatus(str, Enum):
    PENDING = "pending"
    VALIDATED = "validated"
    DISPUTED = "disputed"
    EXPIRED = "expired"

# Database Models
class KnowledgeBase(Base):
    __tablename__ = "knowledge_base"
    
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, index=True)
    topic = Column(String, index=True)
    content = Column(Text)
    sources = Column(JSON)
    confidence_score = Column(Float)
    validation_status = Column(String, default=ValidationStatus.PENDING)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow)
    version = Column(Integer, default=1)
    access_count = Column(Integer, default=0)
    accuracy_score = Column(Float, default=0.0)

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    query_id = Column(String, index=True)
    agent_id = Column(String)
    query_text = Column(Text)
    response_text = Column(Text)
    confidence_score = Column(Float)
    sources_consulted = Column(JSON)
    validation_steps = Column(JSON)
    expertise_level = Column(String)
    processing_time = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)

class ValidationStep(Base):
    __tablename__ = "validation_steps"
    
    id = Column(Integer, primary_key=True, index=True)
    audit_log_id = Column(Integer, ForeignKey("audit_logs.id"))
    step_type = Column(String)
    input_data = Column(JSON)
    output_data = Column(JSON)
    confidence_impact = Column(Float)
    processing_time = Column(Float)
    timestamp = Column(DateTime, default=datetime.utcnow)
    
    audit_log = relationship("AuditLog", back_populates="steps")

AuditLog.steps = relationship("ValidationStep", back_populates="audit_log")

# Pydantic Models
class QueryRequest(BaseModel):
    query: str
    domain: Optional[str] = None
    required_confidence: Optional[float] = 0.7

class ValidationResult(BaseModel):
    confidence_score: float
    sources_validated: List[str]
    expertise_level: ExpertiseLevel
    audit_trail: List[Dict[str, Any]]
    explanation: str
    processing_time: float

class ExpertResponse(BaseModel):
    query_id: str
    response: str
    validation_result: ValidationResult
    recommendations: List[str]
    escalation_required: bool
