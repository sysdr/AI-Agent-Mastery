import re
import time
import asyncio
from typing import Dict, List, Set
from fastapi import Request
import structlog

logger = structlog.get_logger()

class ThreatDetector:
    def __init__(self):
        self.sql_injection_patterns = [
            r"(\s|\+|%20)(union|select|insert|update|delete|drop|create|alter)(\s|\+|%20)",
            r"(\s|\+|%20)(or|and)(\s|\+|%20)\d+(\s|\+|%20)(=|like)(\s|\+|%20)\d+",
            r"\'(\s|\+|%20)(or|and|union)(\s|\+|%20)\'",
        ]
        self.xss_patterns = [
            r"<script[^>]*>.*?</script>",
            r"javascript:",
            r"on\w+\s*=",
            r"<iframe[^>]*>",
        ]
        self.malicious_user_agents = {
            "sqlmap", "nikto", "burpsuite", "nmap", "masscan"
        }
        self.suspicious_headers = {
            "x-forwarded-for", "x-real-ip", "x-originating-ip"
        }
        self.request_history = {}  # IP -> list of request times
        
    async def analyze_request(self, request: Request) -> float:
        """Analyze request and return threat score (0-1)"""
        threat_score = 0.0
        client_ip = request.client.host
        
        # Analyze request components
        threat_score += await self._check_sql_injection(request)
        threat_score += await self._check_xss_attacks(request)
        threat_score += await self._check_user_agent(request)
        threat_score += await self._check_rate_abuse(request)
        threat_score += await self._check_header_anomalies(request)
        
        # Log high threat scores
        if threat_score > 0.5:
            logger.warning(f"High threat score {threat_score:.2f} from {client_ip}")
        
        return min(threat_score, 1.0)
    
    async def _check_sql_injection(self, request: Request) -> float:
        """Check for SQL injection patterns"""
        score = 0.0
        
        # Check URL parameters
        for key, value in request.query_params.items():
            for pattern in self.sql_injection_patterns:
                if re.search(pattern, str(value), re.IGNORECASE):
                    score += 0.3
                    logger.warning(f"SQL injection attempt in param {key}: {value}")
        
        # Check request body if present
        try:
            if request.method in ["POST", "PUT", "PATCH"]:
                # Note: In real implementation, you'd cache the body
                # This is simplified for the example
                pass
        except Exception:
            pass
            
        return min(score, 0.5)
    
    async def _check_xss_attacks(self, request: Request) -> float:
        """Check for XSS attack patterns"""
        score = 0.0
        
        for key, value in request.query_params.items():
            for pattern in self.xss_patterns:
                if re.search(pattern, str(value), re.IGNORECASE):
                    score += 0.2
                    logger.warning(f"XSS attempt in param {key}: {value}")
        
        return min(score, 0.3)
    
    async def _check_user_agent(self, request: Request) -> float:
        """Check for malicious user agents"""
        user_agent = request.headers.get("user-agent", "").lower()
        
        for malicious_ua in self.malicious_user_agents:
            if malicious_ua in user_agent:
                logger.warning(f"Malicious user agent detected: {user_agent}")
                return 0.4
                
        return 0.0
    
    async def _check_rate_abuse(self, request: Request) -> float:
        """Check for rate abuse patterns"""
        client_ip = request.client.host
        current_time = time.time()
        
        # Initialize request history for new IPs
        if client_ip not in self.request_history:
            self.request_history[client_ip] = []
        
        # Clean old requests (older than 1 minute)
        self.request_history[client_ip] = [
            req_time for req_time in self.request_history[client_ip]
            if current_time - req_time < 60
        ]
        
        # Add current request
        self.request_history[client_ip].append(current_time)
        
        # Check request rate
        request_count = len(self.request_history[client_ip])
        
        if request_count > 100:  # More than 100 requests per minute
            logger.warning(f"Rate abuse detected from {client_ip}: {request_count} requests/minute")
            return 0.3
        elif request_count > 50:
            return 0.1
            
        return 0.0
    
    async def _check_header_anomalies(self, request: Request) -> float:
        """Check for suspicious headers"""
        score = 0.0
        
        # Check for header injection attempts
        for name, value in request.headers.items():
            if '\n' in value or '\r' in value:
                score += 0.3
                logger.warning(f"Header injection attempt in {name}: {value}")
        
        # Check for suspicious proxy headers
        suspicious_count = 0
        for header in self.suspicious_headers:
            if header in request.headers:
                suspicious_count += 1
        
        if suspicious_count > 2:
            score += 0.1
            
        return min(score, 0.2)
