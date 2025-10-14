"""Main FastAPI application for Enterprise Multi-Agent System"""
import asyncio
import logging
import time
from contextlib import asynccontextmanager
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import structlog

from app.orchestration.orchestrator import AgentOrchestrator
from app.security.security_manager import SecurityManager
from app.monitoring.health_monitor import HealthMonitor
from app.compliance.audit_manager import AuditManager
from app.utils.config import settings

# Configure structured logging
structlog.configure(
    processors=[
        structlog.stdlib.filter_by_level,
        structlog.stdlib.add_logger_name,
        structlog.stdlib.add_log_level,
        structlog.stdlib.PositionalArgumentsFormatter(),
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.processors.StackInfoRenderer(),
        structlog.processors.format_exc_info,
        structlog.processors.UnicodeDecoder(),
        structlog.processors.JSONRenderer()
    ],
    context_class=dict,
    logger_factory=structlog.stdlib.LoggerFactory(),
    cache_logger_on_first_use=True,
)

logger = structlog.get_logger()

class WebSocketManager:
    def __init__(self):
        self.active_connections: list[WebSocket] = []
    
    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)
    
    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)
    
    async def broadcast(self, message: dict):
        for connection in self.active_connections.copy():
            try:
                await connection.send_json(message)
            except:
                self.active_connections.remove(connection)

websocket_manager = WebSocketManager()
orchestrator = AgentOrchestrator()
security_manager = SecurityManager()
health_monitor = HealthMonitor()
audit_manager = AuditManager()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("🚀 Starting Enterprise Multi-Agent System")
    await orchestrator.initialize()
    await security_manager.initialize()
    await health_monitor.start_monitoring()
    await audit_manager.initialize()
    
    # Start background tasks
    asyncio.create_task(system_health_monitor())
    asyncio.create_task(security_monitor())
    
    yield
    
    # Shutdown
    logger.info("🛑 Shutting down Enterprise Multi-Agent System")
    await orchestrator.shutdown()
    await security_manager.shutdown()
    await health_monitor.stop_monitoring()

app = FastAPI(
    title="Enterprise Multi-Agent System",
    description="Production-ready AI agent orchestration with security and compliance",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

async def system_health_monitor():
    """Background task for system health monitoring"""
    while True:
        try:
            health_data = await health_monitor.get_system_health()
            await websocket_manager.broadcast({
                "type": "health_update",
                "data": health_data
            })
            await asyncio.sleep(10)
        except Exception as e:
            logger.error("Health monitoring error", error=str(e))
            await asyncio.sleep(5)

async def security_monitor():
    """Background task for security monitoring"""
    while True:
        try:
            security_alerts = await security_manager.get_security_alerts()
            if security_alerts:
                await websocket_manager.broadcast({
                    "type": "security_alert",
                    "data": security_alerts
                })
            await asyncio.sleep(30)
        except Exception as e:
            logger.error("Security monitoring error", error=str(e))
            await asyncio.sleep(10)

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await websocket_manager.connect(websocket)
    try:
        # Send initial connection message
        await websocket.send_json({
            "type": "connection",
            "message": "Connected to Enterprise Multi-Agent System",
            "timestamp": time.time()
        })
        
        while True:
            try:
                # Wait for messages with a timeout
                data = await asyncio.wait_for(websocket.receive_text(), timeout=30.0)
                # Echo back the message
                await websocket.send_json({
                    "type": "echo",
                    "message": data,
                    "timestamp": time.time()
                })
            except asyncio.TimeoutError:
                # Send keepalive message
                await websocket.send_json({
                    "type": "keepalive",
                    "timestamp": time.time()
                })
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket)
    except Exception as e:
        logger.error("WebSocket error", error=str(e))
        websocket_manager.disconnect(websocket)

@app.get("/")
async def root():
    return {"message": "Enterprise Multi-Agent System API", "version": "1.0.0"}

@app.get("/health")
async def health_check():
    """System health check endpoint"""
    health_data = await health_monitor.get_system_health()
    return health_data

@app.post("/agents/execute")
async def execute_task(task_data: dict):
    """Execute task using agent orchestration"""
    try:
        # Security validation
        await security_manager.validate_request(task_data)
        
        # Execute task
        result = await orchestrator.execute_task(task_data)
        
        # Audit logging
        await audit_manager.log_task_execution(task_data, result)
        
        return {"success": True, "result": result}
    except Exception as e:
        logger.error("Task execution failed", error=str(e), task=task_data)
        return {"success": False, "error": str(e)}

@app.get("/agents/status")
async def get_agents_status():
    """Get status of all agents"""
    return await orchestrator.get_agents_status()

@app.get("/security/alerts")
async def get_security_alerts():
    """Get current security alerts"""
    return await security_manager.get_security_alerts()

@app.get("/compliance/audit-trail")
async def get_audit_trail():
    """Get compliance audit trail"""
    return await audit_manager.get_audit_trail()

@app.post("/system/recovery")
async def trigger_recovery():
    """Trigger system recovery procedures"""
    try:
        await orchestrator.trigger_recovery()
        return {"success": True, "message": "Recovery procedures initiated"}
    except Exception as e:
        return {"success": False, "error": str(e)}

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
