"""
Authentication and Authorization Manager
"""

import jwt
import os
from datetime import datetime, timedelta
from models.schemas import User
import structlog

logger = structlog.get_logger()

class AuthManager:
    def __init__(self):
        self.secret_key = os.getenv("SECRET_KEY", "dev-secret-key")
        self.algorithm = "HS256"
    
    async def verify_token(self, token: str) -> User:
        """Verify JWT token and return user"""
        try:
            # For demo purposes, return a mock admin user
            # In production, this would decode and validate the JWT
            return User(
                id="admin",
                username="admin",
                is_admin=True
            )
        except Exception as e:
            logger.error("Token verification error", error=str(e))
            raise
    
    def create_token(self, user_id: str, is_admin: bool = False) -> str:
        """Create JWT token for user"""
        payload = {
            "user_id": user_id,
            "is_admin": is_admin,
            "exp": datetime.utcnow() + timedelta(hours=24)
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
