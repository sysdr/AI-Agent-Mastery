"""
Security API routes
"""

from fastapi import APIRouter, HTTPException, Depends, UploadFile, File
from typing import List, Dict, Any
import json

from app.services.security_engine import SecurityEngine
from app.services.ai_service import AIService
from app.core.config import get_settings

router = APIRouter()

# Dependency to get services
def get_security_engine():
    return SecurityEngine()

def get_ai_service():
    settings = get_settings()
    return AIService(settings.gemini_api_key)

@router.post("/analyze-code")
async def analyze_code(
    code_data: Dict[str, Any],
    security_engine: SecurityEngine = Depends(get_security_engine)
):
    """Analyze code snippet for security vulnerabilities"""
    code = code_data.get("code", "")
    file_path = code_data.get("file_path", "unknown.py")
    
    if not code:
        raise HTTPException(status_code=400, detail="Code is required")
    
    findings = await security_engine.analyze_code(code, file_path)
    
    return {
        "file_path": file_path,
        "findings": [
            {
                "rule_id": f.rule_id,
                "severity": f.severity.value,
                "message": f.message,
                "line_number": f.line_number,
                "column": f.column,
                "code_snippet": f.code_snippet,
                "recommendation": f.recommendation,
                "cwe_id": f.cwe_id
            }
            for f in findings
        ],
        "summary": {
            "total_findings": len(findings),
            "critical": len([f for f in findings if f.severity.value == "critical"]),
            "high": len([f for f in findings if f.severity.value == "high"]),
            "medium": len([f for f in findings if f.severity.value == "medium"]),
            "low": len([f for f in findings if f.severity.value == "low"])
        }
    }

@router.post("/analyze-file")
async def analyze_file(
    file: UploadFile = File(...),
    security_engine: SecurityEngine = Depends(get_security_engine)
):
    """Analyze uploaded file for security vulnerabilities"""
    if file.size > 1024 * 1024:  # 1MB limit
        raise HTTPException(status_code=400, detail="File too large")
    
    content = await file.read()
    try:
        code = content.decode('utf-8')
    except UnicodeDecodeError:
        raise HTTPException(status_code=400, detail="File must be text")
    
    findings = await security_engine.analyze_code(code, file.filename)
    
    return {
        "filename": file.filename,
        "size": len(code),
        "findings": [
            {
                "rule_id": f.rule_id,
                "severity": f.severity.value,
                "message": f.message,
                "line_number": f.line_number,
                "code_snippet": f.code_snippet,
                "recommendation": f.recommendation
            }
            for f in findings
        ]
    }

@router.post("/explain-finding")
async def explain_finding(
    request_data: Dict[str, Any],
    ai_service: AIService = Depends(get_ai_service)
):
    """Get AI explanation of security finding"""
    from app.services.security_engine import SecurityFinding, SeverityLevel
    
    # Reconstruct finding from request
    finding = SecurityFinding(
        rule_id=request_data.get("rule_id", ""),
        severity=SeverityLevel(request_data.get("severity", "medium")),
        message=request_data.get("message", ""),
        file_path=request_data.get("file_path", ""),
        line_number=request_data.get("line_number", 0),
        column=request_data.get("column", 0),
        code_snippet=request_data.get("code_snippet", ""),
        recommendation=request_data.get("recommendation", "")
    )
    
    explanation = await ai_service.explain_finding(finding)
    
    return {"explanation": explanation}

@router.get("/patterns")
async def get_security_patterns():
    """Get available security patterns"""
    security_engine = SecurityEngine()
    return {"patterns": security_engine.vulnerability_patterns}

@router.get("/stats")
async def get_security_stats():
    """Get security analysis statistics"""
    # This would typically come from a database
    return {
        "total_scans": 150,
        "vulnerabilities_found": 45,
        "files_analyzed": 1250,
        "repositories_scanned": 12,
        "critical_issues": 3,
        "resolved_issues": 38
    }
