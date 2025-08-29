from pydantic_settings import BaseSettings
from typing import Optional
import os

class Settings(BaseSettings):
    # API Configuration
    API_VERSION: str = "v1"
    PROJECT_NAME: str = "Secure Document Agent"
    
    # Security
    SECRET_KEY: str = "your-secret-key-change-in-production"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 30
    
    # Gemini AI
    GEMINI_API_KEY: str = os.getenv("GEMINI_API_KEY", "")
    
    # Storage
    STORAGE_PATH: str = "./storage"
    ENCRYPTION_KEY: str = "your-encryption-key-32-bytes-long"
    
    # Redis
    REDIS_URL: str = "redis://localhost:6379/0"
    
    # File Processing
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50MB
    ALLOWED_EXTENSIONS: list = [".pdf", ".docx", ".txt", ".xlsx", ".png", ".jpg"]
    
    # Virus Scanning
    CLAMAV_HOST: str = "localhost"
    CLAMAV_PORT: int = 3310
    
    class Config:
        env_file = ".env"

settings = Settings()
