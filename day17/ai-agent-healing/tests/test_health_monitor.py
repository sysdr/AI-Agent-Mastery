import pytest
import asyncio
from backend.app.health.monitor import HealthMonitor

@pytest.mark.asyncio
async def test_health_monitor_initialization():
    monitor = HealthMonitor()
    assert monitor.alert_thresholds is not None
    assert "cpu_usage" in monitor.alert_thresholds
    assert "memory_usage" in monitor.alert_thresholds

@pytest.mark.asyncio
async def test_collect_health_metrics():
    monitor = HealthMonitor()
    metrics = await monitor.collect_health_metrics()
    
    assert "timestamp" in metrics
    assert "system" in metrics
    assert "application" in metrics
    assert "security" in metrics
    
    # Check system metrics
    assert "cpu_usage" in metrics["system"]
    assert "memory_usage" in metrics["system"]
    assert isinstance(metrics["system"]["cpu_usage"], float)
    
    # Check application metrics
    assert "request_count" in metrics["application"]
    assert "error_rate" in metrics["application"]
    assert metrics["application"]["error_rate"] >= 0

@pytest.mark.asyncio
async def test_get_system_health():
    monitor = HealthMonitor()
    
    # Add some test data
    test_metrics = await monitor.collect_health_metrics()
    monitor.metrics_history.append(test_metrics)
    
    health = await monitor.get_system_health()
    
    assert "status" in health
    assert health["status"] in ["healthy", "warning", "critical", "unknown"]
    assert "timestamp" in health
    assert "alerts" in health

if __name__ == "__main__":
    pytest.main([__file__])
