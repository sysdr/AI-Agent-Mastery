from sqlalchemy import Column, Integer, String, Float, DateTime, Boolean, Text, JSON
from sqlalchemy.ext.declarative import declarative_base
from datetime import datetime

Base = declarative_base()

class LearningModel(Base):
    __tablename__ = "learning_models"
    
    id = Column(Integer, primary_key=True, index=True)
    version = Column(String, unique=True, index=True)
    weights = Column(JSON)
    bias_metrics = Column(JSON)
    performance_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
    is_active = Column(Boolean, default=False)

class FeedbackData(Base):
    __tablename__ = "feedback_data"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(String, index=True)
    agent_response_id = Column(String, index=True)
    satisfaction_score = Column(Float)
    feedback_text = Column(Text)
    demographic_data = Column(JSON)
    privacy_level = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    processed = Column(Boolean, default=False)

class BiasMetric(Base):
    __tablename__ = "bias_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    model_version = Column(String, index=True)
    metric_type = Column(String)  # demographic_parity, equalized_odds, etc.
    protected_attribute = Column(String)
    metric_value = Column(Float)
    threshold_exceeded = Column(Boolean)
    created_at = Column(DateTime, default=datetime.utcnow)

class PerformanceMetric(Base):
    __tablename__ = "performance_metrics"
    
    id = Column(Integer, primary_key=True, index=True)
    model_version = Column(String, index=True)
    response_time_ms = Column(Float)
    api_cost_usd = Column(Float)
    memory_usage_mb = Column(Float)
    accuracy_score = Column(Float)
    created_at = Column(DateTime, default=datetime.utcnow)
