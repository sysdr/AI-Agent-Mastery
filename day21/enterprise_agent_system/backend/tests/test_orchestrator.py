import pytest
import asyncio
from app.orchestration.orchestrator import AgentOrchestrator

@pytest.mark.asyncio
async def test_orchestrator_initialization():
    orchestrator = AgentOrchestrator()
    await orchestrator.initialize()
    
    assert len(orchestrator.agents) == 3
    assert "data_agent" in orchestrator.agents
    assert "security_agent" in orchestrator.agents
    assert "compliance_agent" in orchestrator.agents

@pytest.mark.asyncio
async def test_task_execution():
    orchestrator = AgentOrchestrator()
    await orchestrator.initialize()
    
    task_data = {
        "type": "data_processing",
        "data": "test data"
    }
    
    result = await orchestrator.execute_task(task_data)
    
    assert result["status"] in ["completed", "completed_with_fallback"]
    assert "task_id" in result
    assert "agent" in result

if __name__ == "__main__":
    pytest.main([__file__])
