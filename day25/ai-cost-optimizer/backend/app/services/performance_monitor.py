import asyncio
import redis
import json
import psutil
from datetime import datetime, timedelta
from typing import List, Dict, Any
from app.models.performance_metrics import PerformanceMetric

class PerformanceMonitorService:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.monitoring_active = False
    
    async def start_monitoring(self, agent_id: str):
        """Start continuous performance monitoring"""
        self.monitoring_active = True
        
        while self.monitoring_active:
            try:
                # Collect system metrics
                cpu_usage = psutil.cpu_percent(interval=1)
                memory = psutil.virtual_memory()
                
                # Get agent-specific metrics from Redis
                request_count = await self._get_recent_request_count(agent_id)
                error_rate = await self._calculate_error_rate(agent_id)
                avg_response_time = await self._get_avg_response_time(agent_id)
                
                metric = PerformanceMetric(
                    agent_id=agent_id,
                    cpu_usage=cpu_usage,
                    memory_usage=memory.percent,
                    request_count=request_count,
                    error_rate=error_rate,
                    avg_response_time=avg_response_time,
                    throughput=request_count / 60.0  # requests per second
                )
                
                await self.record_performance_metric(metric)
                
                # Check for performance issues
                await self._check_performance_alerts(metric)
                
                await asyncio.sleep(30)  # Monitor every 30 seconds
                
            except Exception as e:
                print(f"Performance monitoring error: {e}")
                await asyncio.sleep(5)
    
    async def stop_monitoring(self):
        """Stop performance monitoring"""
        self.monitoring_active = False
    
    async def record_performance_metric(self, metric: PerformanceMetric):
        """Record performance metric to Redis"""
        key = f"perf_metric:{metric.agent_id}:{metric.timestamp.timestamp()}"
        await self.redis.setex(
            key,
            timedelta(hours=24).total_seconds(),
            json.dumps(metric.to_dict())
        )
    
    async def get_performance_summary(self, agent_id: str, minutes: int = 60) -> Dict[str, Any]:
        """Get performance summary for specified time period"""
        start_time = datetime.now() - timedelta(minutes=minutes)
        
        pattern = f"perf_metric:{agent_id}:*"
        keys = await self.redis.keys(pattern)
        
        metrics = []
        for key in keys:
            data = await self.redis.get(key)
            if data:
                metric_dict = json.loads(data)
                metric_time = datetime.fromisoformat(metric_dict['timestamp'])
                
                if metric_time >= start_time:
                    metrics.append(metric_dict)
        
        if not metrics:
            return {'agent_id': agent_id, 'status': 'no_data'}
        
        # Calculate averages
        avg_cpu = sum(m['cpu_usage'] for m in metrics) / len(metrics)
        avg_memory = sum(m['memory_usage'] for m in metrics) / len(metrics)
        avg_response_time = sum(m['avg_response_time'] for m in metrics) / len(metrics)
        total_requests = sum(m['request_count'] for m in metrics)
        avg_error_rate = sum(m['error_rate'] for m in metrics) / len(metrics)
        
        return {
            'agent_id': agent_id,
            'period_minutes': minutes,
            'avg_cpu_usage': round(avg_cpu, 2),
            'avg_memory_usage': round(avg_memory, 2),
            'avg_response_time': round(avg_response_time, 2),
            'total_requests': total_requests,
            'avg_error_rate': round(avg_error_rate, 4),
            'performance_score': await self._calculate_performance_score(metrics),
            'status': await self._determine_status(avg_cpu, avg_memory, avg_response_time, avg_error_rate)
        }
    
    async def _get_recent_request_count(self, agent_id: str) -> int:
        """Get recent request count from cost metrics"""
        pattern = f"cost_metric:{agent_id}:*"
        keys = await self.redis.keys(pattern)
        
        recent_count = 0
        cutoff = datetime.now() - timedelta(minutes=1)
        
        for key in keys:
            data = await self.redis.get(key)
            if data:
                metric = json.loads(data)
                if datetime.fromisoformat(metric['timestamp']) >= cutoff:
                    recent_count += 1
        
        return recent_count
    
    async def _calculate_error_rate(self, agent_id: str) -> float:
        """Calculate error rate from recent requests"""
        pattern = f"cost_metric:{agent_id}:*"
        keys = await self.redis.keys(pattern)
        
        total_requests = 0
        failed_requests = 0
        cutoff = datetime.now() - timedelta(minutes=5)
        
        for key in keys:
            data = await self.redis.get(key)
            if data:
                metric = json.loads(data)
                if datetime.fromisoformat(metric['timestamp']) >= cutoff:
                    total_requests += 1
                    if not metric['success']:
                        failed_requests += 1
        
        return (failed_requests / max(total_requests, 1)) * 100
    
    async def _get_avg_response_time(self, agent_id: str) -> float:
        """Get average response time from recent requests"""
        pattern = f"cost_metric:{agent_id}:*"
        keys = await self.redis.keys(pattern)
        
        response_times = []
        cutoff = datetime.now() - timedelta(minutes=5)
        
        for key in keys:
            data = await self.redis.get(key)
            if data:
                metric = json.loads(data)
                if datetime.fromisoformat(metric['timestamp']) >= cutoff:
                    response_times.append(metric['response_time_ms'])
        
        return sum(response_times) / max(len(response_times), 1)
    
    async def _calculate_performance_score(self, metrics: List[Dict]) -> float:
        """Calculate overall performance score (0-100)"""
        if not metrics:
            return 0.0
        
        # Weighted scoring
        avg_cpu = sum(m['cpu_usage'] for m in metrics) / len(metrics)
        avg_memory = sum(m['memory_usage'] for m in metrics) / len(metrics)
        avg_response_time = sum(m['avg_response_time'] for m in metrics) / len(metrics)
        avg_error_rate = sum(m['error_rate'] for m in metrics) / len(metrics)
        
        # Score components (lower is better for CPU, memory, response time, error rate)
        cpu_score = max(0, 100 - avg_cpu)
        memory_score = max(0, 100 - avg_memory)
        response_score = max(0, 100 - (avg_response_time / 20))  # 2000ms = 0 score
        error_score = max(0, 100 - (avg_error_rate * 10))
        
        # Weighted average
        total_score = (cpu_score * 0.25 + memory_score * 0.25 + 
                      response_score * 0.3 + error_score * 0.2)
        
        return round(min(100, max(0, total_score)), 1)
    
    async def _determine_status(self, cpu: float, memory: float, 
                              response_time: float, error_rate: float) -> str:
        """Determine overall system status"""
        if error_rate > 5 or response_time > 5000:
            return "critical"
        elif cpu > 80 or memory > 80 or response_time > 2000:
            return "warning"
        else:
            return "healthy"
    
    async def _check_performance_alerts(self, metric: PerformanceMetric):
        """Check for performance-based alerts"""
        alerts = []
        
        if metric.cpu_usage > 80:
            alerts.append(f"High CPU usage: {metric.cpu_usage}%")
        
        if metric.memory_usage > 80:
            alerts.append(f"High memory usage: {metric.memory_usage}%")
        
        if metric.avg_response_time > 2000:
            alerts.append(f"High response time: {metric.avg_response_time}ms")
        
        if metric.error_rate > 5:
            alerts.append(f"High error rate: {metric.error_rate}%")
        
        if alerts:
            await self._send_performance_alert(metric.agent_id, alerts)
    
    async def _send_performance_alert(self, agent_id: str, alerts: List[str]):
        """Send performance alerts (store in Redis for dashboard)"""
        alert_key = f"alert:{agent_id}:{datetime.now().timestamp()}"
        alert_data = {
            'agent_id': agent_id,
            'timestamp': datetime.now().isoformat(),
            'type': 'performance',
            'alerts': alerts,
            'severity': 'high' if any('High' in alert for alert in alerts) else 'medium'
        }
        
        await self.redis.setex(
            alert_key,
            timedelta(hours=1).total_seconds(),
            json.dumps(alert_data)
        )
