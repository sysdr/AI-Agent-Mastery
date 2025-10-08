import asyncio
import numpy as np
from typing import Dict, List, Optional
from datetime import datetime
import logging
import redis.asyncio as redis
from scipy import stats
import json
import os

from ..models.schemas import ABTest, ABTestVariant

logger = logging.getLogger(__name__)

class ABTestingService:
    def __init__(self):
        self.redis_client = None
        self.confidence_level = float(os.getenv('A_B_TEST_CONFIDENCE', 0.95))
    
    async def initialize(self):
        self.redis_client = redis.from_url(os.getenv('REDIS_URL', 'redis://localhost:6379'))
        logger.info("A/B Testing Service initialized")
    
    async def health_check(self) -> bool:
        try:
            await self.redis_client.ping()
            return True
        except Exception:
            return False
    
    async def create_test(self, test: ABTest) -> str:
        test_id = f"test_{datetime.utcnow().timestamp()}"
        test.test_id = test_id
        await self.redis_client.setex(f"ab_test:{test_id}", 86400*30, test.json())
        return test_id
    
    async def get_user_assignment(self, user_id: str) -> Optional[str]:
        # Simple hash-based assignment for demo
        hash_val = hash(user_id) % 100
        if hash_val < 50:
            return "variant_a"
        else:
            return "variant_b"
    
    async def apply_test_variant(self, recommendations, variant):
        # Apply variant modifications to recommendations
        return recommendations
    
    async def get_test_results(self, test_id: str):
        return {"test_id": test_id, "status": "running", "results": {}}
    
    async def get_active_tests(self) -> List[str]:
        keys = await self.redis_client.keys("ab_test:*")
        return [key.decode().split(':')[1] for key in keys]
