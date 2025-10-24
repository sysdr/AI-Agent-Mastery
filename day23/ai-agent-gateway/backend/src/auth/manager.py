import jwt
import bcrypt
import time
import secrets
from typing import Optional, Dict, Any
from fastapi import Request
import structlog

logger = structlog.get_logger()

class AuthManager:
    def __init__(self):
        self.secret_key = "your-jwt-secret-key"
        self.algorithm = "HS256"
        self.token_expiry = 3600  # 1 hour
        self.users_db = {
            "admin": {
                "password_hash": b"$2b$12$1uUOWRFmzai4f5PojU.FI.zBpN2xcHwAj/wS9ckWl3.pC2BdHlqSu",
                "role": "admin",
                "permissions": ["read", "write", "admin"]
            },
            "user": {
                "password_hash": b"$2b$12$1uUOWRFmzai4f5PojU.FI.3XlBijzzyW3grdgl8gFxtcRDPmc74we",
                "role": "user", 
                "permissions": ["read"]
            }
        }
        self.api_keys = {}
        
    async def authenticate(self, username: str, password: str) -> Optional[Dict[str, Any]]:
        """Authenticate user with username/password"""
        try:
            logger.info(f"Attempting authentication for user: {username}")
            if username not in self.users_db:
                logger.warning(f"User {username} not found in database")
                return None
                
            user = self.users_db[username]
            password_check = bcrypt.checkpw(password.encode(), user["password_hash"])
            logger.info(f"Password check result: {password_check}")
            if not password_check:
                logger.warning(f"Password check failed for user: {username}")
                return None
            
            # Generate tokens
            access_token = self._create_access_token(username, user["role"], user["permissions"])
            refresh_token = self._create_refresh_token(username)
            
            logger.info(f"User {username} authenticated successfully")
            
            return {
                "access_token": access_token,
                "refresh_token": refresh_token,
                "token_type": "bearer",
                "expires_in": self.token_expiry,
                "user": {
                    "username": username,
                    "role": user["role"],
                    "permissions": user["permissions"]
                }
            }
            
        except Exception as e:
            logger.error(f"Authentication error: {str(e)}")
            return None
    
    async def validate_request(self, request: Request) -> Optional[Dict[str, Any]]:
        """Validate request authentication"""
        try:
            # Check for JWT token
            auth_header = request.headers.get("Authorization")
            if auth_header and auth_header.startswith("Bearer "):
                token = auth_header.split(" ")[1]
                return self._validate_jwt_token(token)
            
            # Check for API key
            api_key = request.headers.get("X-API-Key")
            if api_key:
                return self._validate_api_key(api_key)
                
            return None
            
        except Exception as e:
            logger.error(f"Token validation error: {str(e)}")
            return None
    
    def _create_access_token(self, username: str, role: str, permissions: list) -> str:
        """Create JWT access token"""
        payload = {
            "sub": username,
            "role": role,
            "permissions": permissions,
            "iat": int(time.time()),
            "exp": int(time.time() + self.token_expiry),
            "type": "access"
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def _create_refresh_token(self, username: str) -> str:
        """Create JWT refresh token"""
        payload = {
            "sub": username,
            "iat": int(time.time()),
            "exp": int(time.time() + (7 * 24 * 3600)),  # 7 days
            "type": "refresh"
        }
        return jwt.encode(payload, self.secret_key, algorithm=self.algorithm)
    
    def _validate_jwt_token(self, token: str) -> Optional[Dict[str, Any]]:
        """Validate JWT token"""
        try:
            payload = jwt.decode(token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != "access":
                return None
                
            return {
                "username": payload["sub"],
                "role": payload["role"],
                "permissions": payload["permissions"],
                "token_type": "jwt"
            }
            
        except jwt.ExpiredSignatureError:
            logger.warning("Token expired")
            return None
        except jwt.InvalidTokenError:
            logger.warning("Invalid token")
            return None
    
    def _validate_api_key(self, api_key: str) -> Optional[Dict[str, Any]]:
        """Validate API key"""
        if api_key in self.api_keys:
            key_info = self.api_keys[api_key]
            return {
                "username": key_info["username"],
                "role": key_info["role"],
                "permissions": key_info["permissions"],
                "token_type": "api_key"
            }
        return None
    
    async def refresh_token(self, refresh_token: str) -> Optional[Dict[str, Any]]:
        """Refresh access token"""
        try:
            payload = jwt.decode(refresh_token, self.secret_key, algorithms=[self.algorithm])
            if payload.get("type") != "refresh":
                return None
            
            username = payload["sub"]
            if username not in self.users_db:
                return None
            
            user = self.users_db[username]
            access_token = self._create_access_token(username, user["role"], user["permissions"])
            
            return {
                "access_token": access_token,
                "token_type": "bearer",
                "expires_in": self.token_expiry
            }
            
        except jwt.ExpiredSignatureError:
            return None
        except jwt.InvalidTokenError:
            return None
