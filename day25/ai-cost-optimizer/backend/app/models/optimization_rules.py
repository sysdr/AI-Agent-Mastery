from dataclasses import dataclass
from datetime import datetime
from typing import Dict, Any, Optional
from enum import Enum

class OptimizationAction(Enum):
    SCALE_UP = "scale_up"
    SCALE_DOWN = "scale_down"
    SWITCH_MODEL = "switch_model"
    ENABLE_CACHE = "enable_cache"
    THROTTLE_REQUESTS = "throttle_requests"

@dataclass
class OptimizationRule:
    id: Optional[str] = None
    name: str = ''
    condition: str = ''
    action: OptimizationAction = OptimizationAction.SCALE_UP
    parameters: Dict[str, Any] = None
    enabled: bool = True
    created_at: datetime = datetime.now()
    
    def __post_init__(self):
        if self.parameters is None:
            self.parameters = {}
    
    def to_dict(self) -> dict:
        return {
            'id': self.id,
            'name': self.name,
            'condition': self.condition,
            'action': self.action.value,
            'parameters': self.parameters,
            'enabled': self.enabled,
            'created_at': self.created_at.isoformat()
        }
