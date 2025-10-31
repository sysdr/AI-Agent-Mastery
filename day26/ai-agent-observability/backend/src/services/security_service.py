from typing import List, Dict, Any, Optional
from datetime import datetime, timedelta
import structlog
import asyncio

logger = structlog.get_logger()

class SecurityService:
    def __init__(self):
        self.alerts: List[Dict] = []
        self.active_alerts: Dict[str, Dict] = {}
        self.security_events: List[Dict] = []
        self.threat_patterns: Dict[str, int] = {}
        
    async def detect_threat(self, event_type: str, severity: str, 
                           details: Dict, correlation_data: Dict = None):
        """Detect and record a security threat"""
        alert_id = f"alert_{int(datetime.now().timestamp() * 1000000)}"
        
        alert = {
            "alert_id": alert_id,
            "event_type": event_type,
            "severity": severity,
            "timestamp": datetime.now().isoformat(),
            "details": details,
            "correlation_data": correlation_data or {},
            "status": "active",
            "auto_response": None
        }
        
        self.active_alerts[alert_id] = alert
        self.alerts.append(alert)
        
        # Keep only last 1000 alerts
        if len(self.alerts) > 1000:
            self.alerts = self.alerts[-1000:]
        
        # Track threat patterns
        pattern_key = f"{event_type}_{severity}"
        self.threat_patterns[pattern_key] = self.threat_patterns.get(pattern_key, 0) + 1
        
        logger.warning("Security threat detected", 
                      alert_id=alert_id, event_type=event_type, severity=severity)
        
        # Auto-response for critical threats
        if severity == "critical":
            await self._auto_respond(alert)
        
        return alert_id
    
    async def _auto_respond(self, alert: Dict):
        """Automatic response to critical threats"""
        try:
            # Implement auto-response logic
            response_actions = {
                "type": "auto_response",
                "actions_taken": ["alert_triggered", "logging_enhanced"],
                "timestamp": datetime.now().isoformat()
            }
            
            alert["auto_response"] = response_actions
            logger.info("Auto-response triggered", alert_id=alert["alert_id"])
            
        except Exception as e:
            logger.error("Error in auto-response", error=str(e))
    
    async def get_active_alerts(self, severity: Optional[str] = None) -> List[Dict]:
        """Get active security alerts"""
        active = list(self.active_alerts.values())
        
        if severity:
            active = [alert for alert in active if alert["severity"] == severity]
        
        return sorted(active, 
                     key=lambda x: x.get("timestamp", ""), 
                     reverse=True)
    
    async def resolve_alert(self, alert_id: str, resolution: str = None):
        """Resolve a security alert"""
        if alert_id in self.active_alerts:
            alert = self.active_alerts[alert_id]
            alert["status"] = "resolved"
            alert["resolved_at"] = datetime.now().isoformat()
            alert["resolution"] = resolution or "Manual resolution"
            del self.active_alerts[alert_id]
            
            logger.info("Alert resolved", alert_id=alert_id)
            return True
        
        return False
    
    async def get_threat_summary(self, hours: int = 24) -> Dict:
        """Get threat summary for dashboard"""
        cutoff_time = datetime.now() - timedelta(hours=hours)
        
        recent_alerts = [
            alert for alert in self.alerts
            if datetime.fromisoformat(alert["timestamp"]) > cutoff_time
        ]
        
        severity_counts = {}
        for alert in recent_alerts:
            severity = alert["severity"]
            severity_counts[severity] = severity_counts.get(severity, 0) + 1
        
        return {
            "total_alerts": len(recent_alerts),
            "active_alerts": len(self.active_alerts),
            "severity_breakdown": severity_counts,
            "threat_patterns": self.threat_patterns
        }
    
    async def health_check(self) -> Dict:
        """Service health check"""
        return {
            "status": "healthy",
            "active_alerts": len(self.active_alerts),
            "total_alerts": len(self.alerts)
        }
