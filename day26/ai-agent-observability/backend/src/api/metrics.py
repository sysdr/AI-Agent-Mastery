from fastapi import APIRouter, Response
from typing import Dict, Any
from services.metrics_service import MetricsService

router = APIRouter()
metrics_service = MetricsService()

@router.get("/realtime")
async def get_realtime_metrics() -> Dict[str, Any]:
    """Get real-time metrics"""
    return await metrics_service.get_real_time_metrics()

@router.post("/confidence")
async def record_confidence(agent_id: str, confidence: float, context: Dict = None) -> Dict:
    """Record confidence score"""
    await metrics_service.record_confidence_score(agent_id, confidence, context)
    return {"status": "recorded"}

@router.post("/request")
async def record_request(agent_type: str, status: str, response_time: float) -> Dict:
    """Record request metric"""
    await metrics_service.record_request(agent_type, status, response_time)
    return {"status": "recorded"}

@router.post("/tokens")
async def record_tokens(operation: str, tokens_used: int, cost_estimate: float) -> Dict:
    """Record token usage"""
    await metrics_service.record_token_usage(operation, tokens_used, cost_estimate)
    return {"status": "recorded"}

@router.get("/prometheus")
async def get_prometheus_metrics():
    """Get Prometheus-format metrics"""
    metrics = await metrics_service.get_prometheus_metrics()
    return Response(content=metrics, media_type="text/plain")
