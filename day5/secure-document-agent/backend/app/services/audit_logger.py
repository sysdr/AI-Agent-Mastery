import json
import os
from datetime import datetime
from typing import Dict, Any, List, Optional
import aiofiles
import logging
from ..core.config import settings

logger = logging.getLogger(__name__)

class AuditLogger:
    def __init__(self):
        self.log_path = f"{settings.STORAGE_PATH}/audit"
        os.makedirs(self.log_path, exist_ok=True)
    
    def log_document_event(self, event_type: str, event_data: Dict[str, Any]):
        """Log document-related events for compliance"""
        try:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "category": "document",
                "severity": "info",
                "data": event_data,
                "source": "document_agent"
            }
            
            self._write_log_entry(log_entry)
            
        except Exception as e:
            logger.error(f"Document event logging error: {str(e)}")
    
    def log_security_event(self, event_type: str, event_data: Dict[str, Any]):
        """Log security events for monitoring"""
        try:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "category": "security",
                "severity": "warning",
                "data": event_data,
                "source": "security_scanner"
            }
            
            self._write_log_entry(log_entry)
            
        except Exception as e:
            logger.error(f"Security event logging error: {str(e)}")
    
    def log_compliance_event(self, event_type: str, event_data: Dict[str, Any]):
        """Log compliance-related events"""
        try:
            log_entry = {
                "timestamp": datetime.utcnow().isoformat(),
                "event_type": event_type,
                "category": "compliance",
                "severity": "info",
                "data": event_data,
                "source": "compliance_engine"
            }
            
            self._write_log_entry(log_entry)
            
        except Exception as e:
            logger.error(f"Compliance event logging error: {str(e)}")
    
    async def get_logs(
        self, 
        document_id: Optional[str] = None,
        category: Optional[str] = None,
        limit: int = 50
    ) -> List[Dict[str, Any]]:
        """Retrieve audit logs with filtering"""
        try:
            logs = []
            
            # Get recent log files
            log_files = sorted([f for f in os.listdir(self.log_path) if f.endswith('.jsonl')])
            
            for log_file in log_files[-7:]:  # Last 7 days
                file_path = os.path.join(self.log_path, log_file)
                async with aiofiles.open(file_path, 'r') as f:
                    async for line in f:
                        try:
                            log_entry = json.loads(line.strip())
                            
                            # Apply filters
                            if document_id and log_entry.get("data", {}).get("document_id") != document_id:
                                continue
                            
                            if category and log_entry.get("category") != category:
                                continue
                            
                            logs.append(log_entry)
                            
                            if len(logs) >= limit:
                                break
                                
                        except json.JSONDecodeError:
                            continue
                
                if len(logs) >= limit:
                    break
            
            # Sort by timestamp (newest first)
            logs.sort(key=lambda x: x["timestamp"], reverse=True)
            
            return logs[:limit]
            
        except Exception as e:
            logger.error(f"Log retrieval error: {str(e)}")
            return []
    
    def _write_log_entry(self, log_entry: Dict[str, Any]):
        """Write log entry to file"""
        try:
            log_date = datetime.utcnow().strftime('%Y-%m-%d')
            log_file = os.path.join(self.log_path, f"audit-{log_date}.jsonl")
            
            with open(log_file, 'a') as f:
                f.write(json.dumps(log_entry) + '\n')
                
        except Exception as e:
            logger.error(f"Log writing error: {str(e)}")
