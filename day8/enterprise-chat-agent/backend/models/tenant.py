from sqlalchemy import Column, String, Integer, DateTime, JSON, Boolean, Text
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.sql import func
from datetime import datetime
from typing import Dict, Any, Optional

Base = declarative_base()

class TenantModel(Base):
    __tablename__ = "tenants"
    
    tenant_id = Column(String, primary_key=True)
    name = Column(String, nullable=False)
    domain = Column(String, nullable=False)
    sso_config = Column(JSON, nullable=True)
    quota_config = Column(JSON, nullable=False)
    settings = Column(JSON, nullable=True)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)

class UserModel(Base):
    __tablename__ = "users"
    
    user_id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)
    email = Column(String, nullable=False)
    name = Column(String, nullable=False)
    roles = Column(JSON, nullable=False)
    sso_subject = Column(String, nullable=True)
    created_at = Column(DateTime, default=func.now())
    last_active = Column(DateTime, nullable=True)
    is_active = Column(Boolean, default=True)

class ConversationModel(Base):
    __tablename__ = "conversations"
    
    conversation_id = Column(String, primary_key=True)
    tenant_id = Column(String, nullable=False)
    created_by = Column(String, nullable=False)
    title = Column(String, nullable=True)
    context_data = Column(JSON, nullable=False)
    created_at = Column(DateTime, default=func.now())
    updated_at = Column(DateTime, default=func.now(), onupdate=func.now())
    is_active = Column(Boolean, default=True)
