"""
AI Service - Gemini integration for advanced security analysis
"""

import json
from typing import List, Dict, Any, Optional
import google.generativeai as genai
from app.services.security_engine import SecurityFinding

class AIService:
    """AI-powered security analysis using Gemini"""
    
    def __init__(self, api_key: str):
        if not api_key:
            raise ValueError("Gemini API key is required")
        
        genai.configure(api_key=api_key)
        self.model = genai.GenerativeModel('gemini-pro')
    
    async def explain_finding(self, finding: SecurityFinding, context: str = "") -> str:
        """Generate human-readable explanation of security finding"""
        prompt = f"""
        Explain this security vulnerability in simple terms:
        
        Rule: {finding.rule_id}
        Severity: {finding.severity.value}
        Message: {finding.message}
        Code: {finding.code_snippet}
        File: {finding.file_path}:{finding.line_number}
        
        Additional context: {context}
        
        Provide:
        1. What this vulnerability means
        2. How it could be exploited
        3. Step-by-step remediation
        4. Example of secure code
        
        Keep the explanation concise but complete.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Could not generate explanation: {str(e)}"
    
    async def analyze_code_context(self, code: str, findings: List[SecurityFinding]) -> Dict[str, Any]:
        """Analyze code context and provide recommendations"""
        findings_summary = "\n".join([
            f"- {f.severity.value.upper()}: {f.message} (Line {f.line_number})"
            for f in findings
        ])
        
        prompt = f"""
        Analyze this code for security context:
        
        Code:
        ```
        {code[:2000]}  # Limit code length
        ```
        
        Found vulnerabilities:
        {findings_summary}
        
        Provide analysis in JSON format:
        {{
            "risk_assessment": "overall risk level (low/medium/high/critical)",
            "priority_fixes": ["list of highest priority fixes"],
            "code_quality": "assessment of overall code security posture",
            "recommendations": ["specific actionable recommendations"],
            "false_positive_likelihood": "assessment if findings might be false positives"
        }}
        """
        
        try:
            response = self.model.generate_content(prompt)
            # Extract JSON from response
            text = response.text.strip()
            if text.startswith('```json'):
                text = text[7:-3]
            elif text.startswith('```'):
                text = text[3:-3]
            
            return json.loads(text)
        except Exception as e:
            return {
                "risk_assessment": "unknown",
                "priority_fixes": ["Manual review required"],
                "code_quality": "Could not assess",
                "recommendations": ["Review findings manually"],
                "error": str(e)
            }
    
    async def generate_security_report(self, analysis_results: Dict[str, Any]) -> str:
        """Generate comprehensive security report"""
        prompt = f"""
        Generate a professional security analysis report based on these results:
        
        {json.dumps(analysis_results, indent=2)}
        
        Create a report with:
        1. Executive Summary
        2. Risk Overview
        3. Critical Findings
        4. Recommendations
        5. Next Steps
        
        Format as markdown for easy reading.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"# Security Analysis Report\n\nError generating report: {str(e)}"
    
    async def suggest_secure_code(self, vulnerable_code: str, vulnerability_type: str) -> str:
        """Suggest secure alternative for vulnerable code"""
        prompt = f"""
        This code has a {vulnerability_type} vulnerability:
        
        ```
        {vulnerable_code}
        ```
        
        Provide a secure alternative with explanation of changes made.
        Show both the vulnerable and secure versions for comparison.
        """
        
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            return f"Could not generate secure code suggestion: {str(e)}"
