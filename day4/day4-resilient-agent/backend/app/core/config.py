from pydantic_settings import BaseSettings
from typing import List

class Settings(BaseSettings):
    SECRET_KEY: str = "dev-secret-key"
    REDIS_URL: str = "redis://localhost:6379"
    DATABASE_URL: str = "sqlite:///./agent.db"
    GEMINI_API_KEY: str = ""
    LOG_LEVEL: str = "INFO"
    CORS_ORIGINS: List[str] = ["http://localhost:3000"]
    
    # Rate limiting settings
    RATE_LIMIT_REQUESTS: int = 100
    RATE_LIMIT_WINDOW: int = 3600  # 1 hour
    
    # Circuit breaker settings
    FAILURE_THRESHOLD: int = 5
    RECOVERY_TIMEOUT: int = 60
    
    class Config:
        env_file = ".env"

settings = Settings()
