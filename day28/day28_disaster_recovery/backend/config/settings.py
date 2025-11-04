from pydantic_settings import BaseSettings
from typing import List, Dict

class Settings(BaseSettings):
    # API Configuration
    GEMINI_API_KEY: str = "AIzaSyDGswqDT4wQw_bd4WZtIgYAawRDZ0Gisn8"
    
    # Backup Configuration
    BACKUP_INTERVAL_SECONDS: int = 30
    BACKUP_ENCRYPTION_KEY: str = "your-32-byte-encryption-key-here-change-in-prod"
    
    # Region Configuration
    PRIMARY_REGION: str = "us-east"
    SECONDARY_REGIONS: List[str] = ["eu-west", "ap-south"]
    
    # Health Thresholds
    LATENCY_THRESHOLD_MS: int = 500
    ERROR_RATE_THRESHOLD: float = 0.01
    
    # RTO/RPO Targets
    RTO_TARGET_SECONDS: int = 60
    RPO_TARGET_SECONDS: int = 30
    
    # Compliance
    GDPR_ENABLED: bool = True
    CCPA_ENABLED: bool = True
    AUDIT_LOG_RETENTION_DAYS: int = 2555  # 7 years
    
    class Config:
        env_file = ".env"

settings = Settings()
