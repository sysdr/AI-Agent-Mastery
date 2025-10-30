from dataclasses import dataclass
from datetime import datetime
from typing import Optional
import json

@dataclass
class CostMetric:
    id: Optional[str] = None
    timestamp: datetime = datetime.now()
    agent_id: str = ''
    request_type: str = ''
    tokens_used: int = 0
    cost_usd: float = 0.0
    model_name: str = ''
    success: bool = True
    response_time_ms: int = 0
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'timestamp': self.timestamp.isoformat(),
            'agent_id': self.agent_id,
            'request_type': self.request_type,
            'tokens_used': self.tokens_used,
            'cost_usd': self.cost_usd,
            'model_name': self.model_name,
            'success': self.success,
            'response_time_ms': self.response_time_ms
        }
    
    @classmethod
    def from_dict(cls, data: dict):
        data['timestamp'] = datetime.fromisoformat(data['timestamp'])
        return cls(**data)
