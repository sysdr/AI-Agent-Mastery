import time
from typing import Dict, List, Any
import structlog
from datetime import datetime
from prometheus_client import Counter, Histogram, Gauge, CollectorRegistry

logger = structlog.get_logger()

class MetricsCollector:
    def __init__(self):
        self.registry = CollectorRegistry()
        self.setup_prometheus_metrics()
        self.orchestration_history = []
        self.system_metrics = {}
        
    def setup_prometheus_metrics(self):
        """Setup Prometheus metrics"""
        self.orchestration_counter = Counter(
            'orchestrations_total', 
            'Total orchestrations executed',
            ['status'],
            registry=self.registry
        )
        
        self.execution_time_histogram = Histogram(
            'orchestration_duration_seconds',
            'Orchestration execution time',
            registry=self.registry
        )
        
        self.cost_gauge = Gauge(
            'total_cost_dollars',
            'Total cost in dollars',
            registry=self.registry
        )
        
        self.active_orchestrations_gauge = Gauge(
            'active_orchestrations',
            'Number of active orchestrations',
            registry=self.registry
        )
    
    async def record_orchestration(self, request_id: str, execution_time: float, 
                                 total_cost: float, tools_used: List[str], success: bool):
        """Record orchestration metrics"""
        
        # Prometheus metrics
        status = "success" if success else "failure"
        self.orchestration_counter.labels(status=status).inc()
        self.execution_time_histogram.observe(execution_time)
        self.cost_gauge.set(total_cost)
        
        # Internal tracking
        orchestration_record = {
            "request_id": request_id,
            "execution_time": execution_time,
            "total_cost": total_cost,
            "tools_used": tools_used,
            "success": success,
            "timestamp": datetime.now().isoformat()
        }
        
        self.orchestration_history.append(orchestration_record)
        
        # Keep only last 1000 records
        if len(self.orchestration_history) > 1000:
            self.orchestration_history = self.orchestration_history[-1000:]
        
        logger.info("Orchestration recorded", 
                   request_id=request_id, 
                   success=success,
                   execution_time=execution_time)
    
    async def get_total_cost(self) -> float:
        """Get total cost from recent orchestrations"""
        return sum(record["total_cost"] for record in self.orchestration_history[-100:])
    
    async def get_security_incidents(self) -> int:
        """Get count of security incidents"""
        return len([record for record in self.orchestration_history 
                   if not record.get("success", True)])
    
    async def get_all_metrics(self) -> Dict[str, Any]:
        """Get comprehensive metrics dashboard"""
        recent_orchestrations = self.orchestration_history[-50:]
        
        total_orchestrations = len(self.orchestration_history)
        successful_orchestrations = len([r for r in self.orchestration_history if r["success"]])
        success_rate = (successful_orchestrations / total_orchestrations * 100) if total_orchestrations > 0 else 0
        
        avg_execution_time = sum(r["execution_time"] for r in recent_orchestrations) / len(recent_orchestrations) if recent_orchestrations else 0
        
        # Tool usage statistics
        tool_usage = {}
        for record in recent_orchestrations:
            for tool in record["tools_used"]:
                tool_usage[tool] = tool_usage.get(tool, 0) + 1
        
        return {
            "system_health": {
                "total_orchestrations": total_orchestrations,
                "success_rate": round(success_rate, 2),
                "avg_execution_time": round(avg_execution_time, 2),
                "total_cost": await self.get_total_cost()
            },
            "tool_usage": tool_usage,
            "recent_orchestrations": recent_orchestrations[-10:],
            "performance": {
                "p50_execution_time": self.calculate_percentile([r["execution_time"] for r in recent_orchestrations], 50),
                "p95_execution_time": self.calculate_percentile([r["execution_time"] for r in recent_orchestrations], 95),
                "p99_execution_time": self.calculate_percentile([r["execution_time"] for r in recent_orchestrations], 99)
            }
        }
    
    def calculate_percentile(self, data: List[float], percentile: int) -> float:
        """Calculate percentile from data"""
        if not data:
            return 0.0
        
        sorted_data = sorted(data)
        k = (len(sorted_data) - 1) * percentile / 100
        f = int(k)
        c = k - f
        
        if f + 1 < len(sorted_data):
            return sorted_data[f] * (1 - c) + sorted_data[f + 1] * c
        else:
            return sorted_data[f]
    
    async def export_prometheus_metrics(self) -> str:
        """Export metrics in Prometheus format"""
        from prometheus_client import generate_latest
        return generate_latest(self.registry).decode('utf-8')
