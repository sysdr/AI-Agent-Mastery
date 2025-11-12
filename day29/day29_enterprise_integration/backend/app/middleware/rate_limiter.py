from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request, HTTPException, status
from fastapi.responses import JSONResponse
import time
from collections import defaultdict
import asyncio
import os

class RateLimitMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.requests = defaultdict(list)
        self.lock = asyncio.Lock()
        self.legacy_limit = int(os.getenv("LEGACY_RATE_LIMIT", "10"))
        self.modern_limit = int(os.getenv("MODERN_RATE_LIMIT", "1000"))
    
    async def dispatch(self, request: Request, call_next):
        # Determine if this is a legacy system request
        is_legacy = "/legacy/" in request.url.path
        # Exclude health check endpoints from strict rate limiting
        is_health_check = "/health" in request.url.path
        limit = self.legacy_limit if is_legacy else self.modern_limit
        # Increase limit for health checks to allow monitoring
        if is_health_check:
            limit = limit * 10  # 10x limit for health checks
        
        client_id = request.client.host
        current_time = time.time()
        window_start = current_time - 60  # 1-minute window
        
        async with self.lock:
            # Clean old requests
            self.requests[client_id] = [
                req_time for req_time in self.requests[client_id]
                if req_time > window_start
            ]
            
            # Check rate limit
            if len(self.requests[client_id]) >= limit:
                # Create response with CORS headers
                response = JSONResponse(
                    status_code=status.HTTP_429_TOO_MANY_REQUESTS,
                    content={
                        "detail": f"Rate limit exceeded: {limit} requests per minute",
                        "system_type": "legacy" if is_legacy else "modern"
                    }
                )
                # Add CORS headers manually since we're returning early
                origin = request.headers.get("origin")
                if origin and origin in ["http://localhost:3000", "http://localhost:5173"]:
                    response.headers["Access-Control-Allow-Origin"] = origin
                    response.headers["Access-Control-Allow-Credentials"] = "true"
                    response.headers["Access-Control-Allow-Methods"] = "*"
                    response.headers["Access-Control-Allow-Headers"] = "*"
                return response
            
            self.requests[client_id].append(current_time)
        
        response = await call_next(request)
        response.headers["X-RateLimit-Limit"] = str(limit)
        response.headers["X-RateLimit-Remaining"] = str(limit - len(self.requests[client_id]))
        
        return response
