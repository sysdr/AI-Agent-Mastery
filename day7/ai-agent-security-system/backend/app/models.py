from pydantic import BaseModel
from typing import List, Dict, Any, Optional
from datetime import datetime

class AgentRegistration(BaseModel):
    agent_id: str
    capabilities: List[str]
    security_level: str = "medium"
    metadata: Optional[Dict[str, Any]] = None

class SecurityEvent(BaseModel):
    event_type: str
    agent_id: Optional[str] = None
    timestamp: datetime
    details: Dict[str, Any]
    severity: str = "low"

class AuditEntry(BaseModel):
    id: Optional[int] = None
    event_type: str
    agent_id: Optional[str] = None
    timestamp: datetime
    event_data: Dict[str, Any]
    verified: bool = False

class VulnerabilityReport(BaseModel):
    scan_id: str
    total_vulnerabilities: int
    high_severity: int
    medium_severity: int
    low_severity: int
    risk_score: int
    last_scan: Optional[str] = None

class PerformanceMetrics(BaseModel):
    timestamp: datetime
    cpu_percent: float
    memory_percent: float
    response_time_ms: float
    active_sessions: int
    health_score: int
