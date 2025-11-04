import hashlib
import json
import uuid
from datetime import datetime
from typing import Dict, List, Optional
import aiofiles
from backend.models.schemas import AuditLogEntry, RegionEnum

class AuditService:
    def __init__(self):
        self.audit_logs: List[AuditLogEntry] = []
        
    async def log_event(self, event_type: str, region: RegionEnum, 
                       details: Dict, user_id: Optional[str] = None):
        """Create immutable audit log entry"""
        log_id = str(uuid.uuid4())
        timestamp = datetime.utcnow()
        
        # Create hash for immutability
        hash_input = f"{log_id}{timestamp.isoformat()}{event_type}{json.dumps(details)}"
        log_hash = hashlib.sha256(hash_input.encode()).hexdigest()
        
        entry = AuditLogEntry(
            log_id=log_id,
            timestamp=timestamp,
            event_type=event_type,
            region=region,
            user_id=user_id,
            details=details,
            hash=log_hash
        )
        
        self.audit_logs.append(entry)
        
        # Persist to disk
        log_path = f"data/logs/audit_{log_id}.json"
        async with aiofiles.open(log_path, 'w') as f:
            await f.write(entry.model_dump_json())
        
        return entry
    
    def get_recent_logs(self, limit: int = 50) -> List[AuditLogEntry]:
        """Get recent audit logs"""
        return self.audit_logs[-limit:]

audit_service = AuditService()
