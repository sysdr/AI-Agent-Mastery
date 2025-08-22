import os
from pathlib import Path
from cryptography.fernet import Fernet

class Settings:
    def __init__(self):
        self.base_dir = Path(__file__).parent.parent
        self.data_dir = self.base_dir / "data"
        self.logs_dir = self.base_dir / "logs"
        
        # Create directories if they don't exist
        self.data_dir.mkdir(exist_ok=True)
        self.logs_dir.mkdir(exist_ok=True)
        
        # Environment settings
        self.environment = os.getenv("AGENT_ENV", "development")
        self.debug = self.environment != "production"
        
        # Security settings
        self.encryption_key = os.getenv("ENCRYPTION_KEY", Fernet.generate_key())
        if isinstance(self.encryption_key, str):
            self.encryption_key = self.encryption_key.encode()
            
        # Gemini API settings
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "your-api-key-here")
        
        # Database settings
        self.db_path = self.data_dir / "agent_state.db"
        
        # Logging settings
        self.log_level = "DEBUG" if self.debug else "INFO"
        self.log_file = self.logs_dir / "agent.log"

settings = Settings()
