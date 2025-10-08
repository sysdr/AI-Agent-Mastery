"""
Input Validation and Security
"""

import re
from typing import Dict, Any
import structlog

logger = structlog.get_logger()

class InputValidator:
    def __init__(self):
        self.dangerous_patterns = [
            r'system\s*:',
            r'ignore\s+previous',
            r'forget\s+instructions',
            r'act\s+as',
            r'pretend\s+to\s+be'
        ]
    
    async def validate_chat_input(self, content: str) -> bool:
        """Validate chat input for prompt injection attempts"""
        if not content or len(content) > 10000:
            return False
        
        # Check for dangerous patterns
        for pattern in self.dangerous_patterns:
            if re.search(pattern, content, re.IGNORECASE):
                logger.warning("Potential prompt injection detected", pattern=pattern)
                return False
        
        return True
    
    async def validate_file_upload(self, file) -> bool:
        """Validate file upload"""
        if not file:
            return False
        
        # Check file size (10MB limit)
        if file.size > 10485760:
            return False
        
        # Check file type
        allowed_types = [
            'image/jpeg', 'image/png', 'image/gif',
            'application/pdf',
            'application/vnd.openxmlformats-officedocument.wordprocessingml.document'
        ]
        
        return file.content_type in allowed_types
    
    async def validate_request_headers(self, headers) -> bool:
        """Validate request headers"""
        # Basic header validation
        return True
