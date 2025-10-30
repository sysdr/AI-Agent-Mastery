import os
import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.responses import JSONResponse
import uvicorn
from dotenv import load_dotenv

from gateway.core import Gateway
from auth.manager import AuthManager
from security.threat_detector import ThreatDetector
from monitoring.metrics import MetricsCollector
from utils.logger import setup_logging

load_dotenv()

# Global instances
gateway = None
auth_manager = None
threat_detector = None
metrics = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global gateway, auth_manager, threat_detector, metrics
    
    logger = setup_logging()
    logger.info("Starting AI Agent Gateway...")
    
    # Initialize components
    metrics = MetricsCollector()
    auth_manager = AuthManager()
    threat_detector = ThreatDetector()
    gateway = Gateway(auth_manager, threat_detector, metrics)
    
    await gateway.initialize()
    logger.info("Gateway initialized successfully")
    
    yield
    
    # Shutdown
    if gateway:
        await gateway.shutdown()
    logger.info("Gateway shutdown complete")

# Create FastAPI app
app = FastAPI(
    title="AI Agent Enterprise Gateway",
    description="Production-grade API gateway with advanced security",
    version="1.0.0",
    lifespan=lifespan
)

# Security middleware
app.add_middleware(TrustedHostMiddleware, allowed_hosts=["localhost", "127.0.0.1"])
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.middleware("http")
async def security_middleware(request: Request, call_next):
    """Main security middleware pipeline"""
    if not gateway:
        raise HTTPException(status_code=503, detail="Gateway not initialized")
    
    # Process request through gateway
    response = await gateway.process_request(request, call_next)
    return response

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": asyncio.get_event_loop().time()}

@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    if metrics:
        return metrics.get_metrics()
    return {"error": "Metrics not available"}

@app.get("/favicon.ico")
async def favicon():
    """Favicon endpoint"""
    return JSONResponse(content={"message": "No favicon"}, status_code=404)

@app.post("/auth/login")
async def login(request: Request):
    """Authentication endpoint"""
    body = await request.json()
    print(f"Login attempt: {body}")  # Debug log
    username = body.get("username")
    password = body.get("password")
    print(f"Username: {username}, Password: {password}")
    
    if not auth_manager:
        raise HTTPException(status_code=503, detail="Auth manager not available")
    
    result = await auth_manager.authenticate(username, password)
    print(f"Authentication result: {result is not None}")  # Debug log
    if result:
        return result
    raise HTTPException(status_code=401, detail="Authentication failed")

@app.post("/auth/refresh")
async def refresh_token(request: Request):
    """Token refresh endpoint"""
    body = await request.json()
    if not auth_manager:
        raise HTTPException(status_code=503, detail="Auth manager not available")
    
    result = await auth_manager.refresh_token(body.get("refresh_token"))
    if result:
        return result
    raise HTTPException(status_code=401, detail="Token refresh failed")

# AI Agent proxy routes
@app.api_route("/api/{path:path}", methods=["GET", "POST", "PUT", "DELETE", "PATCH"])
async def proxy_to_agents(path: str, request: Request):
    """Proxy requests to AI agents"""
    if not gateway:
        raise HTTPException(status_code=503, detail="Gateway not available")
    
    return await gateway.proxy_request(path, request)

if __name__ == "__main__":
    port = int(os.getenv("GATEWAY_PORT", 8080))
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=port,
        reload=True,
        log_level="info"
    )
