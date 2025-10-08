import pytest
import asyncio
from app.services.personality_monitor import PersonalityMonitor

@pytest.mark.asyncio
async def test_personality_monitor():
    monitor = PersonalityMonitor()
    
    personality_profile = {
        "tone": "professional_friendly",
        "expertise_level": "senior_engineer", 
        "communication_style": "direct_helpful"
    }
    
    # Test consistent response
    response = "Here's how to implement distributed caching in your system. You'll want to consider Redis or Memcached for this use case."
    
    result = await monitor.validate_response("test_session", response, personality_profile)
    
    assert "is_consistent" in result
    assert "consistency_score" in result
    assert result["consistency_score"] >= 0.0
    assert result["consistency_score"] <= 1.0

@pytest.mark.asyncio
async def test_feature_extraction():
    monitor = PersonalityMonitor()
    
    response = "Great question! Let me help you understand microservices architecture. This is a complex topic that requires careful consideration."
    
    features = monitor._extract_response_features(response)
    
    assert features["word_count"] > 0
    assert features["technical_terms"] >= 0
    assert features["politeness_markers"] >= 0
    assert "embedding" in features
