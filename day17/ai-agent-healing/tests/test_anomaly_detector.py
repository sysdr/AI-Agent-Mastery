import pytest
import asyncio
from backend.app.monitoring.anomaly_detector import AnomalyDetector

@pytest.mark.asyncio
async def test_anomaly_detector_initialization():
    detector = AnomalyDetector()
    assert detector.baseline_metrics is not None
    assert detector.anomaly_threshold == 2.0

@pytest.mark.asyncio
async def test_collect_metrics():
    detector = AnomalyDetector()
    metrics = await detector._collect_metrics()
    
    assert "timestamp" in metrics
    assert "request_rate" in metrics
    assert "cpu_usage" in metrics
    assert isinstance(metrics["request_rate"], (int, float))

@pytest.mark.asyncio
async def test_detect_anomalies():
    detector = AnomalyDetector()
    
    # Create test metrics with high CPU
    test_metrics = {
        "timestamp": "2024-01-01T00:00:00",
        "request_rate": 1000,  # 10x baseline
        "error_rate": 0.01,
        "response_time": 0.2,
        "cpu_usage": 0.4,
        "memory_usage": 0.6,
        "failed_auth_attempts": 0,
        "suspicious_ips": []
    }
    
    anomalies = await detector._detect_anomalies(test_metrics)
    assert len(anomalies) > 0
    
    # Check if high request rate anomaly is detected
    request_anomaly = next((a for a in anomalies if a["metric"] == "request_rate"), None)
    assert request_anomaly is not None
    assert request_anomaly["severity"] in ["medium", "high"]

@pytest.mark.asyncio 
async def test_security_anomaly_detection():
    detector = AnomalyDetector()
    
    # Test metrics with security issues
    test_metrics = {
        "timestamp": "2024-01-01T00:00:00",
        "request_rate": 100,
        "error_rate": 0.01,
        "response_time": 0.2,
        "cpu_usage": 0.4,
        "memory_usage": 0.6,
        "failed_auth_attempts": 50,  # High failed attempts
        "suspicious_ips": ["192.168.1.100", "192.168.1.101"]
    }
    
    anomalies = await detector._detect_anomalies(test_metrics)
    
    # Should detect brute force attack
    auth_anomaly = next((a for a in anomalies if a["metric"] == "failed_auth_attempts"), None)
    assert auth_anomaly is not None
    assert auth_anomaly["type"] == "security"
    
    # Should detect suspicious IP activity
    ip_anomaly = next((a for a in anomalies if a["metric"] == "suspicious_ips"), None)
    assert ip_anomaly is not None
    assert ip_anomaly["type"] == "security"

if __name__ == "__main__":
    pytest.main([__file__])
