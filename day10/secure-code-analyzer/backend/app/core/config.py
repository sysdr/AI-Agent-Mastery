"""
Configuration management for Secure Code Analysis Agent
"""

import os
from functools import lru_cache
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # API Configuration
    host: str = "127.0.0.1"
    port: int = 8000
    debug: bool = True
    
    # AI Service
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "")
    
    # Database
    database_url: str = "sqlite:///./security_agent.db"
    
    # Security
    secret_key: str = "secure-code-analysis-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Git Integration
    git_webhook_secret: str = "webhook-secret-key"
    
    # Redis (for caching and task queue)
    redis_url: str = "redis://localhost:6379"
    
    # Analysis Settings
    max_file_size: int = 1024 * 1024  # 1MB
    supported_languages: list = ["python", "javascript", "typescript", "java"]
    
    class Config:
        env_file = ".env"

@lru_cache()
def get_settings():
    return Settings()
