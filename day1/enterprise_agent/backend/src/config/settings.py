import os
from pathlib import Path
from typing import Optional
from dotenv import load_dotenv

class Settings:
    def __init__(self):
        # Load environment variables from .env file
        # Look for .env in the project root (parent of backend directory)
        project_root = Path(__file__).parent.parent.parent.parent
        env_path = project_root / ".env"
        if env_path.exists():
            load_dotenv(env_path)
        
        # Environment
        self.agent_env = os.getenv("AGENT_ENV", "development")
        
        # API Keys
        self.gemini_api_key = os.getenv("GEMINI_API_KEY")
        
        # Security
        self.encryption_key = os.getenv("ENCRYPTION_KEY")
        
        # Logging
        self.log_level = os.getenv("LOG_LEVEL", "INFO")
        
        # Database
        self.db_path = Path("data/agent.db")
        self.db_path.parent.mkdir(exist_ok=True)
        
        # Logging
        self.log_file = Path("logs/agent.log")
        self.log_file.parent.mkdir(exist_ok=True)
        
        # Debug mode
        self.debug = self.agent_env == "development"
        
        # API Configuration
        self.api_host = "0.0.0.0"
        self.api_port = 8000
        
        # Frontend Configuration
        self.frontend_url = "http://localhost:3000"

# Global settings instance
settings = Settings()
