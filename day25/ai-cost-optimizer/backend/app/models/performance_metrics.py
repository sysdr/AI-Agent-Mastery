from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional

@dataclass
class PerformanceMetric:
    id: Optional[str] = None
    timestamp: datetime = datetime.now()
    agent_id: str = ''
    cpu_usage: float = 0.0
    memory_usage: float = 0.0
    request_count: int = 0
    error_rate: float = 0.0
    avg_response_time: float = 0.0
    throughput: float = 0.0
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'agent_id': self.agent_id,
            'cpu_usage': self.cpu_usage,
            'memory_usage': self.memory_usage,
            'request_count': self.request_count,
            'error_rate': self.error_rate,
            'avg_response_time': self.avg_response_time,
            'throughput': self.throughput
        }
