import pytest
import asyncio
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.services.preference_learning import PreferenceLearningService
from backend.app.models.schemas import UserInteraction, InteractionType

@pytest.fixture
async def preference_service():
    service = PreferenceLearningService()
    await service.initialize()
    yield service
    # Cleanup if needed

@pytest.mark.asyncio
async def test_add_interaction(preference_service):
    interaction = UserInteraction(
        user_id="test_user_001",
        item_id="movie_123",
        interaction_type=InteractionType.LIKE,
        context={"genre": "sci-fi", "rating": 4.5}
    )
    
    result = await preference_service.add_interaction(interaction)
    
    assert result.interaction_id is not None
    assert result.remaining_budget < 1.0
    assert result.noise_added > 0

@pytest.mark.asyncio
async def test_privacy_budget_management(preference_service):
    user_id = "test_user_budget"
    
    initial_budget = await preference_service.check_user_privacy_budget(user_id)
    assert initial_budget == 1.0
    
    await preference_service.deduct_privacy_budget(user_id, 0.1)
    
    remaining_budget = await preference_service.check_user_privacy_budget(user_id)
    assert remaining_budget == 0.9

if __name__ == "__main__":
    pytest.main([__file__])
