import pytest
import asyncio
from unittest.mock import Mock, AsyncMock
import sys
import os
sys.path.insert(0, os.path.dirname(os.path.dirname(__file__)))

from app.agents.expert_agent import ExpertAgent
from app.core.models import ExpertiseLevel

@pytest.fixture
def mock_db():
    return Mock()

@pytest.fixture
def expert_agent(mock_db):
    agent = ExpertAgent("technology", mock_db)
    agent.model.generate_content_async = AsyncMock()
    return agent

@pytest.mark.asyncio
async def test_domain_expertise_check():
    mock_db = Mock()
    agent = ExpertAgent("technology", mock_db)
    
    # Mock the Gemini response
    mock_response = Mock()
    mock_response.text = '{"has_expertise": true, "relevance_score": 0.9, "domain_match": "technology", "reasoning": "Query is about software development"}'
    agent.model.generate_content_async = AsyncMock(return_value=mock_response)
    
    result = await agent._check_domain_expertise("How do I implement a REST API?")
    
    assert result["has_expertise"] is True
    assert result["relevance_score"] == 0.9

@pytest.mark.asyncio
async def test_confidence_calculation():
    mock_db = Mock()
    agent = ExpertAgent("technology", mock_db)
    
    from app.agents.expert_agent import ValidationStep
    
    steps = [
        ValidationStep("domain_check", {}, {"has_expertise": True}, 0.3, 0.2),
        ValidationStep("knowledge_retrieval", {}, {"entries": []}, 0.4, 0.5),
        ValidationStep("source_validation", {}, {"validated_sources": []}, 0.3, 1.0)
    ]
    
    confidence = agent._calculate_confidence(steps)
    assert 0.0 <= confidence <= 1.0

@pytest.mark.asyncio 
async def test_expertise_level_determination():
    mock_db = Mock()
    agent = ExpertAgent("technology", mock_db)
    
    assert agent._determine_expertise_level(0.95) == ExpertiseLevel.SPECIALIST
    assert agent._determine_expertise_level(0.85) == ExpertiseLevel.EXPERT
    assert agent._determine_expertise_level(0.7) == ExpertiseLevel.INTERMEDIATE
    assert agent._determine_expertise_level(0.3) == ExpertiseLevel.NOVICE

def test_explanation_generation():
    mock_db = Mock()
    agent = ExpertAgent("technology", mock_db)
    
    from app.agents.expert_agent import ValidationStep
    
    steps = [
        ValidationStep("domain_check", {}, {"relevance_score": 0.9}, 0.3, 0.2),
        ValidationStep("knowledge_retrieval", {}, {"entries": [1, 2, 3]}, 0.4, 0.5)
    ]
    
    explanation = agent._generate_explanation(steps, 0.8)
    assert "Domain relevance: 0.90" in explanation
    assert "Knowledge entries found: 3" in explanation
    assert "Overall confidence: 0.80" in explanation

if __name__ == "__main__":
    pytest.main([__file__])
