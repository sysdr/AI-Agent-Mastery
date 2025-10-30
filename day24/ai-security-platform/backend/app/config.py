import os
from pydantic_settings import BaseSettings

class Settings(BaseSettings):
    # Database
    DATABASE_URL: str = "postgresql://postgres:password@localhost/ai_security"
    REDIS_URL: str = "redis://localhost:6379"
    MONGODB_URL: str = "mongodb://localhost:27017"
    CLICKHOUSE_URL: str = "clickhouse://localhost:9000"
    KAFKA_BOOTSTRAP_SERVERS: str = "localhost:9092"
    
    # Security
    SECRET_KEY: str = "your-super-secret-key-change-in-production"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # API Keys
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Features
    ENABLE_AUDIT: bool = True
    ENABLE_COMPLIANCE: bool = True
    ENABLE_THREAT_DETECTION: bool = True
    
    class Config:
        env_file = ".env"

settings = Settings()
