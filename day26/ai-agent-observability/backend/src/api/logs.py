from fastapi import APIRouter, Query
from typing import List, Dict, Optional
from services.logging_service import LoggingService

router = APIRouter()
logging_service = LoggingService()

@router.get("/")
async def get_logs(
    level: Optional[str] = Query(None, description="Filter by log level"),
    start_time: Optional[str] = Query(None, description="Filter by start time"),
    limit: int = Query(100, ge=1, le=1000, description="Limit results")
) -> List[Dict]:
    """Get logs with optional filtering"""
    return await logging_service.get_logs(level, start_time, limit)

@router.get("/search")
async def search_logs(
    query: str = Query(..., description="Search query"),
    limit: int = Query(50, ge=1, le=1000)
) -> List[Dict]:
    """Search logs by query string"""
    return await logging_service.search_logs(query, limit)

@router.post("/")
async def create_log(level: str, message: str, context: Dict = None) -> Dict:
    """Create a log entry"""
    await logging_service.log(level, message, context)
    return {"status": "logged"}
