from fastapi import FastAPI, Depends
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
import redis.asyncio as redis
import uvicorn
from contextlib import asynccontextmanager
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from config.config import config
from app.services.cost_optimizer import CostOptimizerService
from app.services.performance_monitor import PerformanceMonitorService
from app.services.forecasting_service import ForecastingService
from app.controllers.cost_controller import CostController, router as cost_router
from app.controllers.performance_controller import PerformanceController, router as perf_router
from app.controllers.forecast_controller import ForecastController, router as forecast_router

# Global services
redis_client = None
cost_service = None
performance_service = None
forecasting_service = None
cost_controller = None
performance_controller = None
forecast_controller = None

@asynccontextmanager
async def lifespan(app: FastAPI):
    # Startup
    global redis_client, cost_service, performance_service, forecasting_service
    global cost_controller, performance_controller, forecast_controller
    
    # Initialize Redis
    redis_client = redis.Redis.from_url(config.REDIS_URL, decode_responses=True)
    
    # Initialize services
    cost_service = CostOptimizerService(redis_client)
    performance_service = PerformanceMonitorService(redis_client)
    forecasting_service = ForecastingService(redis_client)
    
    # Initialize controllers
    cost_controller = CostController(cost_service)
    performance_controller = PerformanceController(performance_service)
    forecast_controller = ForecastController(forecasting_service)
    
    print("🚀 AI Cost Optimizer services initialized")
    
    yield
    
    # Shutdown
    await redis_client.close()
    print("👋 AI Cost Optimizer services shutdown")

app = FastAPI(
    title="AI Agent Cost Optimizer",
    description="Enterprise-grade cost optimization and performance monitoring for AI agents",
    version="1.0.0",
    lifespan=lifespan
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency injection
def get_cost_controller():
    return cost_controller

def get_performance_controller():
    return performance_controller

def get_forecast_controller():
    return forecast_controller

# Update routes with dependencies
@cost_router.post("/request")
async def make_tracked_ai_request_endpoint(
    agent_id: str,
    prompt: str,
    model_name: str = "gemini-pro",
    controller: CostController = Depends(get_cost_controller)
):
    return await controller.create_ai_request_with_tracking(agent_id, prompt, model_name)

@cost_router.get("/summary/{agent_id}")
async def get_cost_summary_endpoint(
    agent_id: str,
    hours: int = 1,
    controller: CostController = Depends(get_cost_controller)
):
    return await controller.cost_service.get_cost_summary(agent_id, hours)

@cost_router.get("/optimization/{agent_id}")
async def get_optimization_opportunities_endpoint(
    agent_id: str,
    controller: CostController = Depends(get_cost_controller)
):
    return await controller.cost_service.check_optimization_opportunities(agent_id)

@perf_router.get("/summary/{agent_id}")
async def get_performance_summary_endpoint(
    agent_id: str,
    minutes: int = 60,
    controller: PerformanceController = Depends(get_performance_controller)
):
    return await controller.performance_service.get_performance_summary(agent_id, minutes)

@forecast_router.get("/costs/{agent_id}")
async def forecast_costs_endpoint(
    agent_id: str,
    forecast_hours: int = 24,
    controller: ForecastController = Depends(get_forecast_controller)
):
    return await controller.forecasting_service.forecast_costs(agent_id, forecast_hours)

# Include routers
app.include_router(cost_router)
app.include_router(perf_router)
app.include_router(forecast_router)

@app.get("/")
async def root():
    return {
        "message": "AI Agent Cost Optimizer API",
        "version": "1.0.0",
        "status": "running"
    }

@app.get("/health")
async def health_check():
    try:
        await redis_client.ping()
        return {
            "status": "healthy",
            "redis": "connected",
            "timestamp": "2024-05-15T10:00:00Z"
        }
    except:
        return {
            "status": "unhealthy",
            "redis": "disconnected",
            "timestamp": "2024-05-15T10:00:00Z"
        }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=config.PORT,
        reload=config.DEBUG
    )
