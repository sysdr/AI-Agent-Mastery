import pytest
import asyncio
from backend.services.backup_service import backup_service
from backend.models.schemas import RegionEnum

@pytest.mark.asyncio
async def test_create_snapshot():
    """Test backup snapshot creation"""
    test_data = {"test": "data", "conversations": ["conv1", "conv2"]}
    
    metadata = await backup_service.create_snapshot(RegionEnum.US_EAST, test_data)
    
    assert metadata.encrypted == True
    assert metadata.region == RegionEnum.US_EAST
    assert metadata.size_bytes > 0
    assert len(metadata.hash_sha256) == 64  # SHA-256 hash

@pytest.mark.asyncio
async def test_backup_restore():
    """Test backup restore functionality"""
    original_data = {"key": "value", "number": 42}
    
    # Create backup
    metadata = await backup_service.create_snapshot(RegionEnum.US_EAST, original_data)
    
    # Restore backup
    restored_data = await backup_service.restore_from_backup(metadata.backup_id)
    
    assert restored_data == original_data

def test_sovereignty_rules():
    """Test data sovereignty mapping"""
    eu_regions = backup_service._get_allowed_regions(RegionEnum.EU_WEST)
    assert "eu-west" in eu_regions
    assert "us-east" not in eu_regions
