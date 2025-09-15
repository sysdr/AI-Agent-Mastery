import re
import hashlib
from typing import Dict, Any, List
import structlog
from datetime import datetime

logger = structlog.get_logger()

class SecurityValidator:
    def __init__(self):
        self.threat_patterns = []
        self.security_incidents = []
        
    async def initialize(self):
        """Initialize security patterns and rules"""
        self.threat_patterns = [
            r'<script[^>]*>.*?</script>',
            r'javascript:',
            r'on\w+\s*=',
            r'eval\s*\(',
            r'document\.cookie',
            r'location\.href'
        ]
        logger.info("Security validator initialized")
    
    async def validate_request(self, request) -> bool:
        """Validate incoming request for security threats"""
        query = request.query
        
        # Check for malicious patterns
        for pattern in self.threat_patterns:
            if re.search(pattern, query, re.IGNORECASE):
                incident = {
                    "type": "malicious_input",
                    "request_id": request.request_id,
                    "pattern": pattern,
                    "timestamp": datetime.now().isoformat(),
                    "severity": "high"
                }
                self.security_incidents.append(incident)
                logger.warning("Security threat detected", incident=incident)
                raise ValueError("Malicious input detected")
        
        # Validate query length
        if len(query) > 10000:
            raise ValueError("Query too long - potential DoS attack")
        
        # Check for suspicious keywords
        suspicious_keywords = ['password', 'secret', 'token', 'key', 'admin']
        for keyword in suspicious_keywords:
            if keyword in query.lower():
                logger.info("Suspicious keyword detected", keyword=keyword)
        
        return True
    
    async def validate_results(self, results: Dict) -> Dict:
        """Validate tool results for security issues"""
        validated_results = {}
        
        for tool_name, result in results.items():
            if self.is_result_safe(result):
                validated_results[tool_name] = result
            else:
                logger.warning("Unsafe result filtered", tool=tool_name)
                validated_results[tool_name] = {
                    "filtered": True,
                    "reason": "Security validation failed"
                }
        
        return validated_results
    
    def is_result_safe(self, result: Dict) -> bool:
        """Check if result is safe to return"""
        result_str = str(result)
        
        # Check for malicious patterns in results
        for pattern in self.threat_patterns:
            if re.search(pattern, result_str, re.IGNORECASE):
                return False
        
        # Check for sensitive information
        sensitive_patterns = [
            r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',  # Credit card
            r'\b\d{3}-\d{2}-\d{4}\b',  # SSN
            r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'  # Email
        ]
        
        for pattern in sensitive_patterns:
            if re.search(pattern, result_str):
                logger.warning("Sensitive information detected in result")
                return False
        
        return True
    
    async def get_security_incidents(self) -> List[Dict]:
        """Get list of security incidents"""
        return self.security_incidents
    
    def generate_security_hash(self, data: str) -> str:
        """Generate security hash for data integrity"""
        return hashlib.sha256(data.encode()).hexdigest()
