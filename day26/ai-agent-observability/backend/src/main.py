from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import uvicorn
import asyncio
import json
from datetime import datetime
from typing import List, Dict, Any
import structlog

from services.tracing_service import TracingService
from services.metrics_service import MetricsService
from services.logging_service import LoggingService
from services.operations_service import OperationsService
from services.security_service import SecurityService
from api import traces, metrics, logs, operations, security

logger = structlog.get_logger()

app = FastAPI(title="AI Agent Observability Platform", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
tracing_service = TracingService()
metrics_service = MetricsService()
logging_service = LoggingService()
operations_service = OperationsService()
security_service = SecurityService()

# Include routers
app.include_router(traces.router, prefix="/api/traces", tags=["traces"])
app.include_router(metrics.router, prefix="/api/metrics", tags=["metrics"])
app.include_router(logs.router, prefix="/api/logs", tags=["logs"])
app.include_router(operations.router, prefix="/api/operations", tags=["operations"])
app.include_router(security.router, prefix="/api/security", tags=["security"])

# WebSocket connections manager
class ConnectionManager:
    def __init__(self):
        self.active_connections: List[WebSocket] = []

    async def connect(self, websocket: WebSocket):
        await websocket.accept()
        self.active_connections.append(websocket)

    def disconnect(self, websocket: WebSocket):
        self.active_connections.remove(websocket)

    async def broadcast(self, message: dict):
        for connection in self.active_connections:
            try:
                await connection.send_text(json.dumps(message))
            except:
                await self.disconnect(connection)

manager = ConnectionManager()

@app.websocket("/ws")
async def websocket_endpoint(websocket: WebSocket):
    await manager.connect(websocket)
    try:
        while True:
            # Send real-time updates
            await asyncio.sleep(1)
            data = {
                "timestamp": datetime.now().isoformat(),
                "metrics": await metrics_service.get_real_time_metrics(),
                "alerts": await security_service.get_active_alerts(),
                "traces": await tracing_service.get_recent_traces(limit=5)
            }
            await websocket.send_text(json.dumps(data))
    except WebSocketDisconnect:
        manager.disconnect(websocket)

@app.get("/")
async def root():
    return {"message": "AI Agent Observability Platform", "status": "running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.now().isoformat(),
        "services": {
            "tracing": await tracing_service.health_check(),
            "metrics": await metrics_service.health_check(),
            "logging": await logging_service.health_check(),
            "operations": await operations_service.health_check(),
            "security": await security_service.health_check()
        }
    }

if __name__ == "__main__":
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
