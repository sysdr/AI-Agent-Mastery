import asyncio
from typing import Dict, List, Any
from datetime import datetime, timedelta
import logging
from collections import defaultdict, deque

logger = logging.getLogger(__name__)

class MetricsService:
    def __init__(self):
        # Message tracking
        self.total_messages = 0
        self.compliance_violations = 0
        self.violation_types = defaultdict(int)
        self.message_history = deque(maxlen=1000)
        
        # Personality tracking
        self.personality_anomalies = 0
        self.drift_incidents = 0
        self.consistency_scores = deque(maxlen=100)
        
        # System metrics
        self.start_time = datetime.now()
        self.request_count = 0
        self.error_count = 0
        self.response_times = deque(maxlen=100)
        
        # Session tracking
        self.active_sessions = set()
        self.session_history = defaultdict(list)
        
    def track_message(self, session_id: str, message: str, compliance_result: Dict[str, Any]):
        """Track a processed message"""
        self.total_messages += 1
        self.request_count += 1
        
        # Track compliance
        if not compliance_result.get("is_valid", True):
            self.compliance_violations += 1
            for flag in compliance_result.get("flags", []):
                self.violation_types[flag] += 1
        
        # Store message history
        self.message_history.append({
            "session_id": session_id,
            "message": message,
            "timestamp": datetime.now(),
            "compliance_score": compliance_result.get("score", 1.0),
            "flags": compliance_result.get("flags", [])
        })
        
        # Track session
        self.active_sessions.add(session_id)
        self.session_history[session_id].append({
            "timestamp": datetime.now(),
            "compliance_score": compliance_result.get("score", 1.0)
        })
        
    def track_personality_result(self, session_id: str, personality_result: Dict[str, Any]):
        """Track personality monitoring results"""
        consistency_score = personality_result.get("consistency_score", 1.0)
        self.consistency_scores.append(consistency_score)
        
        # Track anomalies
        anomalies = personality_result.get("anomalies", [])
        if anomalies:
            self.personality_anomalies += len(anomalies)
        
        # Track drift
        if personality_result.get("personality_drift", False):
            self.drift_incidents += 1
            
    def track_response_time(self, response_time_ms: float):
        """Track API response time"""
        self.response_times.append(response_time_ms)
        
    def track_error(self):
        """Track an error occurrence"""
        self.error_count += 1
        
    def get_compliance_stats(self) -> Dict[str, Any]:
        """Get compliance statistics"""
        compliance_rate = 100.0
        if self.total_messages > 0:
            compliance_rate = ((self.total_messages - self.compliance_violations) / self.total_messages) * 100
        
        # Get top violations
        top_violations = sorted(
            self.violation_types.items(), 
            key=lambda x: x[1], 
            reverse=True
        )[:5]
        
        return {
            "total_messages": self.total_messages,
            "violations": self.compliance_violations,
            "compliance_rate": round(compliance_rate, 2),
            "top_violations": [{"type": k, "count": v} for k, v in top_violations]
        }
        
    def get_personality_consistency(self) -> Dict[str, Any]:
        """Get personality consistency metrics"""
        overall_consistency = 95.0
        if self.consistency_scores:
            overall_consistency = sum(self.consistency_scores) / len(self.consistency_scores) * 100
        
        return {
            "overall_consistency": round(overall_consistency, 2),
            "anomalies_detected": self.personality_anomalies,
            "drift_incidents": self.drift_incidents
        }
        
    def get_system_health(self) -> Dict[str, Any]:
        """Get system health metrics"""
        uptime = datetime.now() - self.start_time
        uptime_percent = 100.0  # Simplified - assume always up
        
        avg_response_time = "50ms"
        if self.response_times:
            avg_response_time = f"{sum(self.response_times) / len(self.response_times):.1f}ms"
        
        error_rate = "0.01%"
        if self.request_count > 0:
            error_rate = f"{(self.error_count / self.request_count) * 100:.2f}%"
        
        return {
            "status": "healthy",
            "uptime": f"{uptime_percent}%",
            "response_time": avg_response_time,
            "error_rate": error_rate,
            "active_sessions": len(self.active_sessions),
            "total_requests": self.request_count
        }
        
    def get_dashboard_metrics(self) -> Dict[str, Any]:
        """Get comprehensive dashboard metrics"""
        return {
            "compliance": self.get_compliance_stats(),
            "personality": self.get_personality_consistency(),
            "system": self.get_system_health(),
            "timestamp": datetime.now().isoformat()
        }

# Global metrics instance
metrics_service = MetricsService()
