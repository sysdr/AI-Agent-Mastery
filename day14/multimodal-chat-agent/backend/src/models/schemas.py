"""
Pydantic models for request/response schemas
"""

from typing import Optional, List, Dict, Any
from pydantic import BaseModel
from datetime import datetime

class ChatMessage(BaseModel):
    content: str
    conversation_id: Optional[str] = None
    user_id: Optional[str] = None

class ChatResponse(BaseModel):
    content: str
    conversation_id: str
    tokens_used: int
    model_used: str
    timestamp: float = None

class SystemMetrics(BaseModel):
    cpu_usage: float
    memory_usage: float
    active_connections: int
    requests_per_minute: int
    avg_response_time: float
    error_rate: float

class User(BaseModel):
    id: str
    username: str
    is_admin: bool = False

class AuditLog(BaseModel):
    id: Optional[str] = None
    user_id: str
    action: str
    content: str
    response: str
    metadata: Dict[str, Any]
    timestamp: datetime
