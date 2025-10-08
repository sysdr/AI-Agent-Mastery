"""Metrics Collector"""
import time
from typing import Dict, Any

class MetricsCollector:
    async def get_current_metrics(self) -> Dict[str, Any]:
        return {
            "system_uptime": time.time(),
            "active_workflows": 5,
            "completed_workflows": 150,
            "success_rate": 0.94
        }
