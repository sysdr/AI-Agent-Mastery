from fastapi import APIRouter, HTTPException, Query
from typing import List, Dict, Optional
from services.security_service import SecurityService

router = APIRouter()
security_service = SecurityService()

@router.get("/alerts")
async def get_active_alerts(
    severity: Optional[str] = Query(None, description="Filter by severity")
) -> List[Dict]:
    """Get active security alerts"""
    return await security_service.get_active_alerts(severity)

@router.get("/summary")
async def get_threat_summary(
    hours: int = Query(24, ge=1, le=168, description="Hours to look back")
) -> Dict:
    """Get threat summary for dashboard"""
    return await security_service.get_threat_summary(hours)

@router.post("/detect")
async def detect_threat(
    event_type: str,
    severity: str,
    details: Dict,
    correlation_data: Optional[Dict] = None
) -> Dict:
    """Detect and record a security threat"""
    alert_id = await security_service.detect_threat(
        event_type, severity, details, correlation_data
    )
    return {"alert_id": alert_id, "status": "detected"}

@router.post("/alerts/{alert_id}/resolve")
async def resolve_alert(
    alert_id: str,
    resolution: Optional[str] = None
) -> Dict:
    """Resolve a security alert"""
    success = await security_service.resolve_alert(alert_id, resolution)
    if not success:
        raise HTTPException(status_code=404, detail="Alert not found")
    return {"status": "resolved"}
