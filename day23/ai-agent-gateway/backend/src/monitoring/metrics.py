import time
from typing import Dict, Any
from collections import defaultdict, Counter
import structlog

logger = structlog.get_logger()

class MetricsCollector:
    def __init__(self):
        self.request_count = Counter()
        self.request_duration = defaultdict(list)
        self.status_codes = Counter()
        self.threat_blocks = 0
        self.rate_limits = 0
        self.errors = 0
        self.start_time = time.time()
        
    def record_request(self, endpoint: str, status_code: int, duration: float):
        """Record request metrics"""
        self.request_count[endpoint] += 1
        self.status_codes[status_code] += 1
        self.request_duration[endpoint].append(duration)
        
        # Keep only recent durations (last 1000 requests per endpoint)
        if len(self.request_duration[endpoint]) > 1000:
            self.request_duration[endpoint] = self.request_duration[endpoint][-1000:]
    
    def increment_threat_blocked(self):
        """Increment threat block counter"""
        self.threat_blocks += 1
    
    def increment_rate_limited(self):
        """Increment rate limit counter"""
        self.rate_limits += 1
    
    def increment_errors(self):
        """Increment error counter"""
        self.errors += 1
    
    def get_metrics(self) -> Dict[str, Any]:
        """Get current metrics"""
        current_time = time.time()
        uptime = current_time - self.start_time
        
        # Calculate average response times
        avg_durations = {}
        for endpoint, durations in self.request_duration.items():
            if durations:
                avg_durations[endpoint] = sum(durations) / len(durations)
        
        return {
            "uptime_seconds": uptime,
            "total_requests": sum(self.request_count.values()),
            "requests_per_endpoint": dict(self.request_count),
            "status_codes": dict(self.status_codes),
            "average_response_time": avg_durations,
            "security": {
                "threats_blocked": self.threat_blocks,
                "rate_limits_applied": self.rate_limits,
                "errors": self.errors
            },
            "timestamp": current_time
        }
    
    def get_health_status(self) -> Dict[str, Any]:
        """Get system health status"""
        total_requests = sum(self.request_count.values())
        error_rate = (self.errors / total_requests) if total_requests > 0 else 0
        
        status = "healthy"
        if error_rate > 0.05:  # More than 5% errors
            status = "unhealthy"
        elif error_rate > 0.01:  # More than 1% errors
            status = "warning"
        
        return {
            "status": status,
            "error_rate": error_rate,
            "total_requests": total_requests,
            "uptime_seconds": time.time() - self.start_time
        }
