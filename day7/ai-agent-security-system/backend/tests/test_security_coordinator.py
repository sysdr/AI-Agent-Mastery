import pytest
import asyncio
from app.security_coordinator import SecurityCoordinator

@pytest.mark.asyncio
async def test_agent_registration():
    coordinator = SecurityCoordinator()
    await coordinator.initialize()
    
    agent_id = await coordinator.register_agent(
        "test_agent_1",
        ["authentication", "data_processing"],
        "high"
    )
    
    assert agent_id == "test_agent_1"
    assert agent_id in coordinator.agents
    
    context = await coordinator.get_agent_context(agent_id)
    assert context is not None
    assert context["security_level"] == "high"

@pytest.mark.asyncio
async def test_agent_access_validation():
    coordinator = SecurityCoordinator()
    await coordinator.initialize()
    
    await coordinator.register_agent(
        "test_agent_2",
        ["read_data"],
        "medium"
    )
    
    # Should allow access to registered capability
    assert await coordinator.validate_agent_access("test_agent_2", "read_data") == True
    
    # Should deny access to unregistered capability
    assert await coordinator.validate_agent_access("test_agent_2", "write_data") == False

@pytest.mark.asyncio
async def test_security_status():
    coordinator = SecurityCoordinator()
    await coordinator.initialize()
    
    await coordinator.register_agent("agent1", ["auth"], "high")
    await coordinator.register_agent("agent2", ["data"], "medium")
    
    status = await coordinator.get_status()
    assert status["total_agents"] == 2
    assert status["active_agents"] >= 0
    assert status["encryption_active"] == True
