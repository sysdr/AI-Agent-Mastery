import asyncio
import uuid
import json
import logging
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import aiohttp
import google.generativeai as genai
from config.settings import settings

logger = logging.getLogger(__name__)

class SecurityScanner:
    def __init__(self):
        self.scans = {}
        self.genai_client = None
        
    async def initialize(self):
        genai.configure(api_key=settings.GEMINI_API_KEY)
        self.genai_client = genai.GenerativeModel('gemini-pro')
        logger.info("Security Scanner initialized")
        
    async def health_check(self) -> bool:
        return self.genai_client is not None
        
    async def start_scan(self, target_url: str) -> str:
        scan_id = str(uuid.uuid4())
        self.scans[scan_id] = {
            "id": scan_id,
            "target_url": target_url,
            "status": "initiated",
            "started_at": datetime.utcnow(),
            "vulnerabilities": [],
            "ai_analysis": None
        }
        return scan_id
        
    async def execute_scan(self, scan_id: str, target_url: str):
        try:
            self.scans[scan_id]["status"] = "scanning"
            
            # Static Analysis - Check for common vulnerabilities
            static_results = await self._static_analysis(target_url)
            
            # Dynamic Testing - Test endpoints
            dynamic_results = await self._dynamic_testing(target_url)
            
            # AI-Powered Analysis
            ai_analysis = await self._ai_vulnerability_analysis(
                static_results + dynamic_results
            )
            
            self.scans[scan_id].update({
                "status": "completed",
                "completed_at": datetime.utcnow(),
                "vulnerabilities": static_results + dynamic_results,
                "ai_analysis": ai_analysis,
                "risk_score": self._calculate_risk_score(static_results + dynamic_results)
            })
            
        except Exception as e:
            logger.error(f"Scan {scan_id} failed: {str(e)}")
            self.scans[scan_id].update({
                "status": "failed",
                "error": str(e),
                "completed_at": datetime.utcnow()
            })
    
    async def _static_analysis(self, target_url: str) -> List[Dict]:
        """Simulate static code analysis"""
        vulnerabilities = []
        
        # Simulate common AI agent vulnerabilities
        common_issues = [
            {
                "type": "prompt_injection",
                "severity": "high",
                "description": "Potential prompt injection vulnerability in user input processing",
                "cvss_score": 7.5,
                "remediation": "Implement input sanitization and validation"
            },
            {
                "type": "data_exposure",
                "severity": "medium", 
                "description": "Sensitive data may be logged in AI model responses",
                "cvss_score": 5.3,
                "remediation": "Implement response filtering and secure logging"
            }
        ]
        
        return common_issues
    
    async def _dynamic_testing(self, target_url: str) -> List[Dict]:
        """Perform dynamic security testing"""
        vulnerabilities = []
        
        try:
            async with aiohttp.ClientSession() as session:
                # Test for SQL injection
                injection_payloads = ["' OR '1'='1", "1; DROP TABLE users;", "<script>alert('xss')</script>"]
                
                for payload in injection_payloads:
                    test_url = f"{target_url}?input={payload}"
                    try:
                        async with session.get(test_url, timeout=5) as response:
                            if response.status == 500:
                                vulnerabilities.append({
                                    "type": "injection_vulnerability",
                                    "severity": "high",
                                    "description": f"Potential injection vulnerability with payload: {payload}",
                                    "cvss_score": 8.2,
                                    "remediation": "Implement proper input validation and parameterized queries"
                                })
                    except asyncio.TimeoutError:
                        pass
                        
        except Exception as e:
            logger.error(f"Dynamic testing failed: {str(e)}")
            
        return vulnerabilities
    
    async def _ai_vulnerability_analysis(self, vulnerabilities: List[Dict]) -> Dict:
        """Use Gemini AI to analyze vulnerabilities"""
        if not vulnerabilities:
            return {"analysis": "No vulnerabilities detected", "risk_level": "low"}
            
        try:
            prompt = f"""
            Analyze these security vulnerabilities for an AI agent system:
            {json.dumps(vulnerabilities, indent=2)}
            
            Provide:
            1. Overall risk assessment
            2. Priority recommendations
            3. Business impact analysis
            4. Compliance implications
            
            Format as JSON with keys: risk_level, priority_actions, business_impact, compliance_notes
            """
            
            response = await asyncio.to_thread(
                self.genai_client.generate_content, prompt
            )
            
            return {
                "analysis": response.text,
                "generated_at": datetime.utcnow().isoformat()
            }
            
        except Exception as e:
            logger.error(f"AI analysis failed: {str(e)}")
            return {"analysis": "AI analysis unavailable", "error": str(e)}
    
    def _calculate_risk_score(self, vulnerabilities: List[Dict]) -> float:
        """Calculate overall risk score"""
        if not vulnerabilities:
            return 0.0
            
        scores = [v.get("cvss_score", 0) for v in vulnerabilities]
        return sum(scores) / len(scores)
    
    async def get_scan_results(self, scan_id: str) -> Optional[Dict]:
        return self.scans.get(scan_id)
