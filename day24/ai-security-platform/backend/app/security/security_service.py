import asyncio
from typing import Dict, List, Any, Optional
from datetime import datetime, timedelta
from sqlalchemy.orm import Session
from ..models.models import SecurityIncident, AuditLog
import json
import google.generativeai as genai
from ..config import settings
import redis
import structlog

logger = structlog.get_logger()

class ThreatLevel(str):
    LOW = "LOW"
    MEDIUM = "MEDIUM"
    HIGH = "HIGH"
    CRITICAL = "CRITICAL"

class SecurityService:
    def __init__(self):
        self.redis_client = redis.Redis.from_url(settings.REDIS_URL, decode_responses=True)
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
        self.anomaly_thresholds = {
            "failed_logins": 5,
            "api_rate_limit": 1000,
            "suspicious_patterns": 3
        }
        
    def detect_anomalies(self, db: Session, user_id: int, timeframe_minutes: int = 60) -> List[Dict[str, Any]]:
        """Detect security anomalies for a user"""
        anomalies = []
        start_time = datetime.utcnow() - timedelta(minutes=timeframe_minutes)
        
        # Get recent user activity
        user_logs = db.query(AuditLog).filter(
            AuditLog.user_id == user_id,
            AuditLog.timestamp >= start_time
        ).all()
        
        # Check for suspicious patterns
        failed_logins = [log for log in user_logs if log.action == "login_failed"]
        if len(failed_logins) >= self.anomaly_thresholds["failed_logins"]:
            anomalies.append({
                "type": "excessive_failed_logins",
                "severity": ThreatLevel.HIGH,
                "count": len(failed_logins),
                "threshold": self.anomaly_thresholds["failed_logins"]
            })
        
        # Check API rate limiting
        api_calls = [log for log in user_logs if log.action.startswith("api_")]
        if len(api_calls) >= self.anomaly_thresholds["api_rate_limit"]:
            anomalies.append({
                "type": "api_rate_exceeded",
                "severity": ThreatLevel.MEDIUM,
                "count": len(api_calls),
                "threshold": self.anomaly_thresholds["api_rate_limit"]
            })
            
        # Check for unusual access patterns
        unique_resources = set(log.resource for log in user_logs)
        if len(unique_resources) > 20:  # Accessing too many different resources
            anomalies.append({
                "type": "unusual_access_pattern",
                "severity": ThreatLevel.MEDIUM,
                "resources_accessed": len(unique_resources)
            })
            
        return anomalies
    
    async def analyze_threat_with_ai(self, incident_data: Dict[str, Any]) -> Dict[str, Any]:
        """Use Gemini AI to analyze security threats"""
        prompt = f"""
        Analyze this security incident data and provide threat assessment:
        
        Incident Type: {incident_data.get('type', 'Unknown')}
        Severity: {incident_data.get('severity', 'Unknown')}
        Details: {json.dumps(incident_data.get('details', {}), indent=2)}
        
        Provide analysis in JSON format with:
        1. threat_level: LOW/MEDIUM/HIGH/CRITICAL
        2. recommendations: list of recommended actions
        3. risk_score: 0-100
        4. potential_impact: description
        5. mitigation_steps: immediate steps to take
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Parse JSON response from AI
            import re
            json_match = re.search(r'\{.*\}', response.text, re.DOTALL)
            if json_match:
                return json.loads(json_match.group())
            else:
                return {"error": "Could not parse AI response"}
        except Exception as e:
            logger.error("AI threat analysis failed", error=str(e))
            return {"error": str(e)}
    
    def create_security_incident(
        self, 
        db: Session,
        severity: str,
        incident_type: str,
        description: str,
        user_id: Optional[int] = None,
        details: Dict[str, Any] = None
    ) -> SecurityIncident:
        incident = SecurityIncident(
            severity=severity,
            incident_type=incident_type,
            description=description,
            user_id=user_id,
            details=details or {}
        )
        db.add(incident)
        db.commit()
        db.refresh(incident)
        
        # Cache incident for real-time monitoring
        self.redis_client.setex(
            f"security_incident:{incident.id}",
            3600,  # 1 hour TTL
            json.dumps({
                "id": incident.id,
                "severity": severity,
                "type": incident_type,
                "timestamp": incident.created_at.isoformat()
            })
        )
        
        return incident
    
    def get_security_dashboard_data(self, db: Session) -> Dict[str, Any]:
        """Get security dashboard metrics"""
        now = datetime.utcnow()
        last_24h = now - timedelta(hours=24)
        last_7d = now - timedelta(days=7)
        
        # Recent incidents
        recent_incidents = db.query(SecurityIncident).filter(
            SecurityIncident.created_at >= last_24h
        ).all()
        
        # Incident counts by severity
        incident_counts = {
            "critical": 0,
            "high": 0, 
            "medium": 0,
            "low": 0
        }
        
        for incident in recent_incidents:
            incident_counts[incident.severity.lower()] += 1
            
        # Authentication metrics
        auth_logs = db.query(AuditLog).filter(
            AuditLog.action.in_(["login_success", "login_failed"]),
            AuditLog.timestamp >= last_7d
        ).all()
        
        login_success = len([log for log in auth_logs if log.action == "login_success"])
        login_failed = len([log for log in auth_logs if log.action == "login_failed"])
        
        return {
            "incidents_24h": len(recent_incidents),
            "incident_counts": incident_counts,
            "auth_success_rate": (login_success / (login_success + login_failed) * 100) if auth_logs else 100,
            "total_logins_7d": len(auth_logs),
            "active_threats": len([i for i in recent_incidents if i.status == "OPEN"]),
            "last_updated": now.isoformat()
        }
    
    def rate_limit_check(self, user_id: int, action: str, limit: int = 100, window_seconds: int = 3600) -> bool:
        """Check if user action is within rate limits"""
        key = f"rate_limit:{user_id}:{action}"
        current = self.redis_client.get(key)
        
        if current is None:
            self.redis_client.setex(key, window_seconds, 1)
            return True
        elif int(current) < limit:
            self.redis_client.incr(key)
            return True
        else:
            return False

security_service = SecurityService()
