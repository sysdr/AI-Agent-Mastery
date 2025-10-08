from pydantic_settings import BaseSettings
from typing import List, Optional
import os

class Settings(BaseSettings):
    # API Keys
    gemini_api_key: str = os.getenv("GEMINI_API_KEY", "your-gemini-key")
    
    # Database
    redis_url: str = "redis://localhost:6379"
    
    # Security
    secret_key: str = "your-secret-key-change-in-production"
    algorithm: str = "HS256"
    access_token_expire_minutes: int = 30
    
    # Compliance Settings
    profanity_threshold: float = 0.7
    toxicity_threshold: float = 0.8
    max_conversation_length: int = 50
    
    # Personality Monitoring
    personality_deviation_threshold: float = 0.3
    behavioral_window_size: int = 10
    
    # Rate Limiting
    rate_limit_requests: int = 100
    rate_limit_window: int = 60
    
    # CORS
    cors_origins: List[str] = ["http://localhost:3000"]
    
    class Config:
        env_file = ".env"

settings = Settings()
