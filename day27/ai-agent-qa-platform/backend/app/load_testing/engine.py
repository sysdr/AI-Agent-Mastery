import asyncio
import uuid
import json
import logging
from datetime import datetime
from typing import Dict, Optional
import aiohttp
import random
import time

logger = logging.getLogger(__name__)

class LoadTestEngine:
    def __init__(self):
        self.tests = {}
        
    def health_check(self) -> bool:
        return True
        
    async def start_test(self, target_url: str, users: int, duration: int) -> str:
        test_id = str(uuid.uuid4())
        self.tests[test_id] = {
            "id": test_id,
            "target_url": target_url,
            "users": users,
            "duration": duration,
            "status": "started",
            "started_at": datetime.utcnow(),
            "results": None
        }
        
        # Start load test in background
        asyncio.create_task(self._execute_load_test(test_id))
        
        return test_id
    
    async def _execute_load_test(self, test_id: str):
        try:
            test_config = self.tests[test_id]
            self.tests[test_id]["status"] = "running"
            
            # Simulate attack patterns
            attack_patterns = [
                self._credential_stuffing_attack,
                self._rate_limiting_bypass,
                self._ddos_simulation
            ]
            
            results = {
                "response_times": [],
                "error_rates": {},
                "attack_results": {},
                "performance_metrics": {}
            }
            
            # Execute multiple attack patterns
            for pattern in attack_patterns:
                pattern_results = await pattern(
                    test_config["target_url"],
                    test_config["users"],
                    test_config["duration"]
                )
                results["attack_results"][pattern.__name__] = pattern_results
            
            # Standard load test
            load_results = await self._standard_load_test(
                test_config["target_url"],
                test_config["users"],
                test_config["duration"]
            )
            results.update(load_results)
            
            self.tests[test_id].update({
                "status": "completed",
                "completed_at": datetime.utcnow(),
                "results": results
            })
            
        except Exception as e:
            logger.error(f"Load test {test_id} failed: {str(e)}")
            self.tests[test_id].update({
                "status": "failed",
                "error": str(e),
                "completed_at": datetime.utcnow()
            })
    
    async def _standard_load_test(self, target_url: str, users: int, duration: int) -> Dict:
        """Execute standard load test"""
        response_times = []
        errors = 0
        successful_requests = 0
        
        async def make_request(session):
            nonlocal errors, successful_requests
            try:
                start_time = time.time()
                async with session.get(target_url, timeout=10) as response:
                    end_time = time.time()
                    response_time = (end_time - start_time) * 1000  # ms
                    response_times.append(response_time)
                    
                    if response.status == 200:
                        successful_requests += 1
                    else:
                        errors += 1
            except Exception:
                errors += 1
        
        # Simulate concurrent users
        async with aiohttp.ClientSession() as session:
            tasks = []
            end_time = time.time() + duration
            
            while time.time() < end_time:
                for _ in range(users):
                    if time.time() >= end_time:
                        break
                    tasks.append(make_request(session))
                
                if len(tasks) >= 100:  # Batch requests
                    await asyncio.gather(*tasks, return_exceptions=True)
                    tasks = []
                    await asyncio.sleep(0.1)
            
            # Execute remaining tasks
            if tasks:
                await asyncio.gather(*tasks, return_exceptions=True)
        
        total_requests = successful_requests + errors
        avg_response_time = sum(response_times) / len(response_times) if response_times else 0
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful_requests,
            "error_rate": errors / total_requests if total_requests > 0 else 0,
            "avg_response_time_ms": avg_response_time,
            "max_response_time_ms": max(response_times) if response_times else 0,
            "min_response_time_ms": min(response_times) if response_times else 0
        }
    
    async def _credential_stuffing_attack(self, target_url: str, users: int, duration: int) -> Dict:
        """Simulate credential stuffing attack"""
        common_credentials = [
            {"username": "admin", "password": "admin"},
            {"username": "user", "password": "password"},
            {"username": "test", "password": "test123"}
        ]
        
        attempts = 0
        blocked_attempts = 0
        
        async with aiohttp.ClientSession() as session:
            end_time = time.time() + min(duration, 30)  # Limit attack duration
            
            while time.time() < end_time:
                for cred in common_credentials:
                    try:
                        async with session.post(
                            f"{target_url}/login",
                            json=cred,
                            timeout=5
                        ) as response:
                            attempts += 1
                            if response.status == 429:  # Rate limited
                                blocked_attempts += 1
                    except Exception:
                        attempts += 1
                
                await asyncio.sleep(0.1)
        
        return {
            "total_attempts": attempts,
            "blocked_attempts": blocked_attempts,
            "block_rate": blocked_attempts / attempts if attempts > 0 else 0,
            "attack_effectiveness": "low" if blocked_attempts / attempts > 0.8 else "high"
        }
    
    async def _rate_limiting_bypass(self, target_url: str, users: int, duration: int) -> Dict:
        """Test rate limiting bypass techniques"""
        bypass_attempts = 0
        successful_bypasses = 0
        
        # Simulate different IP addresses and user agents
        user_agents = [
            "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
            "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36",
            "Mozilla/5.0 (X11; Linux x86_64) AppleWebKit/537.36"
        ]
        
        async with aiohttp.ClientSession() as session:
            end_time = time.time() + min(duration, 20)
            
            while time.time() < end_time:
                headers = {
                    "User-Agent": random.choice(user_agents),
                    "X-Forwarded-For": f"{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}.{random.randint(1,255)}"
                }
                
                try:
                    async with session.get(
                        target_url,
                        headers=headers,
                        timeout=5
                    ) as response:
                        bypass_attempts += 1
                        if response.status == 200:
                            successful_bypasses += 1
                except Exception:
                    bypass_attempts += 1
                
                await asyncio.sleep(0.01)
        
        return {
            "bypass_attempts": bypass_attempts,
            "successful_bypasses": successful_bypasses,
            "bypass_rate": successful_bypasses / bypass_attempts if bypass_attempts > 0 else 0
        }
    
    async def _ddos_simulation(self, target_url: str, users: int, duration: int) -> Dict:
        """Simulate distributed denial of service attack"""
        concurrent_requests = min(users * 5, 500)  # Limit to prevent actual harm
        successful_responses = 0
        total_requests = 0
        
        async def ddos_request(session):
            nonlocal successful_responses, total_requests
            try:
                async with session.get(target_url, timeout=2) as response:
                    total_requests += 1
                    if response.status == 200:
                        successful_responses += 1
            except Exception:
                total_requests += 1
        
        async with aiohttp.ClientSession() as session:
            end_time = time.time() + min(duration, 15)  # Limit attack duration
            
            while time.time() < end_time:
                tasks = [ddos_request(session) for _ in range(concurrent_requests)]
                await asyncio.gather(*tasks, return_exceptions=True)
                await asyncio.sleep(0.1)
        
        return {
            "total_requests": total_requests,
            "successful_responses": successful_responses,
            "service_availability": successful_responses / total_requests if total_requests > 0 else 0,
            "resilience_score": min(successful_responses / total_requests * 10, 10) if total_requests > 0 else 0
        }
    
    async def get_test_results(self, test_id: str) -> Optional[Dict]:
        return self.tests.get(test_id)
