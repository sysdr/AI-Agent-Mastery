from pydantic import BaseModel
from datetime import datetime
from typing import Optional
import uuid

class SecureMessage(BaseModel):
    id: str = None
    sender_id: str
    receiver_id: str
    content: str
    message_type: str = "text"
    timestamp: datetime = None
    encryption_level: str = "AES256"
    
    def __init__(self, **data):
        if not data.get("id"):
            data["id"] = str(uuid.uuid4())
        if not data.get("timestamp"):
            data["timestamp"] = datetime.utcnow()
        super().__init__(**data)

class MessageResponse(BaseModel):
    status: str
    message_id: Optional[str] = None
    threat_score: Optional[float] = None
    error: Optional[str] = None
