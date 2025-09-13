import pytest
import asyncio
import pandas as pd
from datetime import datetime
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from backend.app.services.bias_detection import BiasDetectionService
from backend.app.models.schemas import UserInteraction, InteractionType

@pytest.fixture
async def bias_service():
    service = BiasDetectionService()
    await service.initialize()
    yield service
    # Cleanup if needed

@pytest.mark.asyncio
async def test_demographic_parity_check(bias_service):
    # Create test data with bias
    test_data = pd.DataFrame([
        {'user_id': f'user_{i}', 'interaction_type': 'like', 'gender': 'male' if i % 2 == 0 else 'female'}
        for i in range(100)
    ])
    
    # Introduce bias - males get more likes
    for i in range(0, 100, 4):
        test_data.loc[i, 'interaction_type'] = 'dislike'
    
    results = bias_service.check_demographic_parity(test_data)
    
    assert len(results) > 0
    gender_result = next((r for r in results if r['attribute'] == 'gender'), None)
    assert gender_result is not None

@pytest.mark.asyncio
async def test_bias_report_generation(bias_service):
    # Add some test interactions
    interactions = [
        {
            'user_id': f'user_{i}',
            'item_id': f'item_{i}',
            'interaction_type': 'like' if i % 3 == 0 else 'view',
            'timestamp': datetime.utcnow().isoformat(),
            'demographics': {
                'gender': 'male' if i % 2 == 0 else 'female',
                'age_group': 'young' if i < 50 else 'old'
            }
        }
        for i in range(100)
    ]
    
    # Store interactions for analysis
    for interaction in interactions:
        await bias_service.redis_client.lpush('bias_analysis_queue', str(interaction))
    
    report = await bias_service.generate_bias_report()
    
    assert report is not None
    assert report.timestamp is not None
    assert report.overall_bias_score >= 0

if __name__ == "__main__":
    pytest.main([__file__])
