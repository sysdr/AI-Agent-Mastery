import pytest
import asyncio
from app.load_testing.engine import LoadTestEngine

@pytest.fixture
def load_test_engine():
    return LoadTestEngine()

def test_load_test_engine_health(load_test_engine):
    assert load_test_engine.health_check() == True

@pytest.mark.asyncio
async def test_start_load_test(load_test_engine):
    test_id = await load_test_engine.start_test("http://httpbin.org/get", 5, 10)
    assert test_id is not None
    assert len(test_id) > 0
    
    # Wait a moment for test to start
    await asyncio.sleep(2)
    
    results = await load_test_engine.get_test_results(test_id)
    assert results is not None
    assert results["status"] in ["started", "running", "completed", "failed"]
