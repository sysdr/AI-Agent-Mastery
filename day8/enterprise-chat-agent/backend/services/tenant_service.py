from typing import Dict, Any, Optional, List
import structlog
import jwt
from datetime import datetime, timedelta
import redis.asyncio as redis
import json
import uuid
import asyncio
from config.settings import Settings

logger = structlog.get_logger()
settings = Settings()

class TenantService:
    def __init__(self):
        self.redis_client = redis.Redis(host=settings.redis_host, port=settings.redis_port, decode_responses=True)
        
        # Initialize demo tenants - will be called when needed
        self._demo_tenants_initialized = False
    
    async def _init_demo_tenants(self):
        """Initialize demo tenant data"""
        demo_tenants = {
            "tenant_1": {
                "name": "Acme Corp",
                "domain": "acme.com",
                "quota_config": {
                    "max_connections": 50,
                    "daily_messages": 5000,
                    "context_size": 4096
                },
                "brand_config": {
                    "brand_name": "Acme Customer Support",
                    "response_tone": "professional",
                    "primary_color": "#2563eb"
                }
            },
            "tenant_2": {
                "name": "TechStart Inc",
                "domain": "techstart.io", 
                "quota_config": {
                    "max_connections": 25,
                    "daily_messages": 2500,
                    "context_size": 2048
                },
                "brand_config": {
                    "brand_name": "TechStart Support",
                    "response_tone": "friendly",
                    "primary_color": "#059669"
                }
            }
        }
        
        for tenant_id, config in demo_tenants.items():
            await self.redis_client.hset(
                f"tenant:{tenant_id}", 
                mapping={
                    "config": json.dumps(config),
                    "created_at": datetime.utcnow().isoformat()
                }
            )
    
    async def validate_sso_token(self, sso_token: str) -> Dict[str, Any]:
        """Validate SSO token (simplified demo implementation)"""
        try:
            # In production, validate against actual SSO provider
            # For demo, decode a simple JWT
            payload = jwt.decode(sso_token, "demo-sso-secret", algorithms=["HS256"])
            
            return {
                "user_id": payload.get("user_id", str(uuid.uuid4())),
                "tenant_id": payload.get("tenant_id", "tenant_1"),
                "email": payload.get("email", "user@acme.com"),
                "name": payload.get("name", "Demo User"),
                "roles": payload.get("roles", ["user"])
            }
        except:
            # Fallback demo user
            return {
                "user_id": str(uuid.uuid4()),
                "tenant_id": "tenant_1",
                "email": "demo@acme.com",
                "name": "Demo User",
                "roles": ["user"]
            }
    
    async def get_tenant_info(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant configuration"""
        # Initialize demo tenants if not done yet
        if not self._demo_tenants_initialized:
            await self._init_demo_tenants()
            self._demo_tenants_initialized = True
        
        tenant_data = await self.redis_client.hget(f"tenant:{tenant_id}", "config")
        if tenant_data:
            return json.loads(tenant_data)
        
        # Return default config
        return {
            "name": "Default Tenant",
            "domain": "example.com",
            "quota_config": {
                "max_connections": settings.default_max_connections,
                "daily_messages": settings.default_daily_messages,
                "context_size": settings.default_context_size
            }
        }
    
    async def get_tenant_config(self, tenant_id: str) -> Dict[str, Any]:
        """Get tenant AI configuration"""
        tenant_info = await self.get_tenant_info(tenant_id)
        return tenant_info.get("brand_config", {})
    
    async def get_quota_info(self, tenant_id: str) -> Dict[str, Any]:
        """Get current quota usage"""
        tenant_info = await self.get_tenant_info(tenant_id)
        quota_config = tenant_info["quota_config"]
        
        # Get current usage from Redis
        current_connections = await self.redis_client.scard(f"tenant:{tenant_id}:connections")
        daily_messages_key = f"tenant:{tenant_id}:messages:{datetime.utcnow().strftime('%Y-%m-%d')}"
        daily_messages = await self.redis_client.get(daily_messages_key) or "0"
        
        return {
            "max_connections": quota_config["max_connections"],
            "current_connections": current_connections,
            "daily_message_limit": quota_config["daily_messages"],
            "daily_messages_used": int(daily_messages),
            "context_size_limit": quota_config["context_size"]
        }
    
    async def check_message_quota(self, tenant_id: str, user_id: str) -> Dict[str, Any]:
        """Check if user can send message within quota"""
        quota_info = await self.get_quota_info(tenant_id)
        
        # Check daily message limit
        if quota_info["daily_messages_used"] >= quota_info["daily_message_limit"]:
            return {"allowed": False, "reason": "daily_limit_exceeded"}
        
        # Check rate limiting (10 messages per minute per user)
        rate_limit_key = f"user:{tenant_id}:{user_id}:rate_limit"
        current_rate = await self.redis_client.get(rate_limit_key) or "0"
        
        if int(current_rate) >= 10:
            return {"allowed": False, "reason": "rate_limit_exceeded"}
        
        return {"allowed": True}
    
    async def update_usage_metrics(self, tenant_id: str, user_id: str, metric_type: str):
        """Update usage metrics"""
        if metric_type == "message_sent":
            # Update daily message count
            daily_key = f"tenant:{tenant_id}:messages:{datetime.utcnow().strftime('%Y-%m-%d')}"
            await self.redis_client.incr(daily_key)
            await self.redis_client.expire(daily_key, 86400)  # Expire after 24 hours
            
            # Update rate limit counter
            rate_limit_key = f"user:{tenant_id}:{user_id}:rate_limit"
            await self.redis_client.incr(rate_limit_key)
            await self.redis_client.expire(rate_limit_key, 60)  # Expire after 1 minute
