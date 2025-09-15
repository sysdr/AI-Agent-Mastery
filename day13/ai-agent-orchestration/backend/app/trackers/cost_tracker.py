import time
from typing import Dict, List
import structlog
from datetime import datetime, timedelta

logger = structlog.get_logger()

class CostTracker:
    def __init__(self):
        self.costs = {}
        self.tool_rates = {}
        self.budget_limit = 100.0
        self.cost_history = []
        
    async def initialize(self):
        """Initialize cost tracking with tool rates"""
        self.tool_rates = {
            "web_search": 0.02,  # Per request
            "document_analyzer": 0.05,
            "fact_checker": 0.03,
            "content_synthesizer": 0.08,
            "bias_detector": 0.04,
            "gemini_api": 0.01  # Per 1K tokens
        }
        logger.info("Cost tracker initialized", rates=self.tool_rates)
    
    async def track_tool_usage(self, tool_name: str, execution_time: float) -> float:
        """Track cost for tool usage"""
        base_cost = self.tool_rates.get(tool_name, 0.01)
        
        # Calculate cost based on execution time and complexity
        time_multiplier = max(1.0, execution_time / 10.0)  # Scale with time
        total_cost = base_cost * time_multiplier
        
        # Track in current session
        if tool_name not in self.costs:
            self.costs[tool_name] = 0.0
        self.costs[tool_name] += total_cost
        
        # Add to history
        cost_entry = {
            "tool": tool_name,
            "cost": total_cost,
            "execution_time": execution_time,
            "timestamp": datetime.now().isoformat()
        }
        self.cost_history.append(cost_entry)
        
        # Check budget limits
        await self.check_budget_limits()
        
        logger.info("Cost tracked", tool=tool_name, cost=total_cost)
        return total_cost
    
    async def get_request_cost(self, request_id: str) -> float:
        """Get total cost for a specific request"""
        # For simplicity, return current session total
        return sum(self.costs.values())
    
    async def get_total_cost(self) -> float:
        """Get total cost across all tools"""
        return sum(self.costs.values())
    
    async def get_cost_by_tool(self) -> Dict[str, float]:
        """Get cost breakdown by tool"""
        return self.costs.copy()
    
    async def check_budget_limits(self):
        """Check if we're approaching budget limits"""
        total_cost = await self.get_total_cost()
        
        if total_cost > self.budget_limit * 0.8:
            logger.warning("Approaching budget limit", 
                         current_cost=total_cost, 
                         limit=self.budget_limit)
        
        if total_cost > self.budget_limit:
            logger.error("Budget limit exceeded", 
                        current_cost=total_cost, 
                        limit=self.budget_limit)
            raise ValueError("Budget limit exceeded")
    
    async def get_cost_analytics(self) -> Dict:
        """Get cost analytics and trends"""
        total_cost = await self.get_total_cost()
        cost_by_tool = await self.get_cost_by_tool()
        
        # Calculate cost trends
        recent_costs = [
            entry for entry in self.cost_history 
            if datetime.fromisoformat(entry["timestamp"]) > datetime.now() - timedelta(hours=1)
        ]
        
        hourly_cost = sum(entry["cost"] for entry in recent_costs)
        
        return {
            "total_cost": total_cost,
            "cost_by_tool": cost_by_tool,
            "hourly_cost": hourly_cost,
            "budget_remaining": max(0, self.budget_limit - total_cost),
            "budget_utilization": min(100, (total_cost / self.budget_limit) * 100)
        }
    
    async def cleanup(self):
        """Clean up cost tracking resources"""
        logger.info("Cost tracker cleanup completed")
