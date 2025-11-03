import os
from typing import List

class Settings:
    # API Configuration
    API_HOST = os.getenv("API_HOST", "0.0.0.0")
    API_PORT = int(os.getenv("API_PORT", 8000))
    
    # Gemini AI Configuration
    GEMINI_API_KEY = "AIzaSyDGswqDT4wQw_bd4WZtIgYAawRDZ0Gisn8"
    
    # Security Settings
    SECRET_KEY = os.getenv("SECRET_KEY", "your-secret-key-for-jwt-signing")
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    
    # Database
    DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://qa_user:qa_password@localhost/qa_platform")
    
    # Redis for Celery
    REDIS_URL = os.getenv("REDIS_URL", "redis://localhost:6379/0")
    
    # Security Scanning
    SECURITY_SCAN_INTERVAL = 300  # 5 minutes
    VULNERABILITY_THRESHOLD = 7.0  # CVSS score threshold
    
    # Load Testing
    LOAD_TEST_USERS = 100
    LOAD_TEST_SPAWN_RATE = 10
    LOAD_TEST_DURATION = 300
    
    # Quality Gates
    PERFORMANCE_THRESHOLD_MS = 200
    ERROR_RATE_THRESHOLD = 0.01
    COVERAGE_THRESHOLD = 0.80

settings = Settings()
