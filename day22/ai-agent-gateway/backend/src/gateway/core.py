import asyncio
import time
import json
import httpx
from typing import Dict, Any, Optional
from fastapi import Request, Response, HTTPException
from fastapi.responses import JSONResponse
import structlog

from auth.manager import AuthManager
from security.threat_detector import ThreatDetector
from monitoring.metrics import MetricsCollector
from security.rate_limiting import RateLimiter

logger = structlog.get_logger()

class Gateway:
    def __init__(self, auth_manager: AuthManager, threat_detector: ThreatDetector, metrics: MetricsCollector):
        self.auth_manager = auth_manager
        self.threat_detector = threat_detector
        self.metrics = metrics
        self.rate_limiter = None
        self.client = None
        self.circuit_breakers = {}
        
    async def initialize(self):
        """Initialize gateway components"""
        self.rate_limiter = RateLimiter()
        self.client = httpx.AsyncClient(timeout=30.0)
        logger.info("Gateway core initialized")
        
    async def shutdown(self):
        """Cleanup gateway resources"""
        if self.client:
            await self.client.aclose()
            
    async def process_request(self, request: Request, call_next):
        """Main request processing pipeline"""
        start_time = time.time()
        client_ip = request.client.host
        
        try:
            # Step 1: Threat detection
            threat_score = await self.threat_detector.analyze_request(request)
            if threat_score > 0.8:
                logger.warning(f"High threat score {threat_score} from {client_ip}")
                self.metrics.increment_threat_blocked()
                raise HTTPException(status_code=403, detail="Request blocked by security policy")
            
            # Step 2: Authentication (skip for public endpoints)
            if not self._is_public_endpoint(request.url.path):
                auth_result = await self.auth_manager.validate_request(request)
                if not auth_result:
                    raise HTTPException(status_code=401, detail="Authentication required")
                request.state.user = auth_result
            
            # Step 3: Rate limiting
            if not await self.rate_limiter.check_limit(client_ip, request.url.path):
                logger.warning(f"Rate limit exceeded for {client_ip}")
                self.metrics.increment_rate_limited()
                raise HTTPException(status_code=429, detail="Rate limit exceeded")
            
            # Step 4: Process request
            response = await call_next(request)
            
            # Step 5: Post-process response
            response.headers["X-Gateway-Version"] = "1.0.0"
            response.headers["X-Content-Type-Options"] = "nosniff"
            response.headers["X-Frame-Options"] = "DENY"
            
            # Record metrics
            duration = time.time() - start_time
            self.metrics.record_request(request.url.path, response.status_code, duration)
            
            return response
            
        except HTTPException:
            raise
        except Exception as e:
            logger.error(f"Gateway error: {str(e)}")
            self.metrics.increment_errors()
            return JSONResponse(
                status_code=500,
                content={"error": "Internal gateway error"}
            )
    
    def _is_public_endpoint(self, path: str) -> bool:
        """Check if endpoint requires authentication"""
        public_paths = [
            "/health", 
            "/metrics", 
            "/auth/login", 
            "/docs", 
            "/openapi.json",
            "/manifest.json",
            "/favicon.ico",
            "/static/",
            "/assets/"
        ]
        return any(path.startswith(p) for p in public_paths)
    
    async def proxy_request(self, path: str, request: Request):
        """Proxy requests to backend services"""
        # Simple proxy implementation - in production, use service discovery
        backend_url = f"http://localhost:8081/api/{path}"
        
        try:
            # Forward request to backend
            body = await request.body() if request.method in ["POST", "PUT", "PATCH"] else None
            
            response = await self.client.request(
                method=request.method,
                url=backend_url,
                headers=dict(request.headers),
                content=body,
                params=dict(request.query_params)
            )
            
            return JSONResponse(
                content=response.json(),
                status_code=response.status_code,
                headers=dict(response.headers)
            )
            
        except Exception as e:
            logger.error(f"Proxy error: {str(e)}")
            return JSONResponse(
                status_code=502,
                content={"error": "Backend service unavailable"}
            )
