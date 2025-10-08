import time
from collections import defaultdict
from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
from config.settings import settings

class RateLimiterMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.request_counts = defaultdict(list)
    
    async def dispatch(self, request: Request, call_next):
        client_ip = request.client.host
        current_time = time.time()
        
        # Clean old requests
        self.request_counts[client_ip] = [
            req_time for req_time in self.request_counts[client_ip]
            if current_time - req_time < settings.rate_limit_window
        ]
        
        # Check rate limit
        if len(self.request_counts[client_ip]) >= settings.rate_limit_requests:
            raise HTTPException(status_code=429, detail="Rate limit exceeded")
        
        # Record current request
        self.request_counts[client_ip].append(current_time)
        
        response = await call_next(request)
        return response
