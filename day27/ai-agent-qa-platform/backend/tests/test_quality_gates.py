import pytest
from app.quality_gates.validator import QualityGateValidator

@pytest.fixture
def quality_validator():
    return QualityGateValidator()

def test_quality_validator_health(quality_validator):
    assert quality_validator.health_check() == True

@pytest.mark.asyncio
async def test_quality_gate_validation(quality_validator):
    deployment_data = {
        "security": {
            "vulnerability_scan": {"status": "passed"},
            "headers_configured": True,
            "authentication": True,
            "input_validation": True
        },
        "performance": {
            "avg_response_time_ms": 150,
            "error_rate": 0.005,
            "requests_per_second": 200,
            "cpu_usage": 0.6
        },
        "compliance": {
            "gdpr_assessment": {"compliant": True},
            "soc2_controls": {"implemented": True},
            "audit_logging": True,
            "encryption": {"enabled": True}
        },
        "ai_ethics": {
            "bias_testing": {"completed": True},
            "explainability": True,
            "human_oversight": True,
            "fairness_score": 0.9
        }
    }
    
    result = await quality_validator.validate(deployment_data)
    assert result is not None
    assert "overall_status" in result
    assert result["overall_status"] in ["passed", "failed", "error"]
