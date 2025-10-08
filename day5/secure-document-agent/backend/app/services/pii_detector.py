import google.generativeai as genai
import re
from typing import Dict, List, Any
import logging
from dataclasses import dataclass
from ..core.config import settings

logger = logging.getLogger(__name__)

@dataclass
class PIIEntity:
    type: str
    value: str
    start_pos: int
    end_pos: int
    confidence: float
    context: str

class PIIResults:
    def __init__(self):
        self.detected_entities: List[PIIEntity] = []
        self.risk_level: str = "low"
        self.compliance_flags: List[str] = []
        
    def get_summary(self) -> Dict[str, Any]:
        return {
            "total_entities": len(self.detected_entities),
            "entity_types": list(set([e.type for e in self.detected_entities])),
            "risk_level": self.risk_level,
            "compliance_flags": self.compliance_flags,
            "entities": [
                {
                    "type": e.type,
                    "confidence": e.confidence,
                    "context": e.context[:50] + "..."
                } for e in self.detected_entities
            ]
        }

class PIIDetector:
    def __init__(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Regex patterns for common PII
        self.patterns = {
            "ssn": re.compile(r'\b\d{3}-\d{2}-\d{4}\b'),
            "phone": re.compile(r'\b\d{3}-\d{3}-\d{4}\b|\(\d{3}\)\s*\d{3}-\d{4}'),
            "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            "credit_card": re.compile(r'\b\d{4}[\s-]?\d{4}[\s-]?\d{4}[\s-]?\d{4}\b'),
            "ip_address": re.compile(r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b')
        }
    
    async def analyze_content(self, text: str) -> PIIResults:
        """Analyze text for PII using both regex and AI"""
        results = PIIResults()
        
        try:
            # First pass: Regex detection
            regex_entities = self._regex_detection(text)
            results.detected_entities.extend(regex_entities)
            
            # Second pass: AI-powered detection
            ai_entities = await self._ai_detection(text)
            results.detected_entities.extend(ai_entities)
            
            # Assess risk level
            results.risk_level = self._assess_risk_level(results.detected_entities)
            
            # Check compliance requirements
            results.compliance_flags = self._check_compliance(results.detected_entities)
            
            return results
            
        except Exception as e:
            logger.error(f"PII detection error: {str(e)}")
            return results
    
    def _regex_detection(self, text: str) -> List[PIIEntity]:
        """Detect PII using regex patterns"""
        entities = []
        
        for pii_type, pattern in self.patterns.items():
            matches = pattern.finditer(text)
            for match in matches:
                start_pos = max(0, match.start() - 20)
                end_pos = min(len(text), match.end() + 20)
                context = text[start_pos:end_pos]
                
                entity = PIIEntity(
                    type=pii_type,
                    value=match.group(),
                    start_pos=match.start(),
                    end_pos=match.end(),
                    confidence=0.9,  # High confidence for regex matches
                    context=context
                )
                entities.append(entity)
        
        return entities
    
    async def _ai_detection(self, text: str) -> List[PIIEntity]:
        """Detect PII using Gemini AI for context-aware detection"""
        try:
            # Process text in chunks to avoid token limits
            chunk_size = 2000
            entities = []
            
            for i in range(0, len(text), chunk_size):
                chunk = text[i:i + chunk_size]
                chunk_entities = await self._analyze_chunk(chunk, i)
                entities.extend(chunk_entities)
            
            return entities
            
        except Exception as e:
            logger.error(f"AI PII detection error: {str(e)}")
            return []
    
    async def _analyze_chunk(self, chunk: str, offset: int) -> List[PIIEntity]:
        """Analyze a text chunk for PII"""
        try:
            prompt = f"""
            Analyze this text for personally identifiable information (PII). 
            Look for names, addresses, dates of birth, government IDs, financial information, etc.
            
            For each PII found, provide:
            - Type of PII (name, address, dob, etc.)
            - The actual text
            - Start and end positions in the text
            - Confidence level (0.0-1.0)
            - Brief context
            
            Text to analyze:
            {chunk}
            
            Respond in JSON format:
            {{
                "entities": [
                    {{
                        "type": "name",
                        "value": "John Doe",
                        "start": 15,
                        "end": 23,
                        "confidence": 0.95,
                        "context": "surrounding text"
                    }}
                ]
            }}
            """
            
            response = self.model.generate_content(prompt)
            
            import json
            try:
                result = json.loads(response.text)
                entities = []
                
                for entity_data in result.get("entities", []):
                    entity = PIIEntity(
                        type=entity_data.get("type", "unknown"),
                        value=entity_data.get("value", ""),
                        start_pos=entity_data.get("start", 0) + offset,
                        end_pos=entity_data.get("end", 0) + offset,
                        confidence=entity_data.get("confidence", 0.5),
                        context=entity_data.get("context", "")
                    )
                    entities.append(entity)
                
                return entities
                
            except json.JSONDecodeError:
                logger.warning("Failed to parse AI PII detection response")
                return []
                
        except Exception as e:
            logger.error(f"Chunk analysis error: {str(e)}")
            return []
    
    def _assess_risk_level(self, entities: List[PIIEntity]) -> str:
        """Assess overall risk level based on detected PII"""
        if not entities:
            return "low"
        
        high_risk_types = {"ssn", "credit_card", "bank_account", "passport"}
        medium_risk_types = {"phone", "email", "address", "dob"}
        
        high_risk_count = sum(1 for e in entities if e.type in high_risk_types)
        medium_risk_count = sum(1 for e in entities if e.type in medium_risk_types)
        
        if high_risk_count > 0:
            return "high"
        elif medium_risk_count > 3:
            return "high"
        elif medium_risk_count > 0:
            return "medium"
        else:
            return "low"
    
    def _check_compliance(self, entities: List[PIIEntity]) -> List[str]:
        """Check compliance requirements based on detected PII"""
        flags = []
        
        entity_types = set(e.type for e in entities)
        
        if any(t in entity_types for t in ["ssn", "credit_card", "bank_account"]):
            flags.append("GDPR")
            flags.append("CCPA")
            flags.append("PCI_DSS")
        
        if any(t in entity_types for t in ["medical_id", "diagnosis", "prescription"]):
            flags.append("HIPAA")
        
        if "email" in entity_types or "phone" in entity_types:
            flags.append("GDPR")
            flags.append("CCPA")
        
        return flags
