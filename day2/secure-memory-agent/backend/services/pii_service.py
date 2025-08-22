import re
import spacy
from typing import Dict, List, Tuple
import structlog

logger = structlog.get_logger()

class PIIService:
    def __init__(self):
        # Load spaCy model for NER
        try:
            self.nlp = spacy.load("en_core_web_sm")
        except OSError:
            logger.warning("spaCy model not found, using regex-only detection")
            self.nlp = None
        
        # PII regex patterns
        self.patterns = {
            "email": re.compile(r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b'),
            "phone": re.compile(r'\b(?:\+?1[-.\s]?)?\(?([0-9]{3})\)?[-.\s]?([0-9]{3})[-.\s]?([0-9]{4})\b'),
            "ssn": re.compile(r'\b\d{3}-?\d{2}-?\d{4}\b'),
            "credit_card": re.compile(r'\b(?:\d{4}[-\s]?){3}\d{4}\b'),
            "ip_address": re.compile(r'\b(?:[0-9]{1,3}\.){3}[0-9]{1,3}\b'),
            "url": re.compile(r'http[s]?://(?:[a-zA-Z]|[0-9]|[$-_@.&+]|[!*\\(\\),]|(?:%[0-9a-fA-F][0-9a-fA-F]))+')
        }
    
    async def detect_pii(self, text: str) -> Dict:
        """Comprehensive PII detection and classification"""
        detection_result = {
            "has_pii": False,
            "classification": {},
            "redacted_text": text,
            "confidence_score": 0.0
        }
        
        pii_found = []
        
        # Regex-based detection
        for pii_type, pattern in self.patterns.items():
            matches = pattern.findall(text)
            if matches:
                pii_found.append({
                    "type": pii_type,
                    "count": len(matches),
                    "confidence": 0.95,
                    "method": "regex"
                })
        
        # NER-based detection
        if self.nlp:
            doc = self.nlp(text)
            for ent in doc.ents:
                if ent.label_ in ["PERSON", "ORG", "GPE", "DATE", "MONEY"]:
                    pii_found.append({
                        "type": f"ner_{ent.label_.lower()}",
                        "text": ent.text,
                        "confidence": 0.8,
                        "method": "ner"
                    })
        
        # Contextual analysis (simplified)
        context_pii = self._analyze_context(text)
        pii_found.extend(context_pii)
        
        if pii_found:
            detection_result["has_pii"] = True
            detection_result["classification"] = self._classify_pii(pii_found)
            detection_result["redacted_text"] = self._redact_pii(text, pii_found)
            detection_result["confidence_score"] = self._calculate_confidence(pii_found)
        
        return detection_result
    
    def _analyze_context(self, text: str) -> List[Dict]:
        """Contextual PII detection using patterns"""
        context_patterns = [
            (r'\b(?:my|his|her)\s+(?:name|address|number)\s+is\s+(\w+)', "contextual_identifier"),
            (r'\bborn\s+(?:on|in)\s+([0-9]{1,2}[/-][0-9]{1,2}[/-][0-9]{2,4})', "birth_date"),
            (r'\blive\s+(?:at|in)\s+([0-9]+\s+\w+\s+(?:street|st|avenue|ave|road|rd))', "address")
        ]
        
        pii_found = []
        for pattern, pii_type in context_patterns:
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                pii_found.append({
                    "type": pii_type,
                    "count": len(matches),
                    "confidence": 0.7,
                    "method": "contextual"
                })
        
        return pii_found
    
    def _classify_pii(self, pii_found: List[Dict]) -> Dict:
        """Classify PII by sensitivity level"""
        classification = {
            "high_sensitivity": [],
            "medium_sensitivity": [],
            "low_sensitivity": []
        }
        
        sensitivity_map = {
            "ssn": "high_sensitivity",
            "credit_card": "high_sensitivity",
            "email": "medium_sensitivity",
            "phone": "medium_sensitivity",
            "ner_person": "medium_sensitivity",
            "contextual_identifier": "medium_sensitivity",
            "ip_address": "low_sensitivity",
            "url": "low_sensitivity"
        }
        
        for pii in pii_found:
            sensitivity = sensitivity_map.get(pii["type"], "low_sensitivity")
            classification[sensitivity].append(pii)
        
        return classification
    
    def _redact_pii(self, text: str, pii_found: List[Dict]) -> str:
        """Redact high-sensitivity PII"""
        redacted = text
        
        # Redact high-sensitivity patterns
        for pii_type, pattern in self.patterns.items():
            if pii_type in ["ssn", "credit_card"]:
                redacted = pattern.sub("[REDACTED]", redacted)
        
        return redacted
    
    def _calculate_confidence(self, pii_found: List[Dict]) -> float:
        """Calculate overall confidence score"""
        if not pii_found:
            return 0.0
        
        total_confidence = sum(pii["confidence"] for pii in pii_found)
        return min(total_confidence / len(pii_found), 1.0)
