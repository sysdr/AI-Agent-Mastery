from fastapi import APIRouter, HTTPException
from typing import List, Dict, Optional
from services.tracing_service import TracingService

router = APIRouter()
tracing_service = TracingService()

@router.get("/")
async def get_traces(limit: int = 50) -> List[Dict]:
    """Get recent traces"""
    return await tracing_service.get_recent_traces(limit)

@router.get("/{trace_id}")
async def get_trace_details(trace_id: str) -> Dict:
    """Get detailed trace information"""
    trace = await tracing_service.get_trace_details(trace_id)
    if not trace:
        raise HTTPException(status_code=404, detail="Trace not found")
    return trace

@router.post("/start")
async def start_trace(operation: str, metadata: Optional[Dict] = None) -> Dict:
    """Start a new distributed trace"""
    trace_id = await tracing_service.start_trace(operation, metadata)
    return {"trace_id": trace_id, "status": "started"}

@router.post("/{trace_id}/spans")
async def add_span(trace_id: str, span_name: str, 
                  duration_ms: Optional[float] = None, 
                  metadata: Optional[Dict] = None) -> Dict:
    """Add a span to an existing trace"""
    await tracing_service.add_span(trace_id, span_name, duration_ms, metadata)
    return {"status": "span_added"}

@router.post("/{trace_id}/complete")
async def complete_trace(trace_id: str, status: str = "success") -> Dict:
    """Complete a distributed trace"""
    await tracing_service.complete_trace(trace_id, status)
    return {"status": "completed"}
