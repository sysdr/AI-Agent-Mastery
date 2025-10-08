import pytest
import tempfile
import os
from PIL import Image
from app.services.image_service import ImageSecurityService

@pytest.fixture
def image_service():
    return ImageSecurityService()

@pytest.fixture
def test_image():
    """Create a test image file"""
    with tempfile.NamedTemporaryFile(suffix='.jpg', delete=False) as f:
        img = Image.new('RGB', (100, 100), color='red')
        img.save(f.name, 'JPEG')
        yield f.name
    os.unlink(f.name)

def test_validate_image_file(image_service, test_image):
    """Test image file validation"""
    result = image_service._validate_image_file(test_image)
    
    assert result["is_valid"] is True
    assert result["file_size"] > 0
    assert result["format"] == "JPEG"
    assert "100x100" in result["dimensions"]

def test_check_malware_signatures(image_service, test_image):
    """Test malware signature detection"""
    result = image_service._check_malware_signatures(test_image)
    
    assert "file_hash" in result
    assert isinstance(result["is_suspicious"], bool)
    assert isinstance(result["indicators"], list)

def test_analyze_image_content(image_service, test_image):
    """Test image content analysis"""
    result = image_service._analyze_image_content(test_image)
    
    assert result["analysis_possible"] is True
    assert "100x100" in result["dimensions"]
    assert isinstance(result["flags"], list)

@pytest.mark.asyncio
async def test_analyze_image_complete(image_service, test_image):
    """Test complete image analysis"""
    result = await image_service.analyze_image(test_image, "test.jpg")
    
    assert result.content_type == "image"
    assert result.filename == "test.jpg"
    assert hasattr(result, 'risk_score')
    assert hasattr(result, 'threat_level')
