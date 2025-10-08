from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # API Settings
    API_V1_STR: str = "/api/v1"
    PROJECT_NAME: str = "AI Agent Security Assessment System"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Database
    DATABASE_URL: str = "postgresql://user:password@localhost:5432/security_db"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379"
    
    # Gemini AI
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Security Settings
    ENCRYPTION_KEY_LENGTH: int = 32
    AUDIT_RETENTION_DAYS: int = 90
    MAX_LOGIN_ATTEMPTS: int = 5
    
    # Monitoring
    PROMETHEUS_PORT: int = 8001
    
    class Config:
        env_file = ".env"

settings = Settings()
