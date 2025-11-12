from fastapi import FastAPI, Request
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from contextlib import asynccontextmanager
import logging
from pythonjsonlogger import jsonlogger
from prometheus_client import make_asgi_app
import time

from app.api.endpoints import integration, legacy, audit, health
from app.middleware.rate_limiter import RateLimitMiddleware
from app.middleware.circuit_breaker import CircuitBreakerMiddleware
from app.middleware.tracing import TracingMiddleware
from app.services.integration.event_sourcing import event_store
from app.services.integration.cache_service import cache_service
from app.utils.database import init_db, close_db

# Configure JSON logging
logHandler = logging.StreamHandler()
formatter = jsonlogger.JsonFormatter('%(asctime)s %(name)s %(levelname)s %(message)s')
logHandler.setFormatter(formatter)
logger = logging.getLogger()
logger.addHandler(logHandler)
logger.setLevel(logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    """Startup and shutdown events"""
    logger.info("Starting Enterprise Integration Platform")
    await init_db()
    await event_store.initialize()
    await cache_service.initialize()
    yield
    logger.info("Shutting down Enterprise Integration Platform")
    await event_store.close()
    await cache_service.close()
    await close_db()

app = FastAPI(
    title="Enterprise Integration Platform",
    description="Legacy System Integration with Event Sourcing",
    version="1.0.0",
    lifespan=lifespan
)

# CORS Configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Custom Middleware
app.add_middleware(TracingMiddleware)
app.add_middleware(CircuitBreakerMiddleware)
app.add_middleware(RateLimitMiddleware)

# Request logging middleware
@app.middleware("http")
async def log_requests(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    duration = time.time() - start_time
    logger.info(
        "Request processed",
        extra={
            "method": request.method,
            "path": request.url.path,
            "status_code": response.status_code,
            "duration_ms": round(duration * 1000, 2)
        }
    )
    return response

# Exception handlers
@app.exception_handler(Exception)
async def global_exception_handler(request: Request, exc: Exception):
    logger.error(f"Unhandled exception: {str(exc)}", exc_info=True)
    response = JSONResponse(
        status_code=500,
        content={"detail": "Internal server error", "error": str(exc)}
    )
    # Ensure CORS headers are included in error responses
    origin = request.headers.get("origin")
    if origin and origin in ["http://localhost:3000", "http://localhost:3001", "http://localhost:5173"]:
        response.headers["Access-Control-Allow-Origin"] = origin
        response.headers["Access-Control-Allow-Credentials"] = "true"
        response.headers["Access-Control-Allow-Methods"] = "*"
        response.headers["Access-Control-Allow-Headers"] = "*"
    return response

# Include routers
app.include_router(health.router, prefix="/api/v1/health", tags=["Health"])
app.include_router(integration.router, prefix="/api/v1/integration", tags=["Integration"])
app.include_router(legacy.router, prefix="/api/v1/legacy", tags=["Legacy"])
app.include_router(audit.router, prefix="/api/v1/audit", tags=["Audit"])

# Prometheus metrics endpoint
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.get("/")
async def root():
    return {
        "service": "Enterprise Integration Platform",
        "version": "1.0.0",
        "status": "operational"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_config=None
    )
