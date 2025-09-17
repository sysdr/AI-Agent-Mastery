"""
Redis Client for Caching and Session Management
"""

import json
import redis.asyncio as redis
import os
import structlog

logger = structlog.get_logger()

class RedisClient:
    client = None
    
    @classmethod
    async def initialize(cls):
        """Initialize Redis connection"""
        try:
            cls.client = redis.from_url(
                os.getenv("REDIS_URL", "redis://localhost:6379"),
                decode_responses=True
            )
            await cls.client.ping()
            logger.info("Redis client initialized")
        except Exception as e:
            logger.error("Redis initialization error", error=str(e))
            # For demo purposes, continue without Redis
            cls.client = None
    
    @classmethod
    async def close(cls):
        """Close Redis connection"""
        if cls.client:
            await cls.client.close()
            logger.info("Redis client closed")
    
    @classmethod
    async def get(cls, key: str):
        """Get value from Redis"""
        if not cls.client:
            return None
        
        try:
            value = await cls.client.get(key)
            return json.loads(value) if value else None
        except Exception as e:
            logger.error("Redis get error", error=str(e))
            return None
    
    @classmethod
    async def set(cls, key: str, value, expire: int = None):
        """Set value in Redis"""
        if not cls.client:
            return
        
        try:
            await cls.client.set(key, json.dumps(value), ex=expire)
        except Exception as e:
            logger.error("Redis set error", error=str(e))
