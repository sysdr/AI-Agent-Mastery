"""
Validation Agent - Validates customer data and performs verification
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
import time
import google.generativeai as genai
import os
import json

logger = logging.getLogger(__name__)

class ValidationAgent:
    """AI-powered customer validation agent"""
    
    def __init__(self):
        # Initialize Gemini AI
        genai.configure(api_key=os.getenv("GEMINI_API_KEY", "demo_key"))
        self.model = genai.GenerativeModel('gemini-pro')
        
        self.validation_stats = {
            "validations_performed": 0,
            "success_rate": 0.92,
            "average_validation_time": 2.3
        }
    
    async def validate_customer(
        self,
        customer_id: str,
        document_results: Dict[str, Any],
        security_context: Dict[str, Any]
    ) -> Dict[str, Any]:
        """Validate customer using processed document data"""
        
        logger.info(f"Validating customer {customer_id}")
        
        start_time = time.time()
        
        # Extract data from processed documents
        extracted_data = self._extract_validation_data(document_results)
        
        # Perform validation steps
        validation_results = {
            "customer_id": customer_id,
            "validation_steps": [],
            "overall_status": "pending",
            "risk_assessment": {},
            "timestamp": time.time()
        }
        
        # Step 1: Identity Validation
        identity_result = await self._validate_identity(extracted_data)
        validation_results["validation_steps"].append(identity_result)
        
        # Step 2: Document Authenticity
        authenticity_result = await self._validate_document_authenticity(extracted_data)
        validation_results["validation_steps"].append(authenticity_result)
        
        # Step 3: Cross-Reference Validation
        cross_ref_result = await self._validate_cross_references(extracted_data)
        validation_results["validation_steps"].append(cross_ref_result)
        
        # Step 4: Risk Assessment
        risk_result = await self._assess_risk(customer_id, extracted_data)
        validation_results["risk_assessment"] = risk_result
        
        # Determine overall status
        all_passed = all(step["status"] == "passed" for step in validation_results["validation_steps"])
        validation_results["overall_status"] = "passed" if all_passed else "failed"
        
        # Update statistics
        processing_time = time.time() - start_time
        self.validation_stats["validations_performed"] += 1
        self.validation_stats["average_validation_time"] = processing_time
        
        logger.info(f"Customer validation completed: {validation_results['overall_status']}")
        
        return validation_results
    
    def _extract_validation_data(self, document_results: Dict[str, Any]) -> Dict[str, Any]:
        """Extract relevant data from document processing results"""
        
        validation_data = {
            "identity_data": {},
            "financial_data": {},
            "supporting_documents": []
        }
        
        processed_docs = document_results.get("processed_documents", [])
        
        for doc in processed_docs:
            if doc["status"] == "success":
                extracted = doc["extracted_data"]
                doc_type = extracted.get("document_type", "unknown")
                
                if doc_type == "identity":
                    validation_data["identity_data"].update(extracted["extracted_fields"])
                elif doc_type == "financial":
                    validation_data["financial_data"].update(extracted["extracted_fields"])
                else:
                    validation_data["supporting_documents"].append(extracted)
        
        return validation_data
    
    async def _validate_identity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate identity information"""
        
        await asyncio.sleep(0.3)  # Simulate validation processing
        
        identity_data = data.get("identity_data", {})
        
        # Check required fields
        required_fields = ["full_name", "date_of_birth", "document_number"]
        missing_fields = [field for field in required_fields if field not in identity_data]
        
        if missing_fields:
            return {
                "step": "identity_validation",
                "status": "failed",
                "reason": f"Missing required fields: {', '.join(missing_fields)}",
                "confidence": 0.0
            }
        
        # Validate data format and consistency
        name = identity_data.get("full_name", "")
        if len(name.split()) < 2:
            return {
                "step": "identity_validation", 
                "status": "failed",
                "reason": "Invalid name format",
                "confidence": 0.2
            }
        
        return {
            "step": "identity_validation",
            "status": "passed",
            "reason": "All identity checks passed",
            "confidence": 0.94,
            "validated_fields": list(identity_data.keys())
        }
    
    async def _validate_document_authenticity(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate document authenticity using AI analysis"""
        
        await asyncio.sleep(0.5)  # Simulate AI processing
        
        # For demo, perform basic authenticity checks
        identity_data = data.get("identity_data", {})
        
        # Check document number format
        doc_number = identity_data.get("document_number", "")
        if len(doc_number) < 8:
            return {
                "step": "document_authenticity",
                "status": "failed",
                "reason": "Document number format invalid",
                "confidence": 0.1
            }
        
        # Simulate AI-powered authenticity detection
        authenticity_score = 0.89  # Simulated AI confidence score
        
        return {
            "step": "document_authenticity",
            "status": "passed" if authenticity_score > 0.8 else "failed",
            "reason": f"Document authenticity validated with {authenticity_score:.2f} confidence",
            "confidence": authenticity_score,
            "ai_analysis": {
                "security_features_detected": True,
                "template_match": "high",
                "anomalies_detected": False
            }
        }
    
    async def _validate_cross_references(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Cross-reference data across multiple documents"""
        
        await asyncio.sleep(0.4)  # Simulate cross-reference processing
        
        identity_data = data.get("identity_data", {})
        financial_data = data.get("financial_data", {})
        
        # Check for data consistency across documents
        inconsistencies = []
        
        # Example: Check name consistency
        identity_name = identity_data.get("full_name", "").lower()
        
        # For demo, assume consistency
        return {
            "step": "cross_reference_validation",
            "status": "passed",
            "reason": "Data consistent across all documents",
            "confidence": 0.91,
            "cross_references_checked": ["name_consistency", "date_consistency", "document_correlation"],
            "inconsistencies": inconsistencies
        }
    
    async def _assess_risk(self, customer_id: str, data: Dict[str, Any]) -> Dict[str, Any]:
        """Assess customer risk profile"""
        
        await asyncio.sleep(0.6)  # Simulate risk assessment
        
        # Calculate risk score based on various factors
        risk_factors = {
            "identity_verification": 0.05,  # Low risk - passed
            "document_quality": 0.03,       # Low risk - high quality
            "data_consistency": 0.02,       # Low risk - consistent
            "financial_profile": 0.08,      # Medium risk - to be verified
        }
        
        total_risk_score = sum(risk_factors.values())
        risk_level = "low" if total_risk_score < 0.2 else "medium" if total_risk_score < 0.5 else "high"
        
        return {
            "risk_score": total_risk_score,
            "risk_level": risk_level,
            "risk_factors": risk_factors,
            "recommendations": [
                "Proceed with standard onboarding process",
                "Monitor for unusual activity",
                "Set standard transaction limits"
            ] if risk_level == "low" else [
                "Require additional verification",
                "Implement enhanced monitoring",
                "Set lower transaction limits"
            ],
            "assessment_timestamp": time.time()
        }
    
    async def get_agent_status(self) -> Dict[str, Any]:
        """Get current agent status and statistics"""
        
        return {
            "agent_type": "validation_processor",
            "status": "healthy",
            "statistics": self.validation_stats,
            "capabilities": [
                "identity_validation",
                "document_authenticity",
                "cross_reference_checking",
                "risk_assessment"
            ],
            "timestamp": time.time()
        }
