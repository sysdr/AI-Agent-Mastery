from sqlalchemy import create_engine, Column, Integer, String, DateTime, Text, Boolean, Float, ForeignKey, JSON
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker, relationship
from sqlalchemy.sql import func
import os

DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:password@localhost:5432/multiagent_security")

engine = create_engine(DATABASE_URL)
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class Agent(Base):
    __tablename__ = "agents"
    
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True)
    agent_type = Column(String)  # writer, editor, reviewer, coordinator
    capabilities = Column(JSON)
    certificate = Column(Text)
    private_key = Column(Text)
    status = Column(String, default="active")
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    sent_messages = relationship("AgentMessage", foreign_keys="AgentMessage.sender_id", back_populates="sender")
    received_messages = relationship("AgentMessage", foreign_keys="AgentMessage.receiver_id", back_populates="receiver")
    resource_usage = relationship("ResourceUsage", back_populates="agent")

class AgentMessage(Base):
    __tablename__ = "agent_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    sender_id = Column(Integer, ForeignKey("agents.id"))
    receiver_id = Column(Integer, ForeignKey("agents.id"))
    encrypted_content = Column(Text)
    message_type = Column(String)
    session_key = Column(Text)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    sender = relationship("Agent", foreign_keys=[sender_id], back_populates="sent_messages")
    receiver = relationship("Agent", foreign_keys=[receiver_id], back_populates="received_messages")

class ResourceUsage(Base):
    __tablename__ = "resource_usage"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"))
    resource_type = Column(String)  # api_calls, compute_time, cost
    amount_used = Column(Float)
    quota_limit = Column(Float)
    date = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationships
    agent = relationship("Agent", back_populates="resource_usage")

class ContentItem(Base):
    __tablename__ = "content_items"
    
    id = Column(Integer, primary_key=True, index=True)
    title = Column(String)
    content = Column(Text)
    status = Column(String, default="draft")  # draft, review, approved, published
    writer_agent_id = Column(Integer, ForeignKey("agents.id"))
    editor_agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    reviewer_agent_id = Column(Integer, ForeignKey("agents.id"), nullable=True)
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())

class AuditLog(Base):
    __tablename__ = "audit_logs"
    
    id = Column(Integer, primary_key=True, index=True)
    agent_id = Column(Integer, ForeignKey("agents.id"))
    action = Column(String)
    resource = Column(String)
    details = Column(JSON)
    timestamp = Column(DateTime(timezone=True), server_default=func.now())
    success = Column(Boolean)
