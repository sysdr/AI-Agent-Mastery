import asyncio
import redis
import json
import numpy as np
from datetime import datetime, timedelta
from typing import List, Dict, Any, Tuple
from sklearn.linear_model import LinearRegression
from sklearn.preprocessing import StandardScaler

class ForecastingService:
    def __init__(self, redis_client):
        self.redis = redis_client
        self.scaler = StandardScaler()
    
    async def forecast_costs(self, agent_id: str, forecast_hours: int = 24) -> Dict[str, Any]:
        """Forecast costs for the specified time period"""
        # Get historical cost data
        historical_data = await self._get_historical_cost_data(agent_id, hours=72)
        
        if len(historical_data) < 10:
            return {
                'agent_id': agent_id,
                'forecast_hours': forecast_hours,
                'status': 'insufficient_data',
                'message': 'Need at least 10 historical data points'
            }
        
        # Prepare time series data
        timestamps, costs = self._prepare_time_series_data(historical_data)
        
        # Fit model and make predictions
        predicted_costs, confidence_interval = await self._fit_and_predict(
            timestamps, costs, forecast_hours
        )
        
        # Generate forecast summary
        current_hourly_rate = await self._calculate_current_hourly_rate(agent_id)
        forecasted_total = sum(predicted_costs)
        
        return {
            'agent_id': agent_id,
            'forecast_hours': forecast_hours,
            'current_hourly_rate': round(current_hourly_rate, 4),
            'forecasted_total_cost': round(forecasted_total, 4),
            'forecasted_hourly_costs': [round(cost, 4) for cost in predicted_costs],
            'confidence_lower': [round(cost, 4) for cost in confidence_interval[0]],
            'confidence_upper': [round(cost, 4) for cost in confidence_interval[1]],
            'trend': await self._analyze_trend(costs),
            'risk_assessment': await self._assess_cost_risk(forecasted_total, current_hourly_rate),
            'recommendations': await self._generate_recommendations(
                agent_id, forecasted_total, current_hourly_rate
            )
        }
    
    async def _get_historical_cost_data(self, agent_id: str, hours: int) -> List[Dict]:
        """Get historical cost data from Redis"""
        start_time = datetime.now() - timedelta(hours=hours)
        pattern = f"cost_metric:{agent_id}:*"
        keys = await self.redis.keys(pattern)
        
        historical_data = []
        for key in keys:
            data = await self.redis.get(key)
            if data:
                metric = json.loads(data)
                metric_time = datetime.fromisoformat(metric['timestamp'])
                
                if metric_time >= start_time:
                    historical_data.append(metric)
        
        # Sort by timestamp
        return sorted(historical_data, key=lambda x: x['timestamp'])
    
    def _prepare_time_series_data(self, historical_data: List[Dict]) -> Tuple[np.ndarray, np.ndarray]:
        """Prepare time series data for modeling"""
        # Group by hour and sum costs
        hourly_costs = {}
        
        for item in historical_data:
            timestamp = datetime.fromisoformat(item['timestamp'])
            hour_key = timestamp.replace(minute=0, second=0, microsecond=0)
            
            if hour_key not in hourly_costs:
                hourly_costs[hour_key] = 0.0
            hourly_costs[hour_key] += item['cost_usd']
        
        # Convert to arrays
        sorted_hours = sorted(hourly_costs.keys())
        timestamps = np.array([
            (hour - sorted_hours[0]).total_seconds() / 3600 
            for hour in sorted_hours
        ]).reshape(-1, 1)
        costs = np.array([hourly_costs[hour] for hour in sorted_hours])
        
        return timestamps, costs
    
    async def _fit_and_predict(self, timestamps: np.ndarray, costs: np.ndarray, 
                              forecast_hours: int) -> Tuple[List[float], Tuple[List[float], List[float]]]:
        """Fit regression model and make predictions"""
        try:
            # Fit linear regression model
            model = LinearRegression()
            model.fit(timestamps, costs)
            
            # Generate future timestamps
            last_timestamp = timestamps[-1][0]
            future_timestamps = np.array([
                [last_timestamp + i + 1] for i in range(forecast_hours)
            ])
            
            # Make predictions
            predictions = model.predict(future_timestamps)
            
            # Calculate confidence intervals (simple approximation)
            residuals = costs - model.predict(timestamps)
            std_error = np.std(residuals)
            
            confidence_lower = predictions - 1.96 * std_error
            confidence_upper = predictions + 1.96 * std_error
            
            return (
                predictions.tolist(),
                (confidence_lower.tolist(), confidence_upper.tolist())
            )
            
        except Exception as e:
            print(f"Forecasting error: {e}")
            # Fallback to simple average
            avg_cost = np.mean(costs)
            return (
                [avg_cost] * forecast_hours,
                ([avg_cost * 0.8] * forecast_hours, [avg_cost * 1.2] * forecast_hours)
            )
    
    async def _calculate_current_hourly_rate(self, agent_id: str) -> float:
        """Calculate current hourly cost rate"""
        recent_summary = await self._get_recent_cost_summary(agent_id, hours=1)
        return recent_summary.get('total_cost', 0.0)
    
    async def _get_recent_cost_summary(self, agent_id: str, hours: int) -> Dict:
        """Get recent cost summary"""
        start_time = datetime.now() - timedelta(hours=hours)
        pattern = f"cost_metric:{agent_id}:*"
        keys = await self.redis.keys(pattern)
        
        total_cost = 0.0
        request_count = 0
        
        for key in keys:
            data = await self.redis.get(key)
            if data:
                metric = json.loads(data)
                metric_time = datetime.fromisoformat(metric['timestamp'])
                
                if metric_time >= start_time:
                    total_cost += metric['cost_usd']
                    request_count += 1
        
        return {
            'total_cost': total_cost,
            'request_count': request_count,
            'avg_cost_per_request': total_cost / max(request_count, 1)
        }
    
    async def _analyze_trend(self, costs: np.ndarray) -> str:
        """Analyze cost trend"""
        if len(costs) < 3:
            return "insufficient_data"
        
        # Simple trend analysis using linear regression slope
        x = np.arange(len(costs)).reshape(-1, 1)
        model = LinearRegression().fit(x, costs)
        slope = model.coef_[0]
        
        if slope > 0.001:
            return "increasing"
        elif slope < -0.001:
            return "decreasing"
        else:
            return "stable"
    
    async def _assess_cost_risk(self, forecasted_total: float, current_rate: float) -> Dict[str, Any]:
        """Assess cost risk based on forecast"""
        # Define risk thresholds
        high_risk_threshold = 80.0  # $80/day
        medium_risk_threshold = 50.0  # $50/day
        
        if forecasted_total > high_risk_threshold:
            risk_level = "high"
            message = f"Forecasted cost (${forecasted_total:.2f}) exceeds high risk threshold"
        elif forecasted_total > medium_risk_threshold:
            risk_level = "medium"
            message = f"Forecasted cost (${forecasted_total:.2f}) approaching risk threshold"
        else:
            risk_level = "low"
            message = "Forecasted costs within acceptable range"
        
        # Calculate risk factors
        rate_change = (forecasted_total / 24) / max(current_rate, 0.001) - 1
        
        return {
            'risk_level': risk_level,
            'message': message,
            'rate_change_percent': round(rate_change * 100, 1),
            'days_until_budget_exceeded': await self._calculate_budget_runway(forecasted_total)
        }
    
    async def _calculate_budget_runway(self, daily_cost: float) -> float:
        """Calculate days until budget is exceeded"""
        monthly_budget = 2000.0  # $2000/month default budget
        current_month_spend = 500.0  # Mock current spend
        
        remaining_budget = monthly_budget - current_month_spend
        
        if daily_cost <= 0:
            return float('inf')
        
        return remaining_budget / daily_cost
    
    async def _generate_recommendations(self, agent_id: str, forecasted_total: float, 
                                      current_rate: float) -> List[str]:
        """Generate cost optimization recommendations"""
        recommendations = []
        
        # Get current performance metrics
        perf_summary = await self._get_performance_context(agent_id)
        
        if forecasted_total > 80.0:
            recommendations.append("Consider implementing request throttling during peak hours")
            recommendations.append("Enable response caching for repeated queries")
            
        if current_rate > 5.0:  # $5/hour
            recommendations.append("Switch to more cost-effective model for routine tasks")
            recommendations.append("Implement query optimization to reduce token usage")
            
        if perf_summary.get('error_rate', 0) > 2:
            recommendations.append("Investigate and fix errors to reduce retry costs")
            
        if len(recommendations) == 0:
            recommendations.append("Current cost trajectory looks healthy")
            
        return recommendations
    
    async def _get_performance_context(self, agent_id: str) -> Dict:
        """Get performance context for recommendations"""
        pattern = f"perf_metric:{agent_id}:*"
        keys = await self.redis.keys(pattern)
        
        if not keys:
            return {}
        
        # Get latest performance metric
        latest_key = max(keys, key=lambda k: k.split(':')[-1])
        data = await self.redis.get(latest_key)
        
        if data:
            return json.loads(data)
        
        return {}
