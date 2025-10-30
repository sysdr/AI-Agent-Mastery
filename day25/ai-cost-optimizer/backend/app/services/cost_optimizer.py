import asyncio
import redis
import json
from datetime import datetime, timedelta
from typing import List, Dict, Any, Optional
from app.models.cost_metrics import CostMetric
from app.models.optimization_rules import OptimizationRule, OptimizationAction

class CostOptimizerService:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.optimization_rules = self._load_default_rules()
    
    def _load_default_rules(self) -> List[OptimizationRule]:
        return [
            OptimizationRule(
                name="High Cost Alert",
                condition="cost_per_hour > 80",
                action=OptimizationAction.THROTTLE_REQUESTS,
                parameters={"throttle_rate": 0.5}
            ),
            OptimizationRule(
                name="Switch to Cheaper Model",
                condition="avg_cost_per_request > 0.05 AND success_rate > 0.95",
                action=OptimizationAction.SWITCH_MODEL,
                parameters={"target_model": "gemini-pro"}
            )
        ]
    
    async def record_cost_metric(self, metric: CostMetric) -> None:
        """Record cost metric to Redis with TTL"""
        key = f"cost_metric:{metric.agent_id}:{metric.timestamp.timestamp()}"
        await self.redis.setex(
            key, 
            timedelta(hours=24).total_seconds(), 
            json.dumps(metric.to_dict())
        )
        
        # Update running totals
        hourly_key = f"cost_hourly:{metric.agent_id}:{datetime.now().hour}"
        await self.redis.incrbyfloat(hourly_key, metric.cost_usd)
        await self.redis.expire(hourly_key, timedelta(hours=2).total_seconds())
    
    async def get_cost_summary(self, agent_id: str, hours: int = 1) -> Dict[str, Any]:
        """Get cost summary for specified time period"""
        start_time = datetime.now() - timedelta(hours=hours)
        
        # Get metrics from Redis
        pattern = f"cost_metric:{agent_id}:*"
        keys = await self.redis.keys(pattern)
        
        metrics = []
        total_cost = 0.0
        total_tokens = 0
        
        for key in keys:
            data = await self.redis.get(key)
            if data:
                metric_dict = json.loads(data)
                metric_time = datetime.fromisoformat(metric_dict['timestamp'])
                
                if metric_time >= start_time:
                    metrics.append(metric_dict)
                    total_cost += metric_dict['cost_usd']
                    total_tokens += metric_dict['tokens_used']
        
        return {
            'agent_id': agent_id,
            'period_hours': hours,
            'total_cost': round(total_cost, 4),
            'total_tokens': total_tokens,
            'average_cost_per_request': round(total_cost / max(len(metrics), 1), 4),
            'request_count': len(metrics),
            'cost_trend': await self._calculate_cost_trend(agent_id, metrics)
        }
    
    async def _calculate_cost_trend(self, agent_id: str, metrics: List[Dict]) -> str:
        """Calculate cost trend (increasing, decreasing, stable)"""
        if len(metrics) < 2:
            return "insufficient_data"
        
        # Sort by timestamp
        sorted_metrics = sorted(metrics, key=lambda x: x['timestamp'])
        
        # Compare first and second half
        mid_point = len(sorted_metrics) // 2
        first_half_avg = sum(m['cost_usd'] for m in sorted_metrics[:mid_point]) / mid_point
        second_half_avg = sum(m['cost_usd'] for m in sorted_metrics[mid_point:]) / (len(sorted_metrics) - mid_point)
        
        if second_half_avg > first_half_avg * 1.1:
            return "increasing"
        elif second_half_avg < first_half_avg * 0.9:
            return "decreasing"
        else:
            return "stable"
    
    async def check_optimization_opportunities(self, agent_id: str) -> List[Dict[str, Any]]:
        """Check for optimization opportunities based on rules"""
        summary = await self.get_cost_summary(agent_id, hours=1)
        opportunities = []
        
        for rule in self.optimization_rules:
            if not rule.enabled:
                continue
                
            if await self._evaluate_rule_condition(rule, summary):
                opportunities.append({
                    'rule_name': rule.name,
                    'action': rule.action.value,
                    'parameters': rule.parameters,
                    'estimated_savings': await self._estimate_savings(rule, summary)
                })
        
        return opportunities
    
    async def _evaluate_rule_condition(self, rule: OptimizationRule, summary: Dict) -> bool:
        """Evaluate if optimization rule condition is met"""
        # Simple condition evaluation - in production, use a proper parser
        condition = rule.condition.lower()
        
        if "cost_per_hour" in condition:
            cost_per_hour = summary['total_cost']
            if ">" in condition:
                threshold = float(condition.split(">")[1].strip())
                return cost_per_hour > threshold
        
        return False
    
    async def _estimate_savings(self, rule: OptimizationRule, summary: Dict) -> float:
        """Estimate potential cost savings from optimization"""
        if rule.action == OptimizationAction.THROTTLE_REQUESTS:
            throttle_rate = rule.parameters.get('throttle_rate', 0.5)
            return summary['total_cost'] * throttle_rate
        elif rule.action == OptimizationAction.SWITCH_MODEL:
            # Assume 30% savings with cheaper model
            return summary['total_cost'] * 0.3
        
        return 0.0
