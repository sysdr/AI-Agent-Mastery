from fastapi import FastAPI, WebSocket, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from contextlib import asynccontextmanager
import asyncio
import json
from datetime import datetime
import structlog

from .monitoring.anomaly_detector import AnomalyDetector
from .recovery.auto_recovery import AutoRecoverySystem
from .health.monitor import HealthMonitor
from .security.incident_manager import IncidentManager

logger = structlog.get_logger()

# Global system components
anomaly_detector = None
recovery_system = None
health_monitor = None
incident_manager = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    global anomaly_detector, recovery_system, health_monitor, incident_manager
    
    # Initialize system components
    logger.info("🔧 Initializing self-healing system...")
    
    anomaly_detector = AnomalyDetector()
    recovery_system = AutoRecoverySystem()
    health_monitor = HealthMonitor()
    incident_manager = IncidentManager()
    
    # Start background monitoring
    asyncio.create_task(health_monitor.continuous_monitoring())
    asyncio.create_task(anomaly_detector.continuous_detection())
    
    logger.info("✅ Self-healing system initialized")
    yield
    
    # Cleanup
    logger.info("🛑 Shutting down self-healing system...")

app = FastAPI(
    title="AI Agent Self-Healing System",
    description="Production-grade self-healing with security monitoring",
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

@app.get("/")
async def root():
    return {"message": "AI Agent Self-Healing System", "status": "healthy"}

@app.get("/health")
async def health_check():
    return await health_monitor.get_system_health()

@app.get("/metrics")
async def get_metrics():
    return await health_monitor.get_detailed_metrics()

@app.get("/security/status")
async def security_status():
    return await incident_manager.get_security_status()

@app.get("/incidents")
async def get_incidents():
    return await incident_manager.get_recent_incidents()

@app.post("/simulate/attack")
async def simulate_attack(attack_type: str = "ddos"):
    """Simulate security attack for testing"""
    return await incident_manager.simulate_attack(attack_type)

@app.post("/recovery/trigger")
async def trigger_recovery(background_tasks: BackgroundTasks):
    """Manually trigger recovery process"""
    background_tasks.add_task(recovery_system.execute_recovery, "manual_trigger")
    return {"status": "recovery_initiated", "timestamp": datetime.utcnow()}

@app.websocket("/ws/monitoring")
async def websocket_monitoring(websocket: WebSocket):
    await websocket.accept()
    try:
        while True:
            # Send real-time monitoring data
            health_data = await health_monitor.get_realtime_data()
            await websocket.send_text(json.dumps(health_data))
            await asyncio.sleep(2)
    except Exception as e:
        logger.error(f"WebSocket error: {e}")
    finally:
        await websocket.close()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
