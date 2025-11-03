from fastapi import FastAPI, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer
from contextlib import asynccontextmanager
import asyncio
import logging
from datetime import datetime

from app.security.scanner import SecurityScanner
from app.load_testing.engine import LoadTestEngine
from app.quality_gates.validator import QualityGateValidator
from app.dashboard.metrics import MetricsCollector

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Initialize components
security_scanner = SecurityScanner()
load_test_engine = LoadTestEngine()
quality_validator = QualityGateValidator()
metrics_collector = MetricsCollector()

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    logger.info("Starting QA Automation Platform...")
    await security_scanner.initialize()
    await metrics_collector.start()
    yield
    # Shutdown
    logger.info("Shutting down QA Automation Platform...")
    await metrics_collector.stop()

app = FastAPI(
    title="AI Agent QA Automation Platform",
    description="Enterprise Testing & Quality Assurance for AI Agent Systems",
    version="1.0.0",
    lifespan=lifespan
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

security = HTTPBearer()

@app.get("/")
async def root():
    return {"message": "AI Agent QA Automation Platform", "status": "running"}

@app.get("/health")
async def health_check():
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "components": {
            "security_scanner": await security_scanner.health_check(),
            "load_test_engine": load_test_engine.health_check(),
            "quality_gates": quality_validator.health_check()
        }
    }

@app.post("/security/scan")
async def run_security_scan(target_url: str, background_tasks: BackgroundTasks):
    scan_id = await security_scanner.start_scan(target_url)
    background_tasks.add_task(security_scanner.execute_scan, scan_id, target_url)
    return {"scan_id": scan_id, "status": "started"}

@app.get("/security/scan/{scan_id}")
async def get_scan_results(scan_id: str):
    results = await security_scanner.get_scan_results(scan_id)
    if not results:
        raise HTTPException(status_code=404, detail="Scan not found")
    return results

@app.post("/load-test/start")
async def start_load_test(target_url: str, users: int = 50, duration: int = 60):
    test_id = await load_test_engine.start_test(target_url, users, duration)
    return {"test_id": test_id, "status": "started"}

@app.get("/load-test/{test_id}")
async def get_load_test_results(test_id: str):
    results = await load_test_engine.get_test_results(test_id)
    if not results:
        raise HTTPException(status_code=404, detail="Load test not found")
    return results

@app.post("/quality-gates/validate")
async def validate_quality_gates(deployment_data: dict):
    validation_result = await quality_validator.validate(deployment_data)
    return validation_result

@app.get("/metrics/dashboard")
async def get_dashboard_metrics():
    return await metrics_collector.get_dashboard_data()

if __name__ == "__main__":
    import uvicorn
    from config.settings import settings
    uvicorn.run(app, host=settings.API_HOST, port=settings.API_PORT)
