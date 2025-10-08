import re
import asyncio
from typing import Dict, List, Any
from datetime import datetime
import logging
from textblob import TextBlob
from better_profanity import profanity

logger = logging.getLogger(__name__)

class ComplianceValidator:
    def __init__(self):
        self.policy_rules = self._load_policy_rules()
        self.threat_patterns = self._load_threat_patterns()
        
    async def validate_message(self, message: str) -> Dict[str, Any]:
        """Validate message against compliance policies"""
        
        validation_results = {
            "is_valid": True,
            "score": 1.0,
            "flags": [],
            "violations": [],
            "timestamp": datetime.now().isoformat()
        }
        
        try:
            # Content moderation checks
            content_check = await self._check_content_policy(message)
            validation_results["score"] *= content_check["score"]
            validation_results["flags"].extend(content_check["flags"])
            
            # Injection attempt detection
            injection_check = await self._check_injection_attempts(message)
            validation_results["score"] *= injection_check["score"]
            validation_results["flags"].extend(injection_check["flags"])
            
            # Profanity detection
            profanity_check = await self._check_profanity(message)
            validation_results["score"] *= profanity_check["score"]
            validation_results["flags"].extend(profanity_check["flags"])
            
            # Policy rule validation
            policy_check = await self._check_policy_rules(message)
            validation_results["score"] *= policy_check["score"]
            validation_results["violations"].extend(policy_check["violations"])
            
            # Overall validation
            validation_results["is_valid"] = validation_results["score"] >= 0.6
            
            return validation_results
            
        except Exception as e:
            logger.error(f"Validation error: {str(e)}")
            return {
                "is_valid": False,
                "score": 0.0,
                "flags": ["validation_error"],
                "violations": [],
                "timestamp": datetime.now().isoformat()
            }
    
    async def _check_content_policy(self, message: str) -> Dict[str, Any]:
        """Check against content policy"""
        flags = []
        score = 1.0
        
        # Sentiment analysis
        blob = TextBlob(message)
        sentiment = blob.sentiment.polarity
        
        if sentiment < -0.5:
            flags.append("negative_sentiment")
            score *= 0.8
        
        # Inappropriate content patterns
        inappropriate_patterns = [
            r'\b(hack|exploit|vulnerability|breach)\b',
            r'\b(password|credential|token|key)\b.*\b(share|give|provide)\b',
            r'\b(personal|private|confidential).*\b(information|data)\b'
        ]
        
        for pattern in inappropriate_patterns:
            if re.search(pattern, message, re.IGNORECASE):
                flags.append("inappropriate_request")
                score *= 0.6
        
        return {"score": score, "flags": flags}
    
    async def _check_injection_attempts(self, message: str) -> Dict[str, Any]:
        """Detect prompt injection attempts"""
        flags = []
        score = 1.0
        
        for pattern_name, pattern in self.threat_patterns.items():
            if re.search(pattern, message, re.IGNORECASE):
                flags.append(f"injection_attempt_{pattern_name}")
                score *= 0.3  # Heavy penalty for injection attempts
        
        return {"score": score, "flags": flags}
    
    async def _check_profanity(self, message: str) -> Dict[str, Any]:
        """Check for profanity"""
        flags = []
        score = 1.0
        
        try:
            is_profane = profanity.contains_profanity(message)
            
            if is_profane:
                # Check for mild profanity (common words that might be flagged)
                mild_profanity = ['damn', 'hell', 'crap']
                is_mild = any(word in message.lower() for word in mild_profanity)
                
                if is_mild:
                    flags.append("mild_profanity_detected")
                    score *= 0.8  # Light penalty for mild profanity
                else:
                    flags.append("profanity_detected")
                    score *= 0.3  # Heavy penalty for strong profanity
        except Exception as e:
            logger.warning(f"Profanity check failed: {str(e)}")
        
        return {"score": score, "flags": flags}
    
    async def _check_policy_rules(self, message: str) -> Dict[str, Any]:
        """Check against organizational policies"""
        violations = []
        score = 1.0
        
        for rule_name, rule in self.policy_rules.items():
            if rule["pattern"] and re.search(rule["pattern"], message, re.IGNORECASE):
                violations.append({
                    "rule": rule_name,
                    "severity": rule["severity"],
                    "description": rule["description"]
                })
                score *= rule["penalty"]
        
        return {"score": score, "violations": violations}
    
    def _load_policy_rules(self) -> Dict[str, Dict]:
        """Load organizational policy rules"""
        return {
            "no_personal_info_request": {
                "pattern": r'\b(ssn|social security|credit card|bank account|driver license)\b',
                "severity": "high",
                "penalty": 0.2,
                "description": "Request for personal information"
            },
            "no_system_access": {
                "pattern": r'\b(admin|root|sudo|system|database|server)\b.*\b(access|login|password)\b',
                "severity": "critical", 
                "penalty": 0.1,
                "description": "System access request"
            },
            "no_financial_advice": {
                "pattern": r'\b(invest|stock|trading|financial advice|buy|sell)\b',
                "severity": "medium",
                "penalty": 0.7,
                "description": "Financial advice request"
            }
        }
    
    def _load_threat_patterns(self) -> Dict[str, str]:
        """Load threat detection patterns"""
        return {
            "instruction_override": r'\b(ignore|forget|disregard).*\b(previous|above|instructions|rules)\b',
            "role_manipulation": r'\b(you are now|pretend to be|act as|roleplay)\b',
            "prompt_escape": r'(\]\]|\}\}|"""|```)',
            "command_injection": r'\b(system|exec|eval|import|subprocess)\b',
            "context_manipulation": r'\b(context|memory|remember|conversation)\b.*\b(change|modify|update)\b'
        }
