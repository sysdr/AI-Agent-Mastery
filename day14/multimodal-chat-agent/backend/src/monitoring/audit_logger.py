"""
Audit Logger for Compliance Tracking
"""

import json
from datetime import datetime
from typing import Dict, Any, List
import structlog
from models.schemas import AuditLog

logger = structlog.get_logger()

class AuditLogger:
    def __init__(self):
        self.log_file = "logs/audit.jsonl"
    
    async def log_interaction(
        self,
        user_id: str,
        action: str,
        content: str,
        response: str,
        metadata: Dict[str, Any] = None
    ):
        """Log user interaction for audit trail"""
        try:
            log_entry = AuditLog(
                user_id=user_id,
                action=action,
                content=content,
                response=response,
                metadata=metadata or {},
                timestamp=datetime.utcnow()
            )
            
            # Write to audit log file
            with open(self.log_file, 'a') as f:
                f.write(json.dumps(log_entry.dict()) + '\n')
            
            # Also log to structured logger
            logger.info("User interaction", **log_entry.dict())
            
        except Exception as e:
            logger.error("Audit logging error", error=str(e))
    
    async def get_logs(self, limit: int = 100, offset: int = 0) -> List[Dict[str, Any]]:
        """Get audit logs for admin review"""
        try:
            logs = []
            with open(self.log_file, 'r') as f:
                for i, line in enumerate(f):
                    if i < offset:
                        continue
                    if len(logs) >= limit:
                        break
                    logs.append(json.loads(line))
            return logs
        except FileNotFoundError:
            return []
        except Exception as e:
            logger.error("Audit log retrieval error", error=str(e))
            return []
