import pytest
from backend.services.health_monitor import health_monitor
from backend.models.schemas import RegionEnum, SystemState

@pytest.mark.asyncio
async def test_health_metrics_collection():
    """Test health metrics collection"""
    metrics = await health_monitor.collect_metrics(RegionEnum.US_EAST)
    
    assert metrics.region == RegionEnum.US_EAST
    assert metrics.latency_ms >= 0
    assert 0 <= metrics.error_rate <= 1
    assert isinstance(metrics.is_healthy, bool)

def test_failure_injection():
    """Test failure injection mechanism"""
    health_monitor.inject_failure()
    assert health_monitor.failure_injected == True
    
    health_monitor.clear_failure()
    assert health_monitor.failure_injected == False
