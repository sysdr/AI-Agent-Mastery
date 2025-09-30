import os
from typing import List
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    app_name: str = "Expert Agent System"
    debug: bool = True
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    
    # Gemini API
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    
    # Database
    database_url: str = "sqlite:///./expert_agent.db"
    
    # Redis
    redis_url: str = "redis://localhost:6379"
    
    # Security
    secret_key: str = "expert-agent-secret-key-2024"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Validation
    min_confidence_threshold: float = 0.7
    max_sources_to_check: int = 5
    source_timeout_seconds: int = 10
    
    # Knowledge Management
    knowledge_version_retention: int = 10
    audit_log_retention_days: int = 90
    
    class Config:
        env_file = ".env"

settings = Settings()
