from typing import Dict, Optional
from datetime import datetime, timedelta
import asyncio
from models.database import SessionLocal, ResourceUsage, Agent

class QuotaManager:
    """Manage resource quotas for agents"""
    
    DEFAULT_QUOTAS = {
        "api_calls": 1000,      # per day
        "compute_time": 1800,   # seconds per day
        "cost": 10.0           # dollars per day
    }
    
    def __init__(self):
        self.quotas = self.DEFAULT_QUOTAS.copy()
        
    async def check_quota(self, agent_id: int, resource_type: str, amount: float) -> bool:
        """Check if agent has enough quota for resource usage"""
        db = SessionLocal()
        try:
            # Get today's usage
            today = datetime.utcnow().date()
            usage = db.query(ResourceUsage).filter(
                ResourceUsage.agent_id == agent_id,
                ResourceUsage.resource_type == resource_type,
                ResourceUsage.date >= today
            ).all()
            
            total_used = sum(u.amount_used for u in usage)
            quota_limit = self.quotas.get(resource_type, 0)
            
            return (total_used + amount) <= quota_limit
            
        finally:
            db.close()
    
    async def consume_quota(self, agent_id: int, resource_type: str, amount: float) -> bool:
        """Consume quota for resource usage"""
        db = SessionLocal()
        try:
            if not await self.check_quota(agent_id, resource_type, amount):
                return False
                
            # Record usage
            usage = ResourceUsage(
                agent_id=agent_id,
                resource_type=resource_type,
                amount_used=amount,
                quota_limit=self.quotas.get(resource_type, 0)
            )
            db.add(usage)
            db.commit()
            return True
            
        finally:
            db.close()
    
    async def get_usage_stats(self, agent_id: int) -> Dict[str, Dict[str, float]]:
        """Get current usage statistics for agent"""
        db = SessionLocal()
        try:
            today = datetime.utcnow().date()
            usage = db.query(ResourceUsage).filter(
                ResourceUsage.agent_id == agent_id,
                ResourceUsage.date >= today
            ).all()
            
            stats = {}
            for resource_type in self.quotas:
                used = sum(u.amount_used for u in usage if u.resource_type == resource_type)
                limit = self.quotas[resource_type]
                stats[resource_type] = {
                    "used": used,
                    "limit": limit,
                    "remaining": limit - used,
                    "percentage": (used / limit) * 100 if limit > 0 else 0
                }
            
            return stats
            
        finally:
            db.close()

    async def reset_daily_quotas(self):
        """Reset quotas daily - called by scheduler"""
        # In production, this would be handled by a cron job or scheduler
        pass
