from pydantic import BaseModel
from typing import Optional, Dict, Any, List
from datetime import datetime

class DocumentResponse(BaseModel):
    document_id: str
    filename: str
    processing_result: Dict[str, Any]
    pii_summary: Dict[str, Any]
    metadata: Dict[str, Any]
    status: str
    uploaded_at: datetime
    
    class Config:
        json_encoders = {
            datetime: lambda v: v.isoformat()
        }

class ProcessingResult(BaseModel):
    text_content: str
    chunks: List[str]
    file_type: str
    content_classification: Dict[str, Any]
    chunk_count: int
    character_count: int

class PIIEntity(BaseModel):
    type: str
    confidence: float
    context: str

class DocumentMetadata(BaseModel):
    filename: str
    file_hash: str
    file_size: int
    content_type: str
    extracted_at: str
    version: str

class AuditLogEntry(BaseModel):
    timestamp: str
    event_type: str
    category: str
    severity: str
    data: Dict[str, Any]
    source: str
