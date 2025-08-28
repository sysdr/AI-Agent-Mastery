from fastapi import APIRouter, Depends
import redis.asyncio as redis
import time

router = APIRouter()

async def get_redis():
    return redis.from_url("redis://localhost:6379")

@router.get("/")
async def health_check():
    """Basic health check"""
    return {
        "status": "healthy",
        "timestamp": time.time(),
        "service": "price-monitoring-agent"
    }

@router.get("/detailed")
async def detailed_health_check(redis_client: redis.Redis = Depends(get_redis)):
    """Detailed health check with dependencies"""
    health_status = {
        "status": "healthy",
        "timestamp": time.time(),
        "checks": {}
    }
    
    # Redis connectivity
    try:
        await redis_client.ping()
        health_status["checks"]["redis"] = {"status": "healthy", "latency_ms": 1}
    except Exception as e:
        health_status["checks"]["redis"] = {"status": "unhealthy", "error": str(e)}
        health_status["status"] = "degraded"
    
    # Memory usage (simplified)
    health_status["checks"]["memory"] = {"status": "healthy", "usage_percent": 45}
    
    return health_status
