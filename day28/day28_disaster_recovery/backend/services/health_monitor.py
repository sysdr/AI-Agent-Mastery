import asyncio
import random
from datetime import datetime
from typing import Dict
from backend.models.schemas import HealthMetrics, RegionEnum, SystemState
from backend.config.settings import settings

class HealthMonitor:
    def __init__(self):
        self.metrics: Dict[str, HealthMetrics] = {}
        self.system_state = SystemState.HEALTHY
        self.failure_injected = False
        
    async def collect_metrics(self, region: RegionEnum) -> HealthMetrics:
        """Collect health metrics for a region"""
        # Simulate metrics (in production, these would be real)
        if self.failure_injected and region == RegionEnum.US_EAST:
            latency_ms = random.uniform(800, 1500)
            error_rate = random.uniform(0.05, 0.15)
        else:
            latency_ms = random.uniform(50, 300)
            error_rate = random.uniform(0.0001, 0.005)
        
        cpu_usage = random.uniform(30, 70)
        memory_usage = random.uniform(40, 80)
        
        is_healthy = (
            latency_ms < settings.LATENCY_THRESHOLD_MS and
            error_rate < settings.ERROR_RATE_THRESHOLD
        )
        
        metrics = HealthMetrics(
            region=region,
            latency_ms=latency_ms,
            error_rate=error_rate,
            cpu_usage=cpu_usage,
            memory_usage=memory_usage,
            timestamp=datetime.utcnow(),
            is_healthy=is_healthy
        )
        
        self.metrics[region.value] = metrics
        return metrics
    
    async def continuous_monitoring(self):
        """Run continuous health monitoring"""
        while True:
            try:
                for region in RegionEnum:
                    await self.collect_metrics(region)
                
                # Update system state
                self._update_system_state()
                
                await asyncio.sleep(5)
            except Exception as e:
                print(f"✗ Monitoring error: {str(e)}")
                await asyncio.sleep(5)
    
    def _update_system_state(self):
        """Update overall system state based on metrics"""
        primary_metrics = self.metrics.get(settings.PRIMARY_REGION)
        
        if not primary_metrics:
            return
        
        if not primary_metrics.is_healthy:
            if primary_metrics.error_rate > 0.05:
                self.system_state = SystemState.CRITICAL
            else:
                self.system_state = SystemState.DEGRADED
        elif self.system_state in [SystemState.DEGRADED, SystemState.CRITICAL]:
            # Check if recovered
            if primary_metrics.is_healthy:
                self.system_state = SystemState.HEALTHY
    
    def inject_failure(self):
        """Inject simulated failure for testing"""
        self.failure_injected = True
        print("⚠ Failure injected in primary region")
    
    def clear_failure(self):
        """Clear simulated failure"""
        self.failure_injected = False
        print("✓ Failure cleared")

health_monitor = HealthMonitor()
