import secrets
import time
import json
from typing import Optional, Dict, Any
import hashlib
from fastapi import Request, Response, HTTPException
import redis.asyncio as redis

class SessionManager:
    def __init__(self, redis_client: redis.Redis, session_timeout: int = 3600):
        self.redis = redis_client
        self.session_timeout = session_timeout
        self.session_prefix = "session:"
        self.csrf_prefix = "csrf:"
    
    def generate_session_id(self) -> str:
        """Generate cryptographically secure session ID"""
        return secrets.token_urlsafe(32)
    
    def generate_csrf_token(self) -> str:
        """Generate CSRF token"""
        return secrets.token_urlsafe(32)
    
    async def create_session(self, user_data: Dict[str, Any], response: Response) -> str:
        """Create new session with CSRF protection"""
        session_id = self.generate_session_id()
        csrf_token = self.generate_csrf_token()
        
        session_data = {
            "user_data": user_data,
            "csrf_token": csrf_token,
            "created_at": time.time(),
            "last_accessed": time.time()
        }
        
        # Store session in Redis
        await self.redis.setex(
            f"{self.session_prefix}{session_id}",
            self.session_timeout,
            json.dumps(session_data)
        )
        
        # Set secure cookie
        response.set_cookie(
            key="session_id",
            value=session_id,
            max_age=self.session_timeout,
            httponly=True,
            secure=True,
            samesite="strict"
        )
        
        return session_id
    
    async def get_session(self, request: Request) -> Optional[Dict[str, Any]]:
        """Retrieve and validate session"""
        session_id = request.cookies.get("session_id")
        if not session_id:
            return None
        
        session_data = await self.redis.get(f"{self.session_prefix}{session_id}")
        if not session_data:
            return None
        
        try:
            data = json.loads(session_data)
            # Update last accessed time
            data["last_accessed"] = time.time()
            await self.redis.setex(
                f"{self.session_prefix}{session_id}",
                self.session_timeout,
                json.dumps(data)
            )
            return data
        except json.JSONDecodeError:
            return None
    
    async def validate_csrf(self, request: Request, csrf_token: str) -> bool:
        """Validate CSRF token"""
        session = await self.get_session(request)
        if not session:
            return False
        
        return session.get("csrf_token") == csrf_token
    
    async def destroy_session(self, request: Request, response: Response) -> bool:
        """Destroy session"""
        session_id = request.cookies.get("session_id")
        if not session_id:
            return False
        
        await self.redis.delete(f"{self.session_prefix}{session_id}")
        response.delete_cookie("session_id")
        return True
