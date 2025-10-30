from typing import Dict, List, Any
from sqlalchemy.orm import Session
from ..models.models import ComplianceRule, AuditLog
from datetime import datetime, timedelta
import json
from enum import Enum

class ComplianceType(str, Enum):
    GDPR = "GDPR"
    HIPAA = "HIPAA" 
    SOX = "SOX"
    PCI_DSS = "PCI_DSS"

class ComplianceService:
    def __init__(self):
        self.rules_cache = {}
        
    def create_rule(
        self,
        db: Session,
        name: str,
        description: str,
        rule_type: ComplianceType,
        conditions: Dict[str, Any],
        actions: Dict[str, Any]
    ) -> ComplianceRule:
        rule = ComplianceRule(
            name=name,
            description=description,
            rule_type=rule_type,
            conditions=conditions,
            actions=actions
        )
        db.add(rule)
        db.commit()
        db.refresh(rule)
        return rule
    
    def check_compliance(self, db: Session, audit_log: AuditLog) -> List[str]:
        violations = []
        active_rules = db.query(ComplianceRule).filter(ComplianceRule.is_active == True).all()
        
        for rule in active_rules:
            if self._evaluate_rule(audit_log, rule):
                violations.append(f"Compliance violation: {rule.name} ({rule.rule_type})")
                
        return violations
    
    def _evaluate_rule(self, audit_log: AuditLog, rule: ComplianceRule) -> bool:
        """Evaluate if audit log violates compliance rule"""
        conditions = rule.conditions
        
        # GDPR: Data access without consent
        if rule.rule_type == ComplianceType.GDPR:
            if conditions.get("requires_consent") and not audit_log.details.get("consent_given"):
                return True
                
        # HIPAA: PHI access logging
        elif rule.rule_type == ComplianceType.HIPAA:
            if "patient" in audit_log.resource and not audit_log.details.get("authorized"):
                return True
                
        # SOX: Financial data access
        elif rule.rule_type == ComplianceType.SOX:
            if "financial" in audit_log.resource and audit_log.details.get("unauthorized_access"):
                return True
                
        return False
    
    def generate_compliance_report(self, db: Session, compliance_type: ComplianceType = None, days: int = 30) -> Dict[str, Any]:
        start_date = datetime.utcnow() - timedelta(days=days)
        
        query = db.query(AuditLog).filter(AuditLog.timestamp >= start_date)
        audit_logs = query.all()
        
        report = {
            "period": f"Last {days} days",
            "total_events": len(audit_logs),
            "compliance_checks": {},
            "violations": [],
            "user_activity": {},
            "resource_access": {}
        }
        
        # Analyze compliance by type
        for log in audit_logs:
            violations = self.check_compliance(db, log)
            if violations:
                report["violations"].extend(violations)
                
            # Track user activity
            user_id = str(log.user_id)
            if user_id not in report["user_activity"]:
                report["user_activity"][user_id] = 0
            report["user_activity"][user_id] += 1
            
            # Track resource access
            if log.resource not in report["resource_access"]:
                report["resource_access"][log.resource] = 0
            report["resource_access"][log.resource] += 1
        
        report["violation_count"] = len(report["violations"])
        report["compliance_score"] = max(0, 100 - (len(report["violations"]) / len(audit_logs) * 100)) if audit_logs else 100
        
        return report
    
    def setup_default_rules(self, db: Session):
        """Setup default compliance rules"""
        default_rules = [
            {
                "name": "GDPR Data Consent",
                "description": "Ensure data access has user consent",
                "rule_type": ComplianceType.GDPR,
                "conditions": {"requires_consent": True, "data_types": ["personal", "sensitive"]},
                "actions": {"alert": True, "block": False}
            },
            {
                "name": "HIPAA PHI Access",
                "description": "Monitor patient health information access",
                "rule_type": ComplianceType.HIPAA,
                "conditions": {"resource_type": "patient_data", "requires_authorization": True},
                "actions": {"alert": True, "log_detailed": True}
            },
            {
                "name": "SOX Financial Controls",
                "description": "Audit financial data access",
                "rule_type": ComplianceType.SOX,
                "conditions": {"resource_contains": "financial", "requires_approval": True},
                "actions": {"alert": True, "require_justification": True}
            }
        ]
        
        for rule_data in default_rules:
            existing = db.query(ComplianceRule).filter(ComplianceRule.name == rule_data["name"]).first()
            if not existing:
                self.create_rule(db, **rule_data)

compliance_service = ComplianceService()
