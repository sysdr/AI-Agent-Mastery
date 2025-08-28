import time
import json
from typing import Dict, List, Any
import redis.asyncio as redis

class MonitoringTracker:
    def __init__(self, redis_client: redis.Redis):
        self.redis = redis_client
        self.session_prefix = "monitoring_session:"
        self.domain_prefix = "active_domain:"
        self.session_timeout = 3600  # 1 hour
    
    async def track_session(self, session_name: str, urls: List[str], results: List[Dict]) -> str:
        """Track a monitoring session"""
        session_id = f"{session_name}_{int(time.time())}"
        session_data = {
            "name": session_name,
            "urls": urls,
            "results": results,
            "created_at": time.time(),
            "total_urls": len(urls),
            "successful_scrapes": len([r for r in results if r.get("success")]),
            "failed_scrapes": len([r for r in results if not r.get("success")])
        }
        
        # Store session data
        await self.redis.setex(
            f"{self.session_prefix}{session_id}",
            self.session_timeout,
            json.dumps(session_data)
        )
        
        # Track active domains
        for url in urls:
            domain = self._extract_domain(url)
            await self._track_domain(domain, url)
        
        return session_id
    
    async def _track_domain(self, domain: str, url: str):
        """Track an active domain"""
        domain_key = f"{self.domain_prefix}{domain}"
        domain_data = {
            "domain": domain,
            "urls": [url],
            "last_accessed": time.time(),
            "total_requests": 1
        }
        
        # Check if domain already exists
        existing_data = await self.redis.get(domain_key)
        if existing_data:
            try:
                existing = json.loads(existing_data)
                if url not in existing["urls"]:
                    existing["urls"].append(url)
                existing["total_requests"] += 1
                existing["last_accessed"] = time.time()
                domain_data = existing
            except json.JSONDecodeError:
                pass
        
        # Store domain data
        await self.redis.setex(domain_key, self.session_timeout, json.dumps(domain_data))
    
    async def get_active_domains(self) -> List[str]:
        """Get list of active domains"""
        keys = await self.redis.keys(f"{self.domain_prefix}*")
        domains = []
        
        for key in keys:
            try:
                data = await self.redis.get(key)
                if data:
                    domain_info = json.loads(data)
                    domains.append(domain_info["domain"])
            except (json.JSONDecodeError, KeyError):
                continue
        
        return domains
    
    async def get_recent_sessions(self, limit: int = 10) -> List[Dict]:
        """Get recent monitoring sessions"""
        keys = await self.redis.keys(f"{self.session_prefix}*")
        sessions = []
        
        for key in keys:
            try:
                data = await self.redis.get(key)
                if data:
                    session_info = json.loads(data)
                    sessions.append(session_info)
            except json.JSONDecodeError:
                continue
        
        # Sort by creation time and limit results
        sessions.sort(key=lambda x: x.get("created_at", 0), reverse=True)
        return sessions[:limit]
    
    def _extract_domain(self, url: str) -> str:
        """Extract domain from URL"""
        import urllib.parse
        parsed = urllib.parse.urlparse(url)
        return parsed.netloc.lower()
