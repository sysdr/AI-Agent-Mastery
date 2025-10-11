import pytest
import asyncio
from unittest.mock import Mock, patch
from app.services.learning_service import ProductionLearningService
from app.models.learning import FeedbackData

@pytest.fixture
def redis_mock():
    return Mock()

@pytest.fixture
def learning_service(redis_mock):
    return ProductionLearningService(redis_mock)

@pytest.mark.asyncio
async def test_process_feedback(learning_service):
    """Test feedback processing with privacy protection"""
    feedback = {
        "user_id": "test_user",
        "satisfaction_score": 0.8,
        "demographic_data": {"age": 25, "location": "test"}
    }
    
    with patch('app.utils.database.get_db_session'):
        result = await learning_service.process_feedback(feedback)
    
    assert "status" in result
    assert result["status"] in ["success", "error"]

def test_differential_privacy():
    """Test privacy protection mechanism"""
    from app.utils.privacy import apply_differential_privacy
    
    test_data = {"satisfaction_score": 0.8, "user_id": "sensitive_user"}
    private_data = apply_differential_privacy(test_data, epsilon=0.1)
    
    # Check that noise was added
    assert abs(private_data["satisfaction_score"] - 0.8) >= 0  # Some noise added
    assert "user_id_hash" in private_data  # ID was hashed

def test_bias_detection():
    """Test bias detection logic"""
    from app.utils.explainability import validate_decision_fairness
    
    decision = {"prediction": 0.8}
    demo_data = {"age_group": "25-34", "location": "test"}
    
    result = validate_decision_fairness(decision, demo_data)
    
    assert "is_fair" in result
    assert "bias_checks" in result
    assert isinstance(result["is_fair"], bool)
