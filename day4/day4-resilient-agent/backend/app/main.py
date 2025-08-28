from fastapi import FastAPI, HTTPException, Depends, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from contextlib import asynccontextmanager
import redis.asyncio as redis
import logging
from .core.config import settings
from .api import router
from .core.rate_limiter import DistributedRateLimiter
from .core.session_manager import SessionManager

# Configure logging
logging.basicConfig(level=getattr(logging, settings.LOG_LEVEL))
logger = logging.getLogger(__name__)

# Global dependencies
redis_client = None
rate_limiter = None
session_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global redis_client, rate_limiter, session_manager
    
    # Startup
    logger.info("🚀 Starting Resilient Agent...")
    redis_client = redis.from_url(settings.REDIS_URL)
    rate_limiter = DistributedRateLimiter(redis_client)
    session_manager = SessionManager(redis_client)
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down gracefully...")
    await redis_client.close()

app = FastAPI(
    title="Resilient Price Monitor Agent",
    description="Production-grade web agent with resilience patterns",
    version="1.0.0",
    lifespan=lifespan
)

# Security middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])

# Include routers
app.include_router(router.api_router, prefix="/api/v1")

@app.get("/health")
async def health_check():
    """Health check endpoint for load balancers"""
    try:
        await redis_client.ping()
        return {"status": "healthy", "redis": "connected"}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Redis unhealthy: {str(e)}")

@app.get("/")
async def root():
    return {"message": "Resilient Agent API", "version": "1.0.0"}
