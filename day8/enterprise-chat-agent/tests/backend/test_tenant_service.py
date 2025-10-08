import pytest
import asyncio
from services.tenant_service import TenantService

@pytest.mark.asyncio
async def test_tenant_info_retrieval():
    """Test tenant information retrieval"""
    service = TenantService()
    tenant_info = await service.get_tenant_info("tenant_1")
    
    assert tenant_info is not None
    assert "name" in tenant_info
    assert "quota_config" in tenant_info

@pytest.mark.asyncio
async def test_quota_calculation():
    """Test quota calculation"""
    service = TenantService()
    quota_info = await service.get_quota_info("tenant_1")
    
    assert quota_info is not None
    assert "max_connections" in quota_info
    assert "daily_message_limit" in quota_info
