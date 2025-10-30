import pytest
import asyncio
import httpx
from fastapi.testclient import TestClient
from unittest.mock import AsyncMock, MagicMock
from backend.app.main import app, get_cost_controller, get_performance_controller, get_forecast_controller
from backend.app.controllers.cost_controller import CostController
from backend.app.controllers.performance_controller import PerformanceController
from backend.app.controllers.forecast_controller import ForecastController

# Create mock services and controllers
mock_redis = AsyncMock()
mock_cost_service = MagicMock()
mock_cost_service.get_cost_summary = AsyncMock(return_value={
    'agent_id': 'test-agent',
    'total_cost': 0.0,
    'request_count': 0
})
mock_cost_service.check_optimization_opportunities = AsyncMock(return_value=[])

mock_perf_service = MagicMock()
mock_perf_service.get_performance_summary = AsyncMock(return_value={
    'agent_id': 'test-agent',
    'avg_cpu_usage': 50.0,
    'avg_memory_usage': 60.0
})

mock_forecast_service = MagicMock()
mock_forecast_service.forecast_costs = AsyncMock(return_value={
    'agent_id': 'test-agent',
    'forecasted_total_cost': 10.0
})

# Create controllers with mock services
mock_cost_controller = CostController(mock_cost_service)
mock_perf_controller = PerformanceController(mock_perf_service)
mock_forecast_controller = ForecastController(mock_forecast_service)

# Override dependencies
app.dependency_overrides[get_cost_controller] = lambda: mock_cost_controller
app.dependency_overrides[get_performance_controller] = lambda: mock_perf_controller
app.dependency_overrides[get_forecast_controller] = lambda: mock_forecast_controller

client = TestClient(app)

def test_health_endpoint():
    """Test health check endpoint"""
    response = client.get("/health")
    assert response.status_code in [200, 500]  # May fail if Redis not available
    data = response.json()
    assert "status" in data

def test_root_endpoint():
    """Test root endpoint"""
    response = client.get("/")
    assert response.status_code == 200
    data = response.json()
    assert data["message"] == "AI Agent Cost Optimizer API"

def test_cost_summary_endpoint():
    """Test cost summary endpoint"""
    response = client.get("/api/cost/summary/test-agent?hours=1")
    assert response.status_code == 200
    data = response.json()
    assert data['agent_id'] == 'test-agent'

def test_performance_summary_endpoint():
    """Test performance summary endpoint"""
    response = client.get("/api/performance/summary/test-agent?minutes=60")
    assert response.status_code == 200
    data = response.json()
    assert data['agent_id'] == 'test-agent'
