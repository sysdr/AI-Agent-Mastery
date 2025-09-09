"""
Secure Code Analysis Agent - Main FastAPI Application
Production-ready security scanning system
"""

import os
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException, Depends, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import JSONResponse
import uvicorn

from app.core.config import get_settings
from app.api.routes import security, git, analysis, websocket
from app.services.security_engine import SecurityEngine
from app.services.git_service import GitService
from app.services.ai_service import AIService

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Global services
security_engine = None
git_service = None
ai_service = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Application lifespan management"""
    global security_engine, git_service, ai_service
    
    settings = get_settings()
    
    # Initialize services
    security_engine = SecurityEngine()
    git_service = GitService()
    ai_service = AIService(settings.gemini_api_key)
    
    logger.info("🔒 Secure Code Analysis Agent started")
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down services")

# Create FastAPI app
app = FastAPI(
    title="Secure Code Analysis Agent",
    description="Production-ready AI-powered code security scanner",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(security.router, prefix="/api/security", tags=["security"])
app.include_router(git.router, prefix="/api/git", tags=["git"])
app.include_router(analysis.router, prefix="/api/analysis", tags=["analysis"])
app.include_router(websocket.router, prefix="/ws", tags=["websocket"])

@app.get("/")
async def root():
    return {"message": "Secure Code Analysis Agent API", "status": "active"}

@app.get("/health")
async def health_check():
    return {"status": "healthy", "services": ["security", "git", "ai"]}

# Global exception handler
@app.exception_handler(Exception)
async def global_exception_handler(request, exc):
    logger.error(f"Global exception: {exc}")
    return JSONResponse(
        status_code=500,
        content={"detail": "Internal server error"}
    )

if __name__ == "__main__":
    settings = get_settings()
    uvicorn.run(
        "app.main:app",
        host=settings.host,
        port=settings.port,
        reload=settings.debug,
        log_level="info"
    )
