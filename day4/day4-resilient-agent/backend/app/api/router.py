from fastapi import APIRouter
from .endpoints import monitoring, health, auth

api_router = APIRouter()

api_router.include_router(monitoring.router, prefix="/monitoring", tags=["monitoring"])
api_router.include_router(health.router, prefix="/health", tags=["health"])
api_router.include_router(auth.router, prefix="/auth", tags=["auth"])
