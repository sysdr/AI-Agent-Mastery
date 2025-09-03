from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import asyncio
import uvicorn
from datetime import datetime
import json

from .security_coordinator import SecurityCoordinator
from .audit_logger import AuditLogger
from .penetration_tester import PenetrationTester
from .performance_monitor import PerformanceMonitor
from .models import (
    AgentRegistration, SecurityEvent, AuditEntry, 
    VulnerabilityReport, PerformanceMetrics
)

app = FastAPI(
    title="AI Agent Security Assessment System",
    description="Enterprise-grade security monitoring for AI agent systems",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

# Initialize components
security_coordinator = SecurityCoordinator()
audit_logger = AuditLogger()
penetration_tester = PenetrationTester()
performance_monitor = PerformanceMonitor()

@app.on_event("startup")
async def startup_event():
    """Initialize security system on startup"""
    await security_coordinator.initialize()
    await audit_logger.initialize()
    await performance_monitor.start()
    print("🔒 Security Assessment System initialized")

@app.get("/")
async def root():
    return {"message": "AI Agent Security Assessment System", "status": "operational"}

@app.post("/api/v1/agents/register")
async def register_agent(registration: AgentRegistration):
    """Register a new agent with security coordinator"""
    try:
        agent_id = await security_coordinator.register_agent(
            registration.agent_id,
            registration.capabilities,
            registration.security_level
        )
        
        await audit_logger.log_event({
            "type": "agent_registration",
            "agent_id": agent_id,
            "timestamp": datetime.utcnow().isoformat(),
            "capabilities": registration.capabilities
        })
        
        return {"agent_id": agent_id, "status": "registered", "encrypted": True}
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@app.get("/api/v1/security/status")
async def get_security_status():
    """Get current security system status"""
    try:
        coordinator_status = await security_coordinator.get_status()
        active_agents = len(coordinator_status.get("agents", {}))
        
        return {
            "status": "operational",
            "active_agents": active_agents,
            "last_security_scan": coordinator_status.get("last_scan"),
            "threat_level": coordinator_status.get("threat_level", "low")
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/api/v1/security/scan")
async def run_security_scan(background_tasks: BackgroundTasks):
    """Trigger comprehensive security scan"""
    scan_id = f"scan_{datetime.utcnow().strftime('%Y%m%d_%H%M%S')}"
    
    background_tasks.add_task(
        penetration_tester.run_comprehensive_scan,
        scan_id
    )
    
    await audit_logger.log_event({
        "type": "security_scan_initiated",
        "scan_id": scan_id,
        "timestamp": datetime.utcnow().isoformat()
    })
    
    return {"scan_id": scan_id, "status": "initiated"}

@app.get("/api/v1/security/vulnerabilities")
async def get_vulnerabilities():
    """Get current vulnerability report"""
    try:
        report = await penetration_tester.get_vulnerability_report()
        return report
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/audit/entries")
async def get_audit_entries(limit: int = 100, offset: int = 0):
    """Get audit log entries"""
    try:
        entries = await audit_logger.get_entries(limit=limit, offset=offset)
        return {"entries": entries, "total": len(entries)}
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/metrics/performance")
async def get_performance_metrics():
    """Get current performance and security metrics"""
    try:
        metrics = await performance_monitor.get_metrics()
        return metrics
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/v1/metrics/dashboard")
async def get_dashboard_data():
    """Get comprehensive dashboard data"""
    try:
        security_status = await security_coordinator.get_status()
        performance_data = await performance_monitor.get_metrics()
        recent_audits = await audit_logger.get_entries(limit=10)
        vulnerabilities = await penetration_tester.get_vulnerability_report()
        
        return {
            "security": security_status,
            "performance": performance_data,
            "recent_events": recent_audits,
            "vulnerabilities": vulnerabilities,
            "timestamp": datetime.utcnow().isoformat()
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
