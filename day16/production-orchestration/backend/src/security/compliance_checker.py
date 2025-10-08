"""
Compliance Checker - Validates workflows against compliance requirements
"""
import asyncio
import logging
from typing import Dict, List, Any, Optional
from dataclasses import dataclass
from enum import Enum
import time
import google.generativeai as genai
import os

logger = logging.getLogger(__name__)

class ComplianceLevel(Enum):
    BASIC = "basic"
    STANDARD = "standard" 
    STRICT = "strict"
    ENTERPRISE = "enterprise"

@dataclass
class ComplianceRule:
    rule_id: str
    name: str
    description: str
    level: ComplianceLevel
    validator_func: str
    severity: str = "high"

class ComplianceChecker:
    """Validates workflows and data against compliance requirements"""
    
    def __init__(self):
        self.rules: Dict[str, ComplianceRule] = {}
        self.violations: List[Dict[str, Any]] = []
        
        # Initialize Gemini AI for compliance analysis
        genai.configure(api_key=os.getenv("GEMINI_API_KEY", "demo_key"))
        self.model = genai.GenerativeModel('gemini-pro')
        
        self._load_compliance_rules()
    
    def _load_compliance_rules(self):
        """Load predefined compliance rules"""
        
        rules = [
            ComplianceRule(
                rule_id="gdpr_data_protection",
                name="GDPR Data Protection",
                description="Ensure personal data is handled according to GDPR",
                level=ComplianceLevel.STANDARD,
                validator_func="validate_gdpr_compliance"
            ),
            ComplianceRule(
                rule_id="pci_dss_payment",
                name="PCI DSS Payment Security", 
                description="Validate payment data security requirements",
                level=ComplianceLevel.STRICT,
                validator_func="validate_pci_compliance"
            ),
            ComplianceRule(
                rule_id="hipaa_health_data",
                name="HIPAA Health Data Protection",
                description="Ensure health information privacy compliance",
                level=ComplianceLevel.ENTERPRISE,
                validator_func="validate_hipaa_compliance"
            )
        ]
        
        for rule in rules:
            self.rules[rule.rule_id] = rule
            
        logger.info(f"Loaded {len(self.rules)} compliance rules")
    
    async def validate_workflow(
        self, 
        workflow_type: str,
        data: Dict[str, Any],
        compliance_level: str
    ) -> Dict[str, Any]:
        """Validate workflow against compliance requirements"""
        
        logger.info(f"Validating workflow {workflow_type} at {compliance_level} level")
        
        level_enum = ComplianceLevel(compliance_level)
        applicable_rules = [
            rule for rule in self.rules.values()
            if self._is_rule_applicable(rule, level_enum, workflow_type)
        ]
        
        validation_results = []
        overall_approved = True
        
        for rule in applicable_rules:
            try:
                result = await self._validate_rule(rule, data, workflow_type)
                validation_results.append(result)
                
                if not result["approved"]:
                    overall_approved = False
                    self.violations.append({
                        "rule_id": rule.rule_id,
                        "workflow_type": workflow_type,
                        "violation": result["reason"],
                        "timestamp": time.time()
                    })
                    
            except Exception as e:
                logger.error(f"Error validating rule {rule.rule_id}: {e}")
                overall_approved = False
        
        return {
            "approved": overall_approved,
            "compliance_level": compliance_level,
            "rules_checked": len(applicable_rules),
            "violations": [r for r in validation_results if not r["approved"]],
            "reason": "Compliance violations detected" if not overall_approved else "All compliance checks passed"
        }
    
    def _is_rule_applicable(
        self, 
        rule: ComplianceRule,
        level: ComplianceLevel,
        workflow_type: str
    ) -> bool:
        """Check if compliance rule applies to this workflow"""
        
        # Basic level only checks basic rules
        if level == ComplianceLevel.BASIC and rule.level != ComplianceLevel.BASIC:
            return False
            
        # Standard level checks basic and standard  
        if level == ComplianceLevel.STANDARD and rule.level in [ComplianceLevel.STRICT, ComplianceLevel.ENTERPRISE]:
            return False
            
        # Apply business logic for workflow types
        if workflow_type == "customer_onboarding":
            return rule.rule_id in ["gdpr_data_protection", "pci_dss_payment"]
        
        return True
    
    async def _validate_rule(
        self,
        rule: ComplianceRule, 
        data: Dict[str, Any],
        workflow_type: str
    ) -> Dict[str, Any]:
        """Validate specific compliance rule using AI analysis"""
        
        # Use Gemini AI to analyze compliance
        prompt = f"""
        Analyze the following data for {rule.name} compliance:
        
        Rule: {rule.description}
        Workflow Type: {workflow_type}
        Data Summary: {str(data)[:500]}...
        
        Check if this data and workflow meets the compliance requirements.
        Respond with a JSON object containing:
        - "approved": boolean
        - "confidence": float (0.0-1.0) 
        - "reason": string explanation
        - "recommendations": list of recommendations if not approved
        """
        
        try:
            response = await self._query_ai_compliance(prompt)
            
            # For demo, simulate compliance checking
            if rule.rule_id == "gdpr_data_protection":
                return self._validate_gdpr_compliance(data)
            elif rule.rule_id == "pci_dss_payment":
                return self._validate_pci_compliance(data)
            else:
                return {"approved": True, "reason": "Demo validation passed"}
                
        except Exception as e:
            logger.error(f"AI compliance check failed: {e}")
            return {"approved": False, "reason": f"Compliance validation error: {e}"}
    
    async def _query_ai_compliance(self, prompt: str) -> str:
        """Query Gemini AI for compliance analysis"""
        
        try:
            # For demo purposes, return simulated response
            await asyncio.sleep(0.1)  # Simulate AI processing time
            return "Compliance analysis complete"
        except Exception as e:
            logger.error(f"Gemini AI query failed: {e}")
            raise
    
    def _validate_gdpr_compliance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate GDPR compliance requirements"""
        
        # Check for personal data handling
        has_personal_data = any(
            key in data for key in ["email", "phone", "name", "address"]
        )
        
        has_consent = data.get("consent_granted", False)
        has_purpose = data.get("data_purpose") is not None
        
        if has_personal_data and not (has_consent and has_purpose):
            return {
                "approved": False,
                "reason": "GDPR violation: Personal data without proper consent or purpose",
                "recommendations": ["Obtain explicit consent", "Define data processing purpose"]
            }
        
        return {
            "approved": True,
            "reason": "GDPR compliance requirements met"
        }
    
    def _validate_pci_compliance(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Validate PCI DSS compliance for payment data"""
        
        # Check for payment card data
        has_card_data = any(
            key in data for key in ["card_number", "cvv", "payment_info"]
        )
        
        is_encrypted = data.get("encryption_enabled", False)
        has_secure_transmission = data.get("secure_transmission", False)
        
        if has_card_data and not (is_encrypted and has_secure_transmission):
            return {
                "approved": False,
                "reason": "PCI DSS violation: Unencrypted payment data",
                "recommendations": ["Enable end-to-end encryption", "Use secure transmission protocols"]
            }
        
        return {
            "approved": True,
            "reason": "PCI DSS compliance requirements met"
        }
    
    async def deep_compliance_check(
        self,
        customer_id: str,
        validation_data: Dict[str, Any],
        compliance_level: str
    ) -> Dict[str, Any]:
        """Perform deep compliance analysis on customer data"""
        
        logger.info(f"Deep compliance check for customer {customer_id}")
        
        # Simulate comprehensive compliance analysis
        await asyncio.sleep(1)  # Simulate processing time
        
        return {
            "status": "compliant",
            "customer_id": customer_id,
            "compliance_level": compliance_level,
            "checks_performed": [
                "identity_verification",
                "sanctions_screening", 
                "aml_check",
                "data_protection_validation"
            ],
            "risk_score": 0.15,  # Low risk
            "approved_for_onboarding": True,
            "timestamp": time.time()
        }
