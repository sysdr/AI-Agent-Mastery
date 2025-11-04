from fastapi import FastAPI, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from backend.models.schemas import *
from backend.services.backup_service import backup_service
from backend.services.health_monitor import health_monitor
from backend.services.failover_orchestrator import failover_orchestrator
from backend.services.recovery_service import recovery_service
from backend.services.audit_service import audit_service
from backend.config.settings import settings
import asyncio
from typing import Dict, List

app = FastAPI(title="Disaster Recovery System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Background tasks
background_tasks_started = False

async def start_background_services():
    """Start all background services"""
    global background_tasks_started
    if background_tasks_started:
        return
    background_tasks_started = True
    
    # Start backup services for all regions
    for region in RegionEnum:
        asyncio.create_task(backup_service.continuous_backup(region))
    
    # Start health monitoring
    asyncio.create_task(health_monitor.continuous_monitoring())
    
    # Start failover monitoring
    asyncio.create_task(failover_orchestrator.monitor_and_failover())

@app.on_event("startup")
async def startup_event():
    await start_background_services()

@app.get("/")
async def root():
    return {
        "service": "Disaster Recovery System",
        "version": "1.0.0",
        "status": "operational"
    }

@app.get("/health")
async def get_health():
    return {
        "system_state": health_monitor.system_state,
        "active_region": failover_orchestrator.active_region,
        "metrics": health_monitor.metrics
    }

@app.get("/backups")
async def get_backups():
    return {
        "backups_by_region": backup_service.backups
    }

@app.get("/backups/{region}")
async def get_region_backups(region: RegionEnum):
    return {
        "region": region,
        "backups": backup_service.backups.get(region.value, [])
    }

@app.post("/failover/inject-failure")
async def inject_failure():
    """Inject simulated failure for testing"""
    health_monitor.inject_failure()
    return {"message": "Failure injected", "region": settings.PRIMARY_REGION}

@app.post("/failover/trigger")
async def trigger_manual_failover():
    """Manually trigger failover"""
    asyncio.create_task(failover_orchestrator.initiate_failover())
    return {"message": "Failover initiated"}

@app.get("/failover/status")
async def get_failover_status():
    return {
        "active_region": failover_orchestrator.active_region,
        "failover_in_progress": failover_orchestrator.failover_in_progress,
        "last_failover": failover_orchestrator.last_failover
    }

@app.post("/recovery/start/{region}")
async def start_recovery(region: RegionEnum):
    """Start recovery for a region"""
    asyncio.create_task(recovery_service.attempt_recovery(region))
    return {"message": f"Recovery started for {region}"}

@app.get("/audit/logs")
async def get_audit_logs(limit: int = 50):
    return {
        "logs": audit_service.get_recent_logs(limit)
    }

@app.get("/metrics/dashboard")
async def get_dashboard_metrics():
    """Get all metrics for dashboard"""
    return {
        "system_state": health_monitor.system_state,
        "active_region": failover_orchestrator.active_region,
        "health_metrics": health_monitor.metrics,
        "backup_counts": {
            region: len(backups) 
            for region, backups in backup_service.backups.items()
        },
        "last_failover": failover_orchestrator.last_failover,
        "recent_audit_logs": audit_service.get_recent_logs(10)
    }
