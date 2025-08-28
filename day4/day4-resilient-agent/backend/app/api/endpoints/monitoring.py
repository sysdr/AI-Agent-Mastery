from fastapi import APIRouter, HTTPException, Depends, Request, Response
from typing import List, Dict, Any
from pydantic import BaseModel, HttpUrl
import asyncio
from ...services.price_scraper import PriceScraper
from ...services.monitoring_tracker import MonitoringTracker
from ...core.rate_limiter import DistributedRateLimiter
from ...core.session_manager import SessionManager
import redis.asyncio as redis

router = APIRouter()

class MonitoringRequest(BaseModel):
    urls: List[HttpUrl]
    name: str = "Price Monitor"

class PriceAlert(BaseModel):
    url: str
    target_price: float
    current_price: float = None

# Dependency injection
async def get_redis():
    return redis.from_url("redis://localhost:6379")

async def get_scraper(redis_client: redis.Redis = Depends(get_redis)):
    rate_limiter = DistributedRateLimiter(redis_client)
    return PriceScraper(rate_limiter)

async def get_tracker(redis_client: redis.Redis = Depends(get_redis)):
    return MonitoringTracker(redis_client)

@router.post("/scrape")
async def scrape_prices(
    request: MonitoringRequest,
    scraper: PriceScraper = Depends(get_scraper),
    tracker: MonitoringTracker = Depends(get_tracker)
):
    """Scrape prices from multiple URLs with resilience patterns"""
    results = []
    
    # Process URLs concurrently with semaphore for backpressure
    semaphore = asyncio.Semaphore(5)  # Max 5 concurrent requests
    
    async def scrape_single(url):
        async with semaphore:
            return await scraper.scrape_price(str(url))
    
    tasks = [scrape_single(url) for url in request.urls]
    results = await asyncio.gather(*tasks, return_exceptions=True)
    
    # Filter out exceptions and get valid results
    valid_results = []
    for result in results:
        if isinstance(result, dict) and result.get("success") is not None:
            valid_results.append(result)
        else:
            # Handle exceptions
            valid_results.append({
                "success": False,
                "error": str(result) if result else "Unknown error"
            })
    
    successful = [r for r in valid_results if r.get("success")]
    failed = [r for r in valid_results if not r.get("success")]
    
    # Track the monitoring session
    await tracker.track_session(request.name, [str(url) for url in request.urls], valid_results)
    
    return {
        "monitoring_session": request.name,
        "total_urls": len(request.urls),
        "successful_scrapes": len(successful),
        "failed_scrapes": len(failed),
        "results": valid_results
    }

@router.get("/status")
async def monitoring_status(
    scraper: PriceScraper = Depends(get_scraper),
    tracker: MonitoringTracker = Depends(get_tracker)
):
    """Get monitoring system status"""
    # Get active domains from tracker
    active_domains = await tracker.get_active_domains()
    
    # Get recent sessions for additional metrics
    recent_sessions = await tracker.get_recent_sessions(5)
    
    # Calculate total metrics
    total_monitored_urls = sum(session.get("total_urls", 0) for session in recent_sessions)
    total_successful_scrapes = sum(session.get("successful_scrapes", 0) for session in recent_sessions)
    total_failed_scrapes = sum(session.get("failed_scrapes", 0) for session in recent_sessions)
    
    return {
        "status": "operational",
        "circuit_breakers": {},
        "active_domains": active_domains,
        "total_monitored_urls": total_monitored_urls,
        "total_successful_scrapes": total_successful_scrapes,
        "total_failed_scrapes": total_failed_scrapes,
        "recent_sessions": len(recent_sessions)
    }

@router.post("/alerts")
async def create_price_alert(
    alert: PriceAlert,
    redis_client: redis.Redis = Depends(get_redis)
):
    """Create price alert with secure storage"""
    alert_id = f"alert:{hash(alert.url)}"
    
    alert_data = {
        "url": alert.url,
        "target_price": alert.target_price,
        "created_at": "2025-01-01T00:00:00",
        "active": True
    }
    
    await redis_client.hset(alert_id, mapping=alert_data)
    
    return {
        "alert_id": alert_id,
        "message": "Price alert created successfully",
        "alert": alert_data
    }

@router.get("/alerts")
async def list_alerts(redis_client: redis.Redis = Depends(get_redis)):
    """List all active price alerts"""
    keys = await redis_client.keys("alert:*")
    alerts = []
    
    for key in keys:
        alert_data = await redis_client.hgetall(key)
        if alert_data and alert_data.get(b"active") == b"True":
            alerts.append({
                "alert_id": key.decode(),
                "url": alert_data.get(b"url", b"").decode(),
                "target_price": float(alert_data.get(b"target_price", 0)),
                "created_at": alert_data.get(b"created_at", b"").decode()
            })
    
    return {"alerts": alerts, "total": len(alerts)}
