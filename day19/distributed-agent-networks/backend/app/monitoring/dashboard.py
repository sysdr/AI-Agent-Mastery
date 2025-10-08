import asyncio
import json
import time
import logging
from typing import Dict, List

logger = logging.getLogger(__name__)

class DashboardManager:
    def __init__(self, network_manager):
        self.network = network_manager
        self.metrics_history: List[Dict] = []
        self.alerts: List[Dict] = []
        self.is_running = False
        
    async def start(self):
        """Start dashboard monitoring"""
        self.is_running = True
        asyncio.create_task(self._collect_metrics())
        asyncio.create_task(self._monitor_alerts())
        logger.info("📊 Dashboard monitoring started")
    
    async def _collect_metrics(self):
        """Collect network metrics every 5 seconds"""
        while self.is_running:
            try:
                # Collect current network status
                status = await self.network.get_network_status()
                
                # Add timestamp
                status["timestamp"] = time.time()
                
                # Add derived metrics
                status["metrics"] = {
                    "avg_reputation": sum(agent["reputation"] for agent in status["agents"].values()) / len(status["agents"]),
                    "total_api_calls": sum(agent["resource_usage"]["api_calls"] for agent in status["agents"].values()),
                    "network_utilization": min(100, sum(agent["resource_usage"]["cpu"] for agent in status["agents"].values()) * 100),
                    "active_agents": len([a for a in status["agents"].values() if a["status"] == "active"])
                }
                
                # Store metrics (keep last 100 samples)
                self.metrics_history.append(status)
                if len(self.metrics_history) > 100:
                    self.metrics_history.pop(0)
                
                await asyncio.sleep(5)
                
            except Exception as e:
                logger.error(f"Metrics collection error: {e}")
                await asyncio.sleep(5)
    
    async def _monitor_alerts(self):
        """Monitor for network issues and generate alerts"""
        while self.is_running:
            try:
                if len(self.metrics_history) > 0:
                    latest = self.metrics_history[-1]
                    
                    # Check for low agent count
                    if latest["metrics"]["active_agents"] < 2:
                        await self._create_alert("warning", "Low Agent Count", 
                                               f"Only {latest['metrics']['active_agents']} agents active")
                    
                    # Check for high resource usage
                    if latest["metrics"]["network_utilization"] > 80:
                        await self._create_alert("warning", "High Resource Usage",
                                               f"Network utilization at {latest['metrics']['network_utilization']:.1f}%")
                    
                    # Check for low reputation scores
                    if latest["metrics"]["avg_reputation"] < 0.5:
                        await self._create_alert("error", "Low Network Reputation",
                                               f"Average reputation dropped to {latest['metrics']['avg_reputation']:.2f}")
                
                await asyncio.sleep(30)  # Check every 30 seconds
                
            except Exception as e:
                logger.error(f"Alert monitoring error: {e}")
                await asyncio.sleep(30)
    
    async def _create_alert(self, level: str, title: str, message: str):
        """Create new alert"""
        alert = {
            "id": f"alert_{int(time.time())}",
            "level": level,
            "title": title,
            "message": message,
            "timestamp": time.time(),
            "acknowledged": False
        }
        
        self.alerts.append(alert)
        
        # Keep only last 50 alerts
        if len(self.alerts) > 50:
            self.alerts.pop(0)
        
        logger.warning(f"🚨 Alert: {title} - {message}")
    
    def get_dashboard_data(self) -> Dict:
        """Get complete dashboard data"""
        return {
            "current_status": self.metrics_history[-1] if self.metrics_history else {},
            "metrics_history": self.metrics_history[-20:],  # Last 20 samples
            "alerts": [a for a in self.alerts if not a["acknowledged"]],
            "performance_summary": self._get_performance_summary()
        }
    
    def _get_performance_summary(self) -> Dict:
        """Generate performance summary"""
        if len(self.metrics_history) < 2:
            return {}
        
        recent_metrics = self.metrics_history[-10:]
        
        return {
            "avg_response_time": 0.8,  # Simulated
            "success_rate": 95.5,
            "uptime_percentage": 99.2,
            "total_requests": sum(m["total_messages"] for m in recent_metrics),
            "agents_online": recent_metrics[-1]["metrics"]["active_agents"] if recent_metrics else 0
        }
    
    async def stop(self):
        """Stop dashboard monitoring"""
        self.is_running = False
        logger.info("📊 Dashboard monitoring stopped")
