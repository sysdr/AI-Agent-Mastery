from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    DATABASE_URL: str = "sqlite:///./secure_memory.db"
    SECRET_KEY: str = "your-secret-key-change-in-production"
    GEMINI_API_KEY: str = "your-gemini-api-key"
    ENCRYPTION_KEY: str = "your-encryption-key-32-characters-long"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    LOG_LEVEL: str = "INFO"
    REDIS_URL: str = "redis://localhost:6379"
    PII_MODEL_PATH: str = "./models/pii_model"
    AUDIT_LOG_PATH: str = "./logs/audit.log"
    
    class Config:
        env_file = ".env"

settings = Settings()
