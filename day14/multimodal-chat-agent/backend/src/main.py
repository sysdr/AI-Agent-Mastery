"""
Multi-Modal Chat Agent - Main Application
Day 14: Production Integration & Monitoring
"""

import asyncio
import logging
import os
from contextlib import asynccontextmanager
from typing import Dict, Any

import structlog
from fastapi import FastAPI, HTTPException, Depends, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import StreamingResponse
from fastapi.security import HTTPBearer
import uvicorn
from prometheus_client import Counter, Histogram, Gauge, generate_latest
from starlette.responses import Response
from starlette.middleware.base import BaseHTTPMiddleware

from agents.multimodal_agent import MultiModalAgent
from monitoring.metrics_collector import MetricsCollector
from monitoring.audit_logger import AuditLogger
from security.input_validator import InputValidator
from security.auth_manager import AuthManager
from utils.database import Database
from utils.redis_client import RedisClient
from models.schemas import ChatMessage, ChatResponse, SystemMetrics

# Initialize structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    wrapper_class=structlog.stdlib.BoundLogger,
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

# Prometheus metrics
REQUESTS_TOTAL = Counter('chat_requests_total', 'Total chat requests', ['method', 'endpoint'])
REQUEST_DURATION = Histogram('chat_request_duration_seconds', 'Request duration in seconds')
ACTIVE_CONNECTIONS = Gauge('chat_active_connections', 'Active WebSocket connections')
TOKEN_USAGE = Counter('gemini_tokens_used', 'Total tokens consumed', ['model'])
SECURITY_EVENTS = Counter('security_events_total', 'Security events detected', ['event_type'])

class SecurityMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request, call_next):
        start_time = asyncio.get_event_loop().time()
        
        # Security validation
        validator = InputValidator()
        if request.method == "POST":
            # Basic security checks
            if not await validator.validate_request_headers(request.headers):
                SECURITY_EVENTS.labels(event_type='invalid_headers').inc()
                raise HTTPException(status_code=400, detail="Invalid request headers")
        
        response = await call_next(request)
        
        # Record metrics
        process_time = asyncio.get_event_loop().time() - start_time
        REQUEST_DURATION.observe(process_time)
        REQUESTS_TOTAL.labels(method=request.method, endpoint=request.url.path).inc()
        
        return response

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan manager"""
    # Startup
    logger.info("Starting Multi-Modal Chat Agent...")
    
    # Initialize components
    await Database.initialize()
    await RedisClient.initialize()
    
    # Start background tasks
    metrics_collector = MetricsCollector()
    asyncio.create_task(metrics_collector.start_collection())
    
    logger.info("Application started successfully")
    yield
    
    # Shutdown
    logger.info("Shutting down...")
    await Database.close()
    await RedisClient.close()

# Create FastAPI application
app = FastAPI(
    title="Multi-Modal Chat Agent",
    description="Production-grade chat agent with monitoring and security",
    version="1.0.0",
    lifespan=lifespan
)

# Add middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
app.add_middleware(SecurityMiddleware)

# Security
security = HTTPBearer()

# Initialize components
multimodal_agent = MultiModalAgent()
audit_logger = AuditLogger()
auth_manager = AuthManager()

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {"status": "healthy", "timestamp": asyncio.get_event_loop().time()}

@app.get("/metrics")
async def get_metrics():
    """Prometheus metrics endpoint"""
    return Response(generate_latest(), media_type="text/plain")

@app.post("/chat", response_model=ChatResponse)
async def chat_endpoint(
    message: ChatMessage,
    token: str = Depends(security)
):
    """Main chat endpoint with security and monitoring"""
    try:
        # Authenticate user
        user = await auth_manager.verify_token(token.credentials)
        
        # Validate input
        validator = InputValidator()
        if not await validator.validate_chat_input(message.content):
            SECURITY_EVENTS.labels(event_type='invalid_input').inc()
            raise HTTPException(status_code=400, detail="Invalid input detected")
        
        # Process with agent
        response = await multimodal_agent.process_message(
            content=message.content,
            user_id=user.id,
            conversation_id=message.conversation_id
        )
        
        # Log audit trail
        await audit_logger.log_interaction(
            user_id=user.id,
            action="chat",
            content=message.content,
            response=response.content,
            metadata={"tokens_used": response.tokens_used}
        )
        
        # Update metrics
        TOKEN_USAGE.labels(model="gemini-pro").inc(response.tokens_used)
        
        return response
        
    except Exception as e:
        logger.error("Chat processing error", error=str(e))
        raise HTTPException(status_code=500, detail="Internal server error")

@app.post("/chat/upload")
async def upload_and_chat(
    file: UploadFile = File(...),
    message: str = "",
    token: str = Depends(security)
):
    """Upload file and chat endpoint"""
    try:
        # Authenticate user
        user = await auth_manager.verify_token(token.credentials)
        
        # Validate file
        validator = InputValidator()
        if not await validator.validate_file_upload(file):
            SECURITY_EVENTS.labels(event_type='invalid_file').inc()
            raise HTTPException(status_code=400, detail="Invalid file upload")
        
        # Process with multimodal agent
        response = await multimodal_agent.process_file_message(
            file=file,
            message=message,
            user_id=user.id
        )
        
        # Log audit trail
        await audit_logger.log_interaction(
            user_id=user.id,
            action="file_upload",
            content=f"File: {file.filename}, Message: {message}",
            response=response.content,
            metadata={
                "filename": file.filename,
                "file_size": file.size,
                "tokens_used": response.tokens_used
            }
        )
        
        return response
        
    except Exception as e:
        logger.error("File upload error", error=str(e))
        raise HTTPException(status_code=500, detail="File processing error")

@app.get("/analytics/metrics")
async def get_system_metrics(token: str = Depends(security)) -> SystemMetrics:
    """Get system performance metrics"""
    user = await auth_manager.verify_token(token.credentials)
    
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    metrics_collector = MetricsCollector()
    return await metrics_collector.get_system_metrics()

@app.get("/analytics/audit")
async def get_audit_logs(
    limit: int = 100,
    offset: int = 0,
    token: str = Depends(security)
):
    """Get audit logs for compliance"""
    user = await auth_manager.verify_token(token.credentials)
    
    if not user.is_admin:
        raise HTTPException(status_code=403, detail="Admin access required")
    
    return await audit_logger.get_logs(limit=limit, offset=offset)

if __name__ == "__main__":
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=None
    )
