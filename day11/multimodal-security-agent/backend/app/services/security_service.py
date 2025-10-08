import google.generativeai as genai
import os
from typing import Dict, List, Any
import json
from datetime import datetime
from ..models.schemas import SecurityAnalysisResult, ThreatLevel

class SecurityService:
    def __init__(self):
        # Initialize Gemini API
        genai.configure(api_key=os.getenv('GEMINI_API_KEY', 'your-api-key'))
        self.model = genai.GenerativeModel('gemini-pro')
        self.reports_storage = {}
    
    async def classify_content_risk(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Classify content risk using Gemini AI"""
        
        prompt = f"""
        Analyze the following content data for security and moderation risks:
        
        Content Type: {content_data.get('type', 'unknown')}
        Analysis Data: {json.dumps(content_data, indent=2)}
        
        Provide a comprehensive risk assessment in JSON format with:
        - overall_risk_score (0-100)
        - threat_level (LOW, MEDIUM, HIGH, CRITICAL)
        - specific_risks (array of identified risks)
        - recommendations (array of recommended actions)
        - confidence_score (0-100)
        
        Focus on: malware detection, inappropriate content, PII exposure, 
        security vulnerabilities, compliance violations.
        """
        
        try:
            response = self.model.generate_content(prompt)
            result = self._parse_gemini_response(response.text)
            return result
        except Exception as e:
            # Fallback basic analysis
            return self._fallback_risk_analysis(content_data)
    
    def _parse_gemini_response(self, response_text: str) -> Dict[str, Any]:
        """Parse and validate Gemini response"""
        try:
            # Extract JSON from response
            start_idx = response_text.find('{')
            end_idx = response_text.rfind('}') + 1
            json_str = response_text[start_idx:end_idx]
            
            result = json.loads(json_str)
            
            # Validate required fields
            required_fields = ['overall_risk_score', 'threat_level', 'specific_risks', 'recommendations', 'confidence_score']
            for field in required_fields:
                if field not in result:
                    result[field] = self._get_default_value(field)
            
            return result
        except:
            return self._fallback_risk_analysis({})
    
    def _fallback_risk_analysis(self, content_data: Dict[str, Any]) -> Dict[str, Any]:
        """Fallback risk analysis when AI service fails"""
        return {
            "overall_risk_score": 25,
            "threat_level": "LOW",
            "specific_risks": ["Basic content validation required"],
            "recommendations": ["Manual review recommended", "Apply standard security measures"],
            "confidence_score": 60
        }
    
    def _get_default_value(self, field: str):
        defaults = {
            'overall_risk_score': 25,
            'threat_level': 'LOW',
            'specific_risks': [],
            'recommendations': [],
            'confidence_score': 50
        }
        return defaults.get(field, None)
    
    async def get_moderation_summary(self) -> Dict[str, Any]:
        """Get summary of moderation activities"""
        return {
            "total_files_processed": len(self.reports_storage),
            "high_risk_count": sum(1 for r in self.reports_storage.values() if r.get('threat_level') == 'HIGH'),
            "processing_date": datetime.utcnow().isoformat(),
            "system_status": "operational"
        }
    
    async def get_detailed_report(self, file_id: str) -> Dict[str, Any]:
        """Get detailed report for specific file"""
        return self.reports_storage.get(file_id, {"error": "Report not found"})
    
    def store_report(self, file_id: str, report_data: Dict[str, Any]):
        """Store analysis report"""
        self.reports_storage[file_id] = report_data
