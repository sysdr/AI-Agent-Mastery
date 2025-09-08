from fastapi import APIRouter
from typing import Dict, Any
import logging
from ..services.metrics_service import metrics_service

logger = logging.getLogger(__name__)
router = APIRouter()

@router.get("/compliance/stats")
async def get_compliance_stats():
    """Get compliance monitoring statistics"""
    return metrics_service.get_compliance_stats()

@router.get("/personality/consistency")
async def get_personality_consistency():
    """Get personality consistency metrics"""
    return metrics_service.get_personality_consistency()

@router.get("/system/health")
async def get_system_health():
    """Get system health metrics"""
    return metrics_service.get_system_health()

@router.get("/dashboard")
async def get_dashboard_metrics():
    """Get comprehensive dashboard metrics"""
    return metrics_service.get_dashboard_metrics()
