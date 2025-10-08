from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime
from enum import Enum

class ThreatLevel(str, Enum):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class SecurityAnalysisResult(BaseModel):
    file_id: Optional[str] = None
    content_type: str
    filename: str
    risk_score: int  # 0-100
    threat_level: ThreatLevel
    issues_found: List[str]
    recommendations: List[str]
    confidence_score: int  # 0-100
    metadata: Dict[str, Any]
    timestamp: Optional[datetime] = None

class ContentModerationRequest(BaseModel):
    content_type: str
    content_data: Dict[str, Any]
    sensitivity_level: str = "standard"

class ModerationSummary(BaseModel):
    total_files_processed: int
    high_risk_count: int
    medium_risk_count: int
    low_risk_count: int
    processing_date: str
    system_status: str
