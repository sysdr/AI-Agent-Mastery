import asyncio
import time
from typing import Optional
import redis.asyncio as redis

class DistributedRateLimiter:
    def __init__(self, redis_client: redis.Redis, key_prefix: str = "rate_limit"):
        self.redis = redis_client
        self.prefix = key_prefix
    
    async def check_rate_limit(self, identifier: str, limit: int, window: int) -> tuple[bool, dict]:
        """
        Check if request is within rate limit.
        Returns (allowed, info) where info contains current count and reset time.
        """
        key = f"{self.prefix}:{identifier}"
        
        try:
            # Use sliding window counter
            now = time.time()
            pipeline = self.redis.pipeline()
            
            # Remove old entries
            pipeline.zremrangebyscore(key, 0, now - window)
            
            # Count current requests
            pipeline.zcard(key)
            
            # Add current request
            pipeline.zadd(key, {str(now): now})
            
            # Set expiry
            pipeline.expire(key, window)
            
            results = await pipeline.execute()
            current_count = results[1] + 1  # +1 for the request we just added
            
            allowed = current_count <= limit
            
            if not allowed:
                # Remove the request we just added if not allowed
                await self.redis.zrem(key, str(now))
            
            return allowed, {
                "current": current_count,
                "limit": limit,
                "reset_time": int(now + window),
                "retry_after": window if not allowed else None
            }
            
        except Exception as e:
            # Fail open - allow request if Redis is down
            return True, {"error": str(e)}
    
    async def get_rate_limit_info(self, identifier: str, window: int) -> dict:
        """Get current rate limit status without making a request"""
        key = f"{self.prefix}:{identifier}"
        now = time.time()
        
        try:
            # Clean and count
            await self.redis.zremrangebyscore(key, 0, now - window)
            current = await self.redis.zcard(key)
            
            return {
                "current": current,
                "reset_time": int(now + window)
            }
        except Exception:
            return {"current": 0, "reset_time": int(now + window)}
