import asyncio
import psutil
import random
from datetime import datetime, timedelta
from typing import Dict, List
import structlog

logger = structlog.get_logger()

class HealthMonitor:
    def __init__(self):
        self.metrics_history = []
        self.alert_thresholds = {
            "cpu_usage": 0.8,
            "memory_usage": 0.85,
            "disk_usage": 0.9,
            "response_time": 2.0,
            "error_rate": 0.05
        }
        
    async def continuous_monitoring(self):
        """Continuous health monitoring loop"""
        logger.info("💓 Starting continuous health monitoring")
        
        while True:
            try:
                health_data = await self.collect_health_metrics()
                self.metrics_history.append(health_data)
                
                # Keep only last hour of data
                cutoff_time = datetime.utcnow() - timedelta(hours=1)
                self.metrics_history = [
                    m for m in self.metrics_history
                    if datetime.fromisoformat(m["timestamp"]) > cutoff_time
                ]
                
                await asyncio.sleep(10)  # Collect every 10 seconds
                
            except Exception as e:
                logger.error(f"Health monitoring error: {e}")
                await asyncio.sleep(30)
    
    async def collect_health_metrics(self) -> Dict:
        """Collect comprehensive health metrics"""
        
        # System metrics
        cpu_percent = psutil.cpu_percent(interval=0.1)
        memory = psutil.virtual_memory()
        disk = psutil.disk_usage('/')
        
        # Simulated application metrics
        request_count = random.randint(90, 110)
        error_count = random.randint(0, 5)
        avg_response_time = random.uniform(0.1, 0.5)
        
        health_data = {
            "timestamp": datetime.utcnow().isoformat(),
            "system": {
                "cpu_usage": cpu_percent / 100.0,
                "memory_usage": memory.percent / 100.0,
                "disk_usage": disk.percent / 100.0,
                "memory_available": memory.available,
                "disk_free": disk.free
            },
            "application": {
                "request_count": request_count,
                "error_count": error_count,
                "error_rate": error_count / max(request_count, 1),
                "avg_response_time": avg_response_time,
                "active_connections": random.randint(20, 100)
            },
            "security": {
                "auth_failures": random.randint(0, 3),
                "blocked_ips": random.randint(0, 2),
                "security_alerts": random.randint(0, 1)
            }
        }
        
        return health_data
    
    async def get_system_health(self) -> Dict:
        """Get current system health status"""
        if not self.metrics_history:
            return {"status": "unknown", "message": "No metrics available"}
        
        latest_metrics = self.metrics_history[-1]
        alerts = []
        
        # Check thresholds
        if latest_metrics["system"]["cpu_usage"] > self.alert_thresholds["cpu_usage"]:
            alerts.append("High CPU usage")
        
        if latest_metrics["system"]["memory_usage"] > self.alert_thresholds["memory_usage"]:
            alerts.append("High memory usage")
        
        if latest_metrics["application"]["error_rate"] > self.alert_thresholds["error_rate"]:
            alerts.append("High error rate")
        
        if latest_metrics["application"]["avg_response_time"] > self.alert_thresholds["response_time"]:
            alerts.append("High response time")
        
        status = "critical" if len(alerts) > 2 else "warning" if alerts else "healthy"
        
        return {
            "status": status,
            "timestamp": latest_metrics["timestamp"],
            "alerts": alerts,
            "metrics": latest_metrics
        }
    
    async def get_detailed_metrics(self) -> Dict:
        """Get detailed metrics for dashboard"""
        if not self.metrics_history:
            return {"error": "No metrics available"}
        
        # Calculate trends
        recent_metrics = self.metrics_history[-10:] if len(self.metrics_history) >= 10 else self.metrics_history
        
        cpu_trend = [m["system"]["cpu_usage"] for m in recent_metrics]
        memory_trend = [m["system"]["memory_usage"] for m in recent_metrics]
        error_trend = [m["application"]["error_rate"] for m in recent_metrics]
        response_trend = [m["application"]["avg_response_time"] for m in recent_metrics]
        
        return {
            "current": self.metrics_history[-1],
            "trends": {
                "cpu_usage": cpu_trend,
                "memory_usage": memory_trend,
                "error_rate": error_trend,
                "response_time": response_trend
            },
            "summary": {
                "total_requests": sum(m["application"]["request_count"] for m in recent_metrics),
                "total_errors": sum(m["application"]["error_count"] for m in recent_metrics),
                "avg_cpu": sum(cpu_trend) / len(cpu_trend),
                "avg_memory": sum(memory_trend) / len(memory_trend)
            }
        }
    
    async def get_realtime_data(self) -> Dict:
        """Get real-time data for WebSocket streaming"""
        if not self.metrics_history:
            return {"error": "No data available"}
        
        latest = self.metrics_history[-1]
        health_status = await self.get_system_health()
        
        return {
            "timestamp": latest["timestamp"],
            "status": health_status["status"],
            "cpu": latest["system"]["cpu_usage"],
            "memory": latest["system"]["memory_usage"],
            "requests": latest["application"]["request_count"],
            "errors": latest["application"]["error_count"],
            "response_time": latest["application"]["avg_response_time"],
            "alerts": health_status["alerts"]
        }
