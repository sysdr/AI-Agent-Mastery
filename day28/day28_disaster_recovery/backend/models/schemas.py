from pydantic import BaseModel, Field
from typing import List, Dict, Optional
from datetime import datetime
from enum import Enum

class RegionEnum(str, Enum):
    US_EAST = "us-east"
    EU_WEST = "eu-west"
    AP_SOUTH = "ap-south"

class SystemState(str, Enum):
    HEALTHY = "HEALTHY"
    DEGRADED = "DEGRADED"
    CRITICAL = "CRITICAL"
    FAILOVER_INITIATED = "FAILOVER_INITIATED"
    SECONDARY_ACTIVE = "SECONDARY_ACTIVE"
    RECOVERY_IN_PROGRESS = "RECOVERY_IN_PROGRESS"
    VALIDATED = "VALIDATED"

class ComplianceTag(BaseModel):
    data_classification: str = "PII"
    retention_days: int = 2555
    encryption_required: bool = True
    allowed_regions: List[str] = ["us-east", "eu-west"]

class BackupMetadata(BaseModel):
    backup_id: str
    timestamp: datetime
    region: RegionEnum
    size_bytes: int
    encrypted: bool
    compliance_tags: ComplianceTag
    hash_sha256: str

class HealthMetrics(BaseModel):
    region: RegionEnum
    latency_ms: float
    error_rate: float
    cpu_usage: float
    memory_usage: float
    timestamp: datetime
    is_healthy: bool

class FailoverEvent(BaseModel):
    event_id: str
    timestamp: datetime
    from_region: RegionEnum
    to_region: RegionEnum
    reason: str
    security_validated: bool
    rto_seconds: float
    rpo_seconds: float

class RecoveryAction(BaseModel):
    action_id: str
    timestamp: datetime
    action_type: str
    target_region: RegionEnum
    success: bool
    details: str

class SovereigntyRule(BaseModel):
    user_region: str
    allowed_storage_regions: List[str]
    compliance_framework: str

class AuditLogEntry(BaseModel):
    log_id: str
    timestamp: datetime
    event_type: str
    region: RegionEnum
    user_id: Optional[str] = None
    details: Dict
    hash: str
