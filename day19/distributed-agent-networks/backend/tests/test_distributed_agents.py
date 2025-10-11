import pytest
import asyncio
from app.agents.distributed_agent import DistributedAgentNetwork

@pytest.mark.asyncio
async def test_network_initialization():
    network = DistributedAgentNetwork()
    await network.initialize_network(num_agents=2)
    
    assert len(network.agents) == 2
    assert all(agent.status == "active" for agent in network.agents.values())

@pytest.mark.asyncio
async def test_encrypted_messaging():
    network = DistributedAgentNetwork()
    await network.initialize_network(num_agents=2)
    
    agents = list(network.agents.keys())
    result = await network.send_encrypted_message(
        agents[0], agents[1], "test_message", {"data": "test"}
    )
    
    assert result is True
    assert len(network.message_history) == 1

@pytest.mark.asyncio
async def test_collaborative_problem_solving():
    network = DistributedAgentNetwork()
    await network.initialize_network(num_agents=3)
    
    result = await network.solve_collaboratively({
        "problem": "What is 2 + 2?"
    })
    
    assert "consensus_solution" in result
    assert result["participating_agents"] == 3
    assert "confidence" in result

if __name__ == "__main__":
    asyncio.run(test_network_initialization())
    asyncio.run(test_encrypted_messaging())
    asyncio.run(test_collaborative_problem_solving())
    print("✅ All tests passed!")
