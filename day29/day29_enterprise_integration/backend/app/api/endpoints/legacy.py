from fastapi import APIRouter, HTTPException
from app.services.legacy.legacy_connector import legacy_connector
from pydantic import BaseModel

router = APIRouter()

class LegacyHealthRequest(BaseModel):
    healthy: bool

@router.get("/health")
async def get_legacy_health():
    """Get legacy system health status"""
    return {
        "healthy": legacy_connector.is_healthy,
        "response_time_ms": legacy_connector.response_time_ms
    }

@router.post("/health")
async def set_legacy_health(request: LegacyHealthRequest):
    """Set legacy system health (for testing)"""
    legacy_connector.set_health(request.healthy)
    return {
        "status": "updated",
        "healthy": request.healthy
    }
