"""
Analysis API routes
"""

from fastapi import APIRouter, Depends
from typing import Dict, Any, List

from app.services.ai_service import AIService
from app.core.config import get_settings

router = APIRouter()

def get_ai_service():
    settings = get_settings()
    return AIService(settings.gemini_api_key)

@router.post("/generate-report")
async def generate_report(
    report_data: Dict[str, Any],
    ai_service: AIService = Depends(get_ai_service)
):
    """Generate comprehensive security report"""
    report = await ai_service.generate_security_report(report_data)
    return {"report": report}

@router.post("/suggest-fix")
async def suggest_fix(
    fix_data: Dict[str, Any],
    ai_service: AIService = Depends(get_ai_service)
):
    """Suggest secure code alternative"""
    vulnerable_code = fix_data.get("code", "")
    vulnerability_type = fix_data.get("vulnerability_type", "unknown")
    
    suggestion = await ai_service.suggest_secure_code(vulnerable_code, vulnerability_type)
    return {"suggestion": suggestion}

@router.get("/dashboard-data")
async def get_dashboard_data():
    """Get dashboard data for UI"""
    return {
        "recent_scans": [
            {
                "id": 1,
                "repository": "security-demo-app",
                "timestamp": "2024-11-20T10:30:00Z",
                "findings": 12,
                "status": "completed"
            },
            {
                "id": 2,
                "repository": "web-api-service",
                "timestamp": "2024-11-20T09:15:00Z",
                "findings": 3,
                "status": "completed"
            }
        ],
        "vulnerability_trends": {
            "labels": ["Mon", "Tue", "Wed", "Thu", "Fri"],
            "critical": [2, 1, 0, 3, 1],
            "high": [8, 6, 4, 7, 5],
            "medium": [15, 12, 10, 14, 11],
            "low": [25, 20, 18, 22, 19]
        },
        "top_vulnerabilities": [
            {"type": "SQL Injection", "count": 8, "severity": "high"},
            {"type": "XSS", "count": 6, "severity": "medium"},
            {"type": "Hardcoded Secrets", "count": 4, "severity": "critical"},
            {"type": "Path Traversal", "count": 3, "severity": "high"}
        ]
    }
