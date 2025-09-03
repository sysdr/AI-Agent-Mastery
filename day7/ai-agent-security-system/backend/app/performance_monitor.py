import asyncio
import time
import psutil
import json
from datetime import datetime, timedelta
from typing import Dict, List, Any
import random

class PerformanceMonitor:
    def __init__(self):
        self.metrics_history = []
        self.security_metrics = []
        self.monitoring_active = False
        self.alert_thresholds = {
            "cpu_percent": 80,
            "memory_percent": 85,
            "auth_failure_rate": 10,
            "response_time_ms": 2000
        }
    
    async def start(self):
        """Start performance monitoring"""
        self.monitoring_active = True
        asyncio.create_task(self._collect_metrics())
        print("📊 Performance Monitor started")
    
    async def stop(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
    
    async def _collect_metrics(self):
        """Continuously collect system and security metrics"""
        while self.monitoring_active:
            try:
                # System metrics
                cpu_percent = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                disk = psutil.disk_usage('/')
                
                # Security-specific metrics (simulated)
                auth_latency = random.uniform(50, 500)  # ms
                encryption_overhead = random.uniform(5, 25)  # %
                active_sessions = random.randint(10, 100)
                failed_auths_last_hour = random.randint(0, 20)
                
                metrics = {
                    "timestamp": datetime.utcnow().isoformat(),
                    "system": {
                        "cpu_percent": cpu_percent,
                        "memory_percent": memory.percent,
                        "memory_available_gb": memory.available / (1024**3),
                        "disk_percent": disk.percent
                    },
                    "security": {
                        "auth_latency_ms": auth_latency,
                        "encryption_overhead_percent": encryption_overhead,
                        "active_sessions": active_sessions,
                        "failed_auths_last_hour": failed_auths_last_hour,
                        "security_events_per_minute": random.randint(1, 15)
                    },
                    "performance": {
                        "response_time_ms": random.uniform(100, 800),
                        "throughput_rps": random.randint(50, 200),
                        "queue_size": random.randint(0, 50)
                    }
                }
                
                self.metrics_history.append(metrics)
                
                # Keep only last 1000 entries
                if len(self.metrics_history) > 1000:
                    self.metrics_history = self.metrics_history[-500:]
                
                # Check for alerts
                await self._check_alerts(metrics)
                
            except Exception as e:
                print(f"Error collecting metrics: {e}")
            
            await asyncio.sleep(30)  # Collect every 30 seconds
    
    async def _check_alerts(self, metrics: Dict):
        """Check metrics against alert thresholds"""
        alerts = []
        
        system = metrics["system"]
        security = metrics["security"]
        performance = metrics["performance"]
        
        if system["cpu_percent"] > self.alert_thresholds["cpu_percent"]:
            alerts.append({
                "type": "high_cpu",
                "value": system["cpu_percent"],
                "threshold": self.alert_thresholds["cpu_percent"]
            })
        
        if system["memory_percent"] > self.alert_thresholds["memory_percent"]:
            alerts.append({
                "type": "high_memory",
                "value": system["memory_percent"],
                "threshold": self.alert_thresholds["memory_percent"]
            })
        
        if security["failed_auths_last_hour"] > self.alert_thresholds["auth_failure_rate"]:
            alerts.append({
                "type": "auth_failures",
                "value": security["failed_auths_last_hour"],
                "threshold": self.alert_thresholds["auth_failure_rate"]
            })
        
        if performance["response_time_ms"] > self.alert_thresholds["response_time_ms"]:
            alerts.append({
                "type": "slow_response",
                "value": performance["response_time_ms"],
                "threshold": self.alert_thresholds["response_time_ms"]
            })
        
        if alerts:
            print(f"🚨 Performance alerts: {alerts}")
    
    async def get_metrics(self) -> Dict:
        """Get current performance metrics"""
        if not self.metrics_history:
            return {
                "current": None,
                "history": [],
                "alerts": [],
                "summary": {}
            }
        
        current = self.metrics_history[-1]
        
        # Calculate summary statistics
        recent_metrics = self.metrics_history[-20:]  # Last 20 entries
        
        avg_cpu = sum(m["system"]["cpu_percent"] for m in recent_metrics) / len(recent_metrics)
        avg_memory = sum(m["system"]["memory_percent"] for m in recent_metrics) / len(recent_metrics)
        avg_auth_latency = sum(m["security"]["auth_latency_ms"] for m in recent_metrics) / len(recent_metrics)
        avg_response_time = sum(m["performance"]["response_time_ms"] for m in recent_metrics) / len(recent_metrics)
        
        return {
            "current": current,
            "history": self.metrics_history[-50:],  # Last 50 entries
            "summary": {
                "avg_cpu_percent": round(avg_cpu, 2),
                "avg_memory_percent": round(avg_memory, 2),
                "avg_auth_latency_ms": round(avg_auth_latency, 2),
                "avg_response_time_ms": round(avg_response_time, 2),
                "uptime_hours": self._calculate_uptime()
            },
            "health_score": self._calculate_health_score(current)
        }
    
    def _calculate_uptime(self) -> float:
        """Calculate system uptime in hours"""
        if not self.metrics_history:
            return 0
        
        first_metric = datetime.fromisoformat(self.metrics_history[0]["timestamp"])
        current_time = datetime.utcnow()
        uptime = (current_time - first_metric).total_seconds() / 3600
        return round(uptime, 2)
    
    def _calculate_health_score(self, current_metrics: Dict) -> int:
        """Calculate overall system health score (0-100)"""
        if not current_metrics:
            return 0
        
        score = 100
        system = current_metrics["system"]
        security = current_metrics["security"]
        performance = current_metrics["performance"]
        
        # Deduct points for high resource usage
        if system["cpu_percent"] > 70:
            score -= min(30, (system["cpu_percent"] - 70) * 2)
        
        if system["memory_percent"] > 80:
            score -= min(25, (system["memory_percent"] - 80) * 5)
        
        # Deduct points for security issues
        if security["failed_auths_last_hour"] > 5:
            score -= min(20, security["failed_auths_last_hour"] * 2)
        
        # Deduct points for performance issues
        if performance["response_time_ms"] > 1000:
            score -= min(25, (performance["response_time_ms"] - 1000) / 100)
        
        return max(0, int(score))
