from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import structlog
import json

logger = structlog.get_logger()

class LoggingService:
    def __init__(self):
        self.logs: List[Dict] = []
        self.log_levels = ["DEBUG", "INFO", "WARNING", "ERROR", "CRITICAL"]
        
    async def log(self, level: str, message: str, context: Dict = None):
        """Log a message with structured logging"""
        if level not in self.log_levels:
            level = "INFO"
            
        log_entry = {
            "timestamp": datetime.now().isoformat(),
            "level": level,
            "message": message,
            "context": context or {}
        }
        
        self.logs.append(log_entry)
        
        # Keep only last 10000 logs
        if len(self.logs) > 10000:
            self.logs = self.logs[-10000:]
        
        # Use structlog for actual logging
        log_func = getattr(logger, level.lower(), logger.info)
        log_func(message, **(context or {}))
        
    async def get_logs(self, level: Optional[str] = None, 
                      start_time: Optional[str] = None, 
                      limit: int = 100) -> List[Dict]:
        """Get logs with optional filtering"""
        filtered_logs = self.logs.copy()
        
        if level:
            filtered_logs = [log for log in filtered_logs if log["level"] == level]
        
        if start_time:
            start_dt = datetime.fromisoformat(start_time)
            filtered_logs = [
                log for log in filtered_logs 
                if datetime.fromisoformat(log["timestamp"]) >= start_dt
            ]
        
        return filtered_logs[-limit:]
    
    async def search_logs(self, query: str, limit: int = 50) -> List[Dict]:
        """Search logs by query string"""
        matching_logs = [
            log for log in self.logs
            if query.lower() in log["message"].lower() or 
               query.lower() in json.dumps(log.get("context", {})).lower()
        ]
        return matching_logs[-limit:]
    
    async def health_check(self) -> Dict:
        """Service health check"""
        return {
            "status": "healthy",
            "total_logs": len(self.logs),
            "recent_logs_count": len([log for log in self.logs 
                                     if datetime.fromisoformat(log["timestamp"]) > 
                                     datetime.now() - timedelta(hours=1)])
        }
