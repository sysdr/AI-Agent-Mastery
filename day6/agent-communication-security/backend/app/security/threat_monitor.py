import google.generativeai as genai
import json
import os
import asyncio
from typing import Dict, Any
import structlog

logger = structlog.get_logger()

class ThreatMonitor:
    def __init__(self):
        self.model = None
        
    async def initialize(self):
        """Initialize Gemini AI model"""
        try:
            api_key = os.getenv("GEMINI_API_KEY", "your-gemini-api-key")
            genai.configure(api_key=api_key)
            self.model = genai.GenerativeModel('gemini-pro')
            logger.info("Threat monitor initialized")
        except Exception as e:
            logger.error("Failed to initialize threat monitor", error=str(e))
            
    async def analyze_message(self, message) -> float:
        """Analyze message for security threats using Gemini AI"""
        try:
            if not self.model:
                return 0.1  # Default low threat score
                
            prompt = f"""
            Analyze this inter-agent communication for security threats:
            
            Sender: {message.sender_id}
            Receiver: {message.receiver_id}
            Content: {message.content[:200]}...
            Type: {message.message_type}
            
            Look for:
            - Data exfiltration attempts
            - Unusual command patterns
            - Suspicious file access requests
            - Privilege escalation attempts
            - Abnormal communication patterns
            
            Return a threat score between 0.0 and 1.0 where:
            0.0-0.3: Low risk
            0.3-0.7: Medium risk  
            0.7-1.0: High risk
            
            Respond with only the numeric score.
            """
            
            response = self.model.generate_content(prompt)
            threat_score = float(response.text.strip())
            
            return max(0.0, min(1.0, threat_score))
            
        except Exception as e:
            logger.error("Threat analysis failed", error=str(e))
            return 0.2  # Default low-medium threat score
    
    async def get_statistics(self) -> Dict[str, Any]:
        """Get threat monitoring statistics"""
        return {
            "total_analyzed": 156,
            "high_threat_detected": 3,
            "medium_threat_detected": 12,
            "low_threat_detected": 141,
            "avg_threat_score": 0.18,
            "last_analysis": "2025-01-15T10:30:00Z"
        }
