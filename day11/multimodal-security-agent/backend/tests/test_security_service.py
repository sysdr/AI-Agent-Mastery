import pytest
import asyncio
from unittest.mock import Mock, patch
from app.services.security_service import SecurityService

@pytest.fixture
def security_service():
    return SecurityService()

@pytest.mark.asyncio
async def test_classify_content_risk(security_service):
    """Test content risk classification"""
    content_data = {
        "type": "image",
        "filename": "test.jpg",
        "file_size": 1024
    }
    
    with patch.object(security_service.model, 'generate_content') as mock_generate:
        mock_response = Mock()
        mock_response.text = '{"overall_risk_score": 25, "threat_level": "LOW", "specific_risks": [], "recommendations": [], "confidence_score": 80}'
        mock_generate.return_value = mock_response
        
        result = await security_service.classify_content_risk(content_data)
        
        assert result["overall_risk_score"] == 25
        assert result["threat_level"] == "LOW"
        assert isinstance(result["specific_risks"], list)

@pytest.mark.asyncio
async def test_fallback_risk_analysis(security_service):
    """Test fallback analysis when AI service fails"""
    result = security_service._fallback_risk_analysis({})
    
    assert result["overall_risk_score"] == 25
    assert result["threat_level"] == "LOW"
    assert isinstance(result["specific_risks"], list)

def test_get_default_value(security_service):
    """Test default value retrieval"""
    assert security_service._get_default_value("overall_risk_score") == 25
    assert security_service._get_default_value("threat_level") == "LOW"
    assert security_service._get_default_value("nonexistent") is None
