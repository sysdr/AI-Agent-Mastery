import os
from dataclasses import dataclass
from typing import Dict, Any

@dataclass
class Config:
    GEMINI_API_KEY: str = os.getenv('GEMINI_API_KEY', '')
    REDIS_URL: str = os.getenv('REDIS_URL', 'redis://localhost:6379/0')
    POSTGRES_URL: str = os.getenv('POSTGRES_URL', 'postgresql://postgres:password@localhost:5432/cost_optimizer')
    DEBUG: bool = os.getenv('DEBUG', 'False').lower() == 'true'
    PORT: int = int(os.getenv('PORT', '8000'))
    
    # Cost optimization settings
    MAX_COST_PER_HOUR: float = 100.0
    COST_ALERT_THRESHOLD: float = 80.0
    PERFORMANCE_THRESHOLD_MS: int = 2000
    AUTO_SCALE_ENABLED: bool = True
    
    # Performance monitoring
    METRICS_RETENTION_HOURS: int = 24
    ALERT_COOLDOWN_MINUTES: int = 15
    
config = Config()
