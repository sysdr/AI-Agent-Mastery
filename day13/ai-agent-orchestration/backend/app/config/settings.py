import os
from typing import Optional
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    
    # Redis Configuration  
    redis_url: str = os.getenv("REDIS_URL", "redis://localhost:6379")
    
    # Database Configuration
    database_url: str = os.getenv("DATABASE_URL", "sqlite:///./orchestration.db")
    
    # Orchestration Settings
    max_parallel_tools: int = int(os.getenv("MAX_PARALLEL_TOOLS", "5"))
    cost_budget_limit: float = float(os.getenv("COST_BUDGET_LIMIT", "100.0"))
    
    # Security Settings
    security_log_level: str = os.getenv("SECURITY_LOG_LEVEL", "INFO")
    
    # Circuit Breaker Settings
    circuit_breaker_threshold: int = int(os.getenv("CIRCUIT_BREAKER_THRESHOLD", "5"))
    
    # Rate Limiting
    rate_limit_calls: int = int(os.getenv("RATE_LIMIT_CALLS", "1000"))
    rate_limit_period: int = int(os.getenv("RATE_LIMIT_PERIOD", "3600"))
    
    class Config:
        env_file = ".env"
