import pytest
import asyncio
from app.core.circuit_breaker import CircuitBreaker, CircuitBreakerConfig, CircuitBreakerOpenException

@pytest.fixture
def circuit_breaker():
    config = CircuitBreakerConfig(failure_threshold=2, recovery_timeout=1)
    return CircuitBreaker(config)

@pytest.mark.asyncio
async def test_circuit_breaker_allows_success(circuit_breaker):
    async def successful_function():
        return "success"
    
    result = await circuit_breaker.call(successful_function)
    assert result == "success"
    assert circuit_breaker.stats.state.value == "CLOSED"

@pytest.mark.asyncio
async def test_circuit_breaker_opens_on_failures(circuit_breaker):
    async def failing_function():
        raise Exception("Test failure")
    
    # Trigger failures to open circuit
    for _ in range(2):
        with pytest.raises(Exception):
            await circuit_breaker.call(failing_function)
    
    # Circuit should be open now
    with pytest.raises(CircuitBreakerOpenException):
        await circuit_breaker.call(failing_function)
    
    assert circuit_breaker.stats.state.value == "OPEN"
