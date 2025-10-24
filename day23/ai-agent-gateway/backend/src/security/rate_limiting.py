import asyncio
import time
from typing import Dict, Optional
from collections import defaultdict
import structlog

logger = structlog.get_logger()

class RateLimiter:
    def __init__(self):
        self.limits = {
            "default": {"requests": 100, "window": 60},  # 100 requests per minute
            "premium": {"requests": 1000, "window": 60},  # 1000 requests per minute
            "auth": {"requests": 10, "window": 60},  # 10 auth requests per minute
        }
        self.buckets = defaultdict(lambda: defaultdict(list))  # IP -> endpoint -> timestamps
        
    async def check_limit(self, client_ip: str, endpoint: str) -> bool:
        """Check if request is within rate limits"""
        current_time = time.time()
        limit_type = self._get_limit_type(endpoint)
        limit_config = self.limits[limit_type]
        
        # Clean old requests outside the window
        window_start = current_time - limit_config["window"]
        self.buckets[client_ip][endpoint] = [
            timestamp for timestamp in self.buckets[client_ip][endpoint]
            if timestamp > window_start
        ]
        
        # Check current request count
        request_count = len(self.buckets[client_ip][endpoint])
        
        if request_count >= limit_config["requests"]:
            logger.warning(
                f"Rate limit exceeded for {client_ip} on {endpoint}: "
                f"{request_count}/{limit_config['requests']} requests"
            )
            return False
        
        # Add current request
        self.buckets[client_ip][endpoint].append(current_time)
        return True
    
    def _get_limit_type(self, endpoint: str) -> str:
        """Determine rate limit type based on endpoint"""
        if "/auth/" in endpoint:
            return "auth"
        elif "/premium/" in endpoint:
            return "premium"
        else:
            return "default"
    
    async def get_limit_status(self, client_ip: str, endpoint: str) -> Dict:
        """Get current rate limit status"""
        current_time = time.time()
        limit_type = self._get_limit_type(endpoint)
        limit_config = self.limits[limit_type]
        
        # Clean old requests
        window_start = current_time - limit_config["window"]
        self.buckets[client_ip][endpoint] = [
            timestamp for timestamp in self.buckets[client_ip][endpoint]
            if timestamp > window_start
        ]
        
        request_count = len(self.buckets[client_ip][endpoint])
        
        return {
            "limit": limit_config["requests"],
            "remaining": max(0, limit_config["requests"] - request_count),
            "reset_time": int(current_time + limit_config["window"]),
            "window": limit_config["window"]
        }
