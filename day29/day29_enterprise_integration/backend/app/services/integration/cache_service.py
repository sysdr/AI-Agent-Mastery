import redis.asyncio as redis
import json
import os
from typing import Any, Optional

class CacheService:
    def __init__(self):
        self.redis_client = None
        self.default_ttl = 300  # 5 minutes
    
    async def initialize(self):
        """Initialize Redis connection"""
        import asyncio
        import logging
        logger = logging.getLogger(__name__)
        
        redis_url = os.getenv("REDIS_URL", "redis://localhost:6379")
        max_retries = 5
        retry_delay = 2
        
        for attempt in range(max_retries):
            try:
                self.redis_client = await redis.from_url(redis_url, decode_responses=True)
                # Test connection
                await self.redis_client.ping()
                return
            except Exception as e:
                if attempt < max_retries - 1:
                    logger.warning(f"Redis connection failed (attempt {attempt + 1}/{max_retries}): {str(e)}. Retrying in {retry_delay} seconds...")
                    await asyncio.sleep(retry_delay)
                else:
                    logger.warning(f"Failed to connect to Redis after {max_retries} attempts: {str(e)}. Continuing without cache.")
                    self.redis_client = None
    
    async def get(self, key: str) -> Optional[Any]:
        """Get value from cache"""
        if not self.redis_client:
            return None
        
        try:
            value = await self.redis_client.get(key)
            return json.loads(value) if value else None
        except Exception:
            return None
    
    async def set(self, key: str, value: Any, ttl: int = None):
        """Set value in cache"""
        if not self.redis_client:
            return
        
        try:
            ttl = ttl or self.default_ttl
            await self.redis_client.setex(
                key,
                ttl,
                json.dumps(value)
            )
        except Exception:
            pass
    
    async def delete(self, key: str):
        """Delete key from cache"""
        if not self.redis_client:
            return
        
        try:
            await self.redis_client.delete(key)
        except Exception:
            pass
    
    async def close(self):
        """Close Redis connection"""
        if self.redis_client:
            await self.redis_client.close()

cache_service = CacheService()
