from fastapi import FastAPI, HTTPException, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import structlog
from app.core.config import settings
from app.api import memory, analytics, security
from app.db.database import init_db
from app.core.logging import setup_logging

security_scheme = HTTPBearer()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    setup_logging()
    await init_db()
    yield
    # Shutdown
    pass

app = FastAPI(
    title="Secure Memory Agent API",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=settings.CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(memory.router, prefix="/api/memory", tags=["memory"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["analytics"])
app.include_router(security.router, prefix="/api/security", tags=["security"])

@app.get("/")
async def root():
    return {"message": "Secure Memory Agent API", "version": "1.0.0"}

@app.get("/health")
async def health():
    return {"status": "healthy"}
