import pytest
import asyncio
from datetime import datetime
from unittest.mock import AsyncMock, MagicMock
from backend.app.services.cost_optimizer import CostOptimizerService
from backend.app.models.cost_metrics import CostMetric

@pytest.fixture
def mock_redis():
    return AsyncMock()

@pytest.fixture
def cost_service(mock_redis):
    return CostOptimizerService(mock_redis)

@pytest.mark.asyncio
async def test_record_cost_metric(cost_service, mock_redis):
    """Test recording cost metrics"""
    metric = CostMetric(
        agent_id="test-agent",
        request_type="generate_content",
        tokens_used=100,
        cost_usd=0.0015,
        model_name="gemini-pro",
        success=True,
        response_time_ms=1500
    )
    
    await cost_service.record_cost_metric(metric)
    
    # Verify Redis calls
    assert mock_redis.setex.called
    assert mock_redis.incrbyfloat.called

@pytest.mark.asyncio
async def test_get_cost_summary(cost_service, mock_redis):
    """Test getting cost summary"""
    mock_redis.keys.return_value = ['cost_metric:test-agent:123456']
    mock_redis.get.return_value = '{"agent_id": "test-agent", "cost_usd": 0.001, "tokens_used": 50, "timestamp": "2024-05-15T10:00:00"}'
    
    summary = await cost_service.get_cost_summary("test-agent", 1)
    
    assert summary['agent_id'] == 'test-agent'
    assert 'total_cost' in summary
    assert 'total_tokens' in summary
