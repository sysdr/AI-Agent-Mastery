import pytest
import pytest_asyncio
import asyncio
from app.security.scanner import SecurityScanner

@pytest_asyncio.fixture
async def security_scanner():
    scanner = SecurityScanner()
    await scanner.initialize()
    return scanner

@pytest.mark.asyncio
async def test_security_scanner_initialization(security_scanner):
    assert await security_scanner.health_check() == True

@pytest.mark.asyncio
async def test_start_scan(security_scanner):
    scan_id = await security_scanner.start_scan("http://example.com")
    assert scan_id is not None
    assert len(scan_id) > 0

@pytest.mark.asyncio
async def test_vulnerability_detection(security_scanner):
    scan_id = await security_scanner.start_scan("http://example.com")
    await security_scanner.execute_scan(scan_id, "http://example.com")
    
    results = await security_scanner.get_scan_results(scan_id)
    assert results is not None
    assert results["status"] in ["completed", "failed"]
    if results["status"] == "completed":
        assert "vulnerabilities" in results
        assert "risk_score" in results
