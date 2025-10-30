import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock, patch
from backend.app.services.performance_monitor import PerformanceMonitorService
from backend.app.models.performance_metrics import PerformanceMetric

@pytest.fixture
def mock_redis():
    return AsyncMock()

@pytest.fixture
def perf_service(mock_redis):
    return PerformanceMonitorService(mock_redis)

@pytest.mark.asyncio
async def test_record_performance_metric(perf_service, mock_redis):
    """Test recording performance metrics"""
    metric = PerformanceMetric(
        agent_id="test-agent",
        cpu_usage=45.2,
        memory_usage=62.8,
        request_count=10,
        error_rate=1.5,
        avg_response_time=1200,
        throughput=0.16
    )
    
    await perf_service.record_performance_metric(metric)
    
    # Verify Redis calls
    assert mock_redis.setex.called

@pytest.mark.asyncio
async def test_get_performance_summary(perf_service, mock_redis):
    """Test getting performance summary"""
    # Generate recent timestamp for the mock data
    recent_timestamp = (datetime.now() - timedelta(minutes=30)).isoformat()
    
    mock_redis.keys.return_value = ['perf_metric:test-agent:123456']
    mock_redis.get.return_value = f'{{"agent_id": "test-agent", "cpu_usage": 45.2, "memory_usage": 62.8, "request_count": 10, "error_rate": 1.5, "avg_response_time": 1200, "throughput": 0.16, "timestamp": "{recent_timestamp}"}}'
    
    summary = await perf_service.get_performance_summary("test-agent", 60)
    
    assert summary['agent_id'] == 'test-agent'
    assert 'avg_cpu_usage' in summary
    assert 'avg_memory_usage' in summary
