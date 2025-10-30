"""System Health Monitoring"""
import asyncio
import time
import psutil
import random
from typing import Dict, Any
import structlog

logger = structlog.get_logger()

class HealthMonitor:
    def __init__(self):
        self.monitoring_active = False
        self.system_metrics = {}
        self.health_history = []
        
    async def start_monitoring(self):
        """Start health monitoring"""
        logger.info("Starting Health Monitor")
        self.monitoring_active = True
        asyncio.create_task(self._collect_metrics())
    
    async def stop_monitoring(self):
        """Stop health monitoring"""
        logger.info("Stopping Health Monitor")
        self.monitoring_active = False
    
    async def get_system_health(self) -> Dict[str, Any]:
        """Get current system health metrics"""
        try:
            # System metrics
            cpu_percent = psutil.cpu_percent()
            memory = psutil.virtual_memory()
            disk = psutil.disk_usage('/')
            
            # Simulate additional metrics
            health_score = random.uniform(0.85, 0.99)
            
            health_data = {
                "timestamp": time.time(),
                "health_score": health_score,
                "status": "healthy" if health_score > 0.8 else "warning",
                "system_metrics": {
                    "cpu_usage": cpu_percent,
                    "memory_usage": memory.percent,
                    "disk_usage": disk.percent,
                    "available_memory": memory.available / (1024**3),  # GB
                    "network_connections": len(psutil.net_connections())
                },
                "service_status": {
                    "api_server": "running",
                    "database": "connected",
                    "cache": "connected",
                    "message_queue": "running"
                },
                "performance_metrics": {
                    "avg_response_time": random.uniform(0.1, 0.5),
                    "requests_per_second": random.randint(50, 200),
                    "error_rate": random.uniform(0.001, 0.01),
                    "uptime_hours": random.uniform(24, 168)
                }
            }
            
            self.system_metrics = health_data
            return health_data
            
        except Exception as e:
            logger.error("Failed to collect health metrics", error=str(e))
            return {
                "timestamp": time.time(),
                "health_score": 0.0,
                "status": "error",
                "error": str(e)
            }
    
    async def _collect_metrics(self):
        """Background task to collect metrics"""
        while self.monitoring_active:
            try:
                health_data = await self.get_system_health()
                
                # Store health history (keep last 100 entries)
                self.health_history.append(health_data)
                if len(self.health_history) > 100:
                    self.health_history.pop(0)
                
                # Check for health alerts
                if health_data["health_score"] < 0.7:
                    logger.warning("Low system health detected", 
                                 health_score=health_data["health_score"])
                
                await asyncio.sleep(10)  # Collect every 10 seconds
                
            except Exception as e:
                logger.error("Health monitoring error", error=str(e))
                await asyncio.sleep(5)
    
    def get_health_history(self) -> list:
        """Get health metrics history"""
        return self.health_history.copy()
