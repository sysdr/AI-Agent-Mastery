import asyncio
import logging
from contextlib import asynccontextmanager
from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import structlog
from prometheus_client import make_asgi_app

from orchestrator.orchestration_engine import OrchestrationEngine
from monitoring.metrics_collector import MetricsCollector
from config.settings import Settings

# Configure structured logging
structlog.configure(
    processors=[
        structlog.processors.TimeStamper(),
        structlog.dev.ConsoleRenderer()
    ],
    logger_factory=structlog.stdlib.LoggerFactory(),
)

logger = structlog.get_logger()
settings = Settings()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting Advanced Tool Orchestration System")
    app.state.orchestration_engine = OrchestrationEngine()
    app.state.metrics_collector = MetricsCollector()
    await app.state.orchestration_engine.initialize()
    yield
    # Shutdown
    logger.info("Shutting down system")
    await app.state.orchestration_engine.cleanup()

app = FastAPI(
    title="Advanced Tool Orchestration & Monitoring",
    description="Production-ready AI agent tool orchestration system",
    version="1.0.0",
    lifespan=lifespan
)

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Add Prometheus metrics
metrics_app = make_asgi_app()
app.mount("/metrics", metrics_app)

@app.post("/api/research")
async def execute_research(request: dict):
    """Execute research task with orchestrated tools"""
    try:
        engine = app.state.orchestration_engine
        result = await engine.execute_research(
            query=request.get("query"),
            tools_config=request.get("tools", {}),
            security_level=request.get("security_level", "standard")
        )
        return JSONResponse(content=result)
    except Exception as e:
        logger.error("Research execution failed", error=str(e))
        raise HTTPException(status_code=500, detail=str(e))

@app.get("/api/status")
async def get_system_status():
    """Get system health and metrics"""
    engine = app.state.orchestration_engine
    metrics = app.state.metrics_collector
    
    return {
        "status": "healthy",
        "active_orchestrations": await engine.get_active_count(),
        "total_cost": await metrics.get_total_cost(),
        "security_incidents": await metrics.get_security_incidents(),
        "circuit_breakers": await engine.get_circuit_breaker_status()
    }

@app.get("/api/metrics")
async def get_detailed_metrics():
    """Get detailed system metrics"""
    metrics = app.state.metrics_collector
    return await metrics.get_all_metrics()

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
