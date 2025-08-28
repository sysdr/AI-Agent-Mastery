import asyncio
import time
from enum import Enum
from dataclasses import dataclass, field
from typing import Callable, Any, Optional
import logging

logger = logging.getLogger(__name__)

class CircuitState(Enum):
    CLOSED = "CLOSED"
    OPEN = "OPEN"
    HALF_OPEN = "HALF_OPEN"

@dataclass
class CircuitBreakerConfig:
    failure_threshold: int = 5
    recovery_timeout: int = 60
    expected_exception: type = Exception

@dataclass
class CircuitBreakerStats:
    failure_count: int = 0
    success_count: int = 0
    last_failure_time: Optional[float] = None
    state: CircuitState = CircuitState.CLOSED
    state_change_time: float = field(default_factory=time.time)

class CircuitBreaker:
    def __init__(self, config: CircuitBreakerConfig):
        self.config = config
        self.stats = CircuitBreakerStats()
        self._lock = asyncio.Lock()
    
    async def call(self, func: Callable, *args, **kwargs) -> Any:
        """Execute function with circuit breaker protection"""
        async with self._lock:
            await self._update_state()
            
            if self.stats.state == CircuitState.OPEN:
                raise CircuitBreakerOpenException(
                    f"Circuit breaker is OPEN. Last failure: {self.stats.last_failure_time}"
                )
            
            if self.stats.state == CircuitState.HALF_OPEN:
                logger.info("Circuit breaker in HALF_OPEN state, attempting call")
        
        try:
            result = await func(*args, **kwargs) if asyncio.iscoroutinefunction(func) else func(*args, **kwargs)
            await self._on_success()
            return result
            
        except self.config.expected_exception as e:
            await self._on_failure()
            raise e
    
    async def _update_state(self):
        """Update circuit breaker state based on current conditions"""
        now = time.time()
        
        if self.stats.state == CircuitState.OPEN:
            if now - self.stats.state_change_time >= self.config.recovery_timeout:
                logger.info("Circuit breaker transitioning from OPEN to HALF_OPEN")
                self.stats.state = CircuitState.HALF_OPEN
                self.stats.state_change_time = now
    
    async def _on_success(self):
        """Handle successful call"""
        async with self._lock:
            self.stats.success_count += 1
            
            if self.stats.state == CircuitState.HALF_OPEN:
                logger.info("Circuit breaker transitioning from HALF_OPEN to CLOSED")
                self.stats.state = CircuitState.CLOSED
                self.stats.failure_count = 0
                self.stats.state_change_time = time.time()
    
    async def _on_failure(self):
        """Handle failed call"""
        async with self._lock:
            self.stats.failure_count += 1
            self.stats.last_failure_time = time.time()
            
            if (self.stats.state in [CircuitState.CLOSED, CircuitState.HALF_OPEN] and 
                self.stats.failure_count >= self.config.failure_threshold):
                
                logger.warning(f"Circuit breaker transitioning to OPEN after {self.stats.failure_count} failures")
                self.stats.state = CircuitState.OPEN
                self.stats.state_change_time = time.time()
    
    def get_stats(self) -> dict:
        """Get current circuit breaker statistics"""
        return {
            "state": self.stats.state.value,
            "failure_count": self.stats.failure_count,
            "success_count": self.stats.success_count,
            "last_failure_time": self.stats.last_failure_time,
            "state_change_time": self.stats.state_change_time
        }

class CircuitBreakerOpenException(Exception):
    """Raised when circuit breaker is in OPEN state"""
    pass
