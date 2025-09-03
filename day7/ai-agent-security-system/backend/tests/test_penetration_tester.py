import pytest
import asyncio
from app.penetration_tester import PenetrationTester

@pytest.mark.asyncio
async def test_security_scan():
    tester = PenetrationTester()
    
    scan_id = "test_scan_001"
    results = await tester.run_comprehensive_scan(scan_id)
    
    assert results["scan_id"] == scan_id
    assert "tests" in results
    assert "vulnerabilities_found" in results
    assert "risk_level" in results
    
    # Should have run multiple test types
    assert len(results["tests"]) >= 3

@pytest.mark.asyncio
async def test_vulnerability_report():
    tester = PenetrationTester()
    
    # Run a scan to generate vulnerabilities
    await tester.run_comprehensive_scan("test_scan_002")
    
    report = await tester.get_vulnerability_report()
    
    assert "total_vulnerabilities" in report
    assert "severity_breakdown" in report
    assert "risk_score" in report
    
    # Risk score should be between 0 and 100
    assert 0 <= report["risk_score"] <= 100
