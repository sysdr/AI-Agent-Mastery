import pytest
import asyncio
from datetime import datetime, timedelta
from unittest.mock import AsyncMock
from backend.app.services.forecasting_service import ForecastingService

@pytest.fixture
def mock_redis():
    return AsyncMock()

@pytest.fixture
def forecast_service(mock_redis):
    return ForecastingService(mock_redis)

@pytest.mark.asyncio
async def test_forecast_costs_insufficient_data(forecast_service, mock_redis):
    """Test cost forecasting with insufficient data"""
    mock_redis.keys.return_value = []
    
    forecast = await forecast_service.forecast_costs("test-agent", 24)
    
    assert forecast['status'] == 'insufficient_data'
    assert 'message' in forecast

@pytest.mark.asyncio 
async def test_forecast_costs_with_data(forecast_service, mock_redis):
    """Test cost forecasting with sufficient data"""
    # Generate recent timestamps for the mock data
    recent_timestamp = (datetime.now() - timedelta(hours=1)).isoformat()
    
    # Mock sufficient historical data
    mock_data = []
    for i in range(15):
        mock_data.append(f'cost_metric:test-agent:{123456 + i}')
    
    mock_redis.keys.return_value = mock_data
    mock_redis.get.return_value = f'{{"agent_id": "test-agent", "cost_usd": 0.001, "timestamp": "{recent_timestamp}"}}'
    
    forecast = await forecast_service.forecast_costs("test-agent", 24)
    
    assert forecast['agent_id'] == 'test-agent'
    assert 'forecasted_total_cost' in forecast
    assert len(forecast['forecasted_hourly_costs']) == 24
