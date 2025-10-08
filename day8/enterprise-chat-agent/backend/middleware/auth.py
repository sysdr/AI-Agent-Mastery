from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import jwt
from config.settings import Settings

settings = Settings()

class AuthMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Skip auth for health check and auth endpoints
        if request.url.path in ["/health", "/auth/login", "/docs", "/openapi.json"]:
            return await call_next(request)
        
        # Check for WebSocket upgrades (handled in endpoint)
        if request.headers.get("upgrade") == "websocket":
            return await call_next(request)
        
        # Validate JWT token
        auth_header = request.headers.get("authorization")
        if not auth_header or not auth_header.startswith("Bearer "):
            raise HTTPException(status_code=401, detail="Missing or invalid authorization header")
        
        try:
            token = auth_header.split(" ")[1]
            payload = jwt.decode(token, settings.secret_key, algorithms=["HS256"])
            request.state.user_id = payload.get("user_id")
            request.state.tenant_id = payload.get("tenant_id")
        except jwt.InvalidTokenError:
            raise HTTPException(status_code=401, detail="Invalid token")
        
        return await call_next(request)
