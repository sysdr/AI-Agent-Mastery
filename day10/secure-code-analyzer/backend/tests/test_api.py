import pytest
from fastapi.testclient import TestClient
from app.main import app

client = TestClient(app)

class TestSecurityAPI:
    
    def test_health_endpoint(self):
        response = client.get("/health")
        assert response.status_code == 200
        assert response.json()["status"] == "healthy"
    
    def test_analyze_code_endpoint(self):
        vulnerable_code = {
            "code": 'password = "hardcoded123"',
            "file_path": "test.py"
        }
        
        response = client.post("/api/security/analyze-code", json=vulnerable_code)
        assert response.status_code == 200
        
        data = response.json()
        assert "findings" in data
        assert data["summary"]["total_findings"] >= 0
    
    def test_get_patterns_endpoint(self):
        response = client.get("/api/security/patterns")
        assert response.status_code == 200
        
        data = response.json()
        assert "patterns" in data
        assert "sql_injection" in data["patterns"]
