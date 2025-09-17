"""
Database Connection Manager
"""

import asyncio
import asyncpg
import os
import structlog

logger = structlog.get_logger()

class Database:
    pool = None
    
    @classmethod
    async def initialize(cls):
        """Initialize database connection pool"""
        try:
            cls.pool = await asyncpg.create_pool(
                os.getenv("DATABASE_URL", "postgresql://postgres:postgres@localhost:5432/chatdb"),
                min_size=1,
                max_size=10
            )
            logger.info("Database pool initialized")
        except Exception as e:
            logger.error("Database initialization error", error=str(e))
            # For demo purposes, continue without DB
            cls.pool = None
    
    @classmethod
    async def close(cls):
        """Close database connection pool"""
        if cls.pool:
            await cls.pool.close()
            logger.info("Database pool closed")
    
    @classmethod
    async def execute(cls, query: str, *args):
        """Execute database query"""
        if not cls.pool:
            return None
        
        try:
            async with cls.pool.acquire() as connection:
                return await connection.execute(query, *args)
        except Exception as e:
            logger.error("Database query error", error=str(e))
            return None
