import re
import os
from typing import Dict, Any, List
from ..models.schemas import SecurityAnalysisResult, ThreatLevel
from .security_service import SecurityService

class DocumentSecurityService:
    def __init__(self):
        self.security_service = SecurityService()
        self.pii_patterns = self._load_pii_patterns()
    
    def _load_pii_patterns(self) -> Dict[str, str]:
        """Load PII detection patterns"""
        return {
            "ssn": r'\b\d{3}-\d{2}-\d{4}\b',
            "credit_card": r'\b\d{4}[-\s]?\d{4}[-\s]?\d{4}[-\s]?\d{4}\b',
            "email": r'\b[A-Za-z0-9._%+-]+@[A-Za-z0-9.-]+\.[A-Z|a-z]{2,}\b',
            "phone": r'\b\d{3}[-.]?\d{3}[-.]?\d{4}\b',
            "ip_address": r'\b\d{1,3}\.\d{1,3}\.\d{1,3}\.\d{1,3}\b',
            "bank_account": r'\b\d{8,17}\b',
            "passport": r'\b[A-Z]{1,2}\d{6,9}\b'
        }
    
    async def analyze_document(self, file_path: str, filename: str) -> SecurityAnalysisResult:
        """Complete document security analysis"""
        analysis_data = {
            "type": "document",
            "filename": filename,
            "file_path": file_path
        }
        
        # File validation
        file_info = self._validate_document_file(file_path)
        analysis_data.update(file_info)
        
        # Extract text content
        text_content = self._extract_text(file_path)
        analysis_data["text_content"] = text_content[:1000]  # Store sample
        
        # PII detection
        pii_analysis = self._detect_pii(text_content)
        analysis_data["pii_analysis"] = pii_analysis
        
        # Content classification
        content_analysis = self._classify_document_content(text_content)
        analysis_data["content_classification"] = content_analysis
        
        # Metadata analysis
        metadata_analysis = self._analyze_metadata(file_path)
        analysis_data["metadata_analysis"] = metadata_analysis
        
        # Get AI risk classification
        risk_assessment = await self.security_service.classify_content_risk(analysis_data)
        
        result = SecurityAnalysisResult(
            content_type="document",
            filename=filename,
            risk_score=risk_assessment["overall_risk_score"],
            threat_level=ThreatLevel(risk_assessment["threat_level"]),
            issues_found=risk_assessment["specific_risks"],
            recommendations=risk_assessment["recommendations"],
            confidence_score=risk_assessment["confidence_score"],
            metadata={
                "file_size": file_info["file_size"],
                "format": file_info["format"],
                "pii_found": pii_analysis["pii_types_found"],
                "content_category": content_analysis["category"],
                "sensitive_data_score": pii_analysis["sensitivity_score"]
            }
        )
        
        return result
    
    def _validate_document_file(self, file_path: str) -> Dict[str, Any]:
        """Basic document file validation"""
        try:
            file_stats = os.stat(file_path)
            file_size = file_stats.st_size
            file_type = "text/plain"  # Simplified for demo
            
            return {
                "file_size": file_size,
                "mime_type": file_type,
                "format": file_type.split('/')[1] if '/' in file_type else "unknown",
                "is_valid": True
            }
        except Exception as e:
            return {
                "file_size": 0,
                "is_valid": False,
                "error": str(e)
            }
    
    def _extract_text(self, file_path: str) -> str:
        """Extract text from document (simplified)"""
        try:
            # Simplified text extraction for demo
            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                return f.read()
        except Exception as e:
            return f"[Text extraction failed: {str(e)}]"
    
    def _detect_pii(self, text: str) -> Dict[str, Any]:
        """Detect personally identifiable information"""
        pii_found = {}
        pii_types_found = []
        sensitivity_score = 0
        
        for pii_type, pattern in self.pii_patterns.items():
            matches = re.findall(pattern, text, re.IGNORECASE)
            if matches:
                pii_found[pii_type] = {
                    "count": len(matches),
                    "samples": matches[:3]  # Store first 3 matches
                }
                pii_types_found.append(pii_type)
                
                # Assign sensitivity scores
                scores = {
                    "ssn": 95, "credit_card": 90, "bank_account": 90,
                    "passport": 85, "email": 30, "phone": 40, "ip_address": 20
                }
                sensitivity_score = max(sensitivity_score, scores.get(pii_type, 50))
        
        return {
            "pii_found": pii_found,
            "pii_types_found": pii_types_found,
            "sensitivity_score": sensitivity_score,
            "total_pii_instances": sum(item["count"] for item in pii_found.values())
        }
    
    def _classify_document_content(self, text: str) -> Dict[str, Any]:
        """Classify document content type and sensitivity"""
        text_lower = text.lower()
        
        # Content classification keywords
        classifications = {
            "financial": ["bank", "account", "loan", "credit", "payment", "invoice"],
            "medical": ["patient", "diagnosis", "treatment", "medical", "health", "doctor"],
            "legal": ["contract", "agreement", "legal", "court", "lawsuit", "attorney"],
            "personal": ["personal", "private", "confidential", "family", "relationship"],
            "business": ["company", "business", "corporate", "revenue", "strategy", "confidential"]
        }
        
        scores = {}
        for category, keywords in classifications.items():
            score = sum(1 for keyword in keywords if keyword in text_lower)
            scores[category] = score
        
        # Find dominant category
        dominant_category = max(scores, key=scores.get) if scores else "general"
        max_score = scores.get(dominant_category, 0)
        
        return {
            "category": dominant_category,
            "confidence": min(max_score * 10, 100),
            "all_scores": scores
        }
    
    def _analyze_metadata(self, file_path: str) -> Dict[str, Any]:
        """Analyze document metadata"""
        try:
            file_stats = os.stat(file_path)
            return {
                "creation_time": file_stats.st_ctime,
                "modification_time": file_stats.st_mtime,
                "file_size": file_stats.st_size,
                "permissions": oct(file_stats.st_mode)[-3:]
            }
        except Exception as e:
            return {"error": str(e)}
