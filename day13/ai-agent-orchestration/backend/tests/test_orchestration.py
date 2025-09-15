import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
import sys
import os

# Add parent directory to path for imports
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from app.orchestrator.orchestration_engine import OrchestrationEngine
from app.security.security_validator import SecurityValidator
from app.trackers.cost_tracker import CostTracker

@pytest.mark.asyncio
async def test_orchestration_engine_initialization():
    """Test orchestration engine initialization"""
    engine = OrchestrationEngine()
    await engine.initialize()
    
    assert engine.tool_manager is not None
    assert engine.security_validator is not None
    assert engine.cost_tracker is not None
    
    await engine.cleanup()

@pytest.mark.asyncio
async def test_security_validator():
    """Test security validation"""
    validator = SecurityValidator()
    await validator.initialize()
    
    # Test safe request
    safe_request = Mock()
    safe_request.query = "What is machine learning?"
    safe_request.request_id = "test_123"
    
    result = await validator.validate_request(safe_request)
    assert result is True
    
    # Test malicious request
    malicious_request = Mock()
    malicious_request.query = "<script>alert('xss')</script>"
    malicious_request.request_id = "test_456"
    
    with pytest.raises(ValueError):
        await validator.validate_request(malicious_request)

@pytest.mark.asyncio
async def test_cost_tracker():
    """Test cost tracking functionality"""
    tracker = CostTracker()
    await tracker.initialize()
    
    # Track some tool usage
    cost = await tracker.track_tool_usage("web_search", 2.5)
    assert cost > 0
    
    total_cost = await tracker.get_total_cost()
    assert total_cost == cost
    
    cost_by_tool = await tracker.get_cost_by_tool()
    assert "web_search" in cost_by_tool
    
    await tracker.cleanup()

@pytest.mark.asyncio
async def test_parallel_tool_execution():
    """Test parallel tool execution"""
    engine = OrchestrationEngine()
    await engine.initialize()
    
    execution_plan = {
        "parallel_groups": [["web_search", "fact_checker"]],
        "sequential_steps": [["content_synthesizer"]]
    }
    
    # Mock the execute_single_tool method
    async def mock_execute_single_tool(tool_name, semaphore):
        return {
            "success": True,
            "data": f"Mock result from {tool_name}",
            "execution_time": 1.0
        }
    
    engine.execute_single_tool = mock_execute_single_tool
    
    results = await engine.execute_tools_parallel(execution_plan)
    
    assert "web_search" in results
    assert "fact_checker" in results
    assert results["web_search"]["success"] is True
    assert results["fact_checker"]["success"] is True
    
    await engine.cleanup()

def test_circuit_breaker_logic():
    """Test circuit breaker functionality"""
    from app.recovery.failure_handler import FailureHandler
    
    handler = FailureHandler()
    
    # Test severity assessment
    assert handler.assess_severity("security violation") == "critical"
    assert handler.assess_severity("timeout error") == "high"
    assert handler.assess_severity("general error") == "medium"
    
    # Test component identification
    assert handler.identify_failed_component("gemini api error") == "ai_service"
    assert handler.identify_failed_component("database connection failed") == "database"
    assert handler.identify_failed_component("network timeout") == "network"

if __name__ == "__main__":
    pytest.main([__file__])
