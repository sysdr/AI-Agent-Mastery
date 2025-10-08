import asyncio
import random
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import structlog

logger = structlog.get_logger()

class IncidentManager:
    def __init__(self):
        self.incidents = []
        self.security_status = {
            "threat_level": "low",
            "active_incidents": 0,
            "blocked_ips": [],
            "last_attack": None
        }
        
    async def create_incident(self, incident_type: str, severity: str, details: Dict) -> Dict:
        """Create new security incident"""
        incident = {
            "id": f"INC-{random.randint(1000, 9999)}",
            "type": incident_type,
            "severity": severity,
            "status": "active",
            "created_at": datetime.utcnow().isoformat(),
            "details": details,
            "response_actions": [],
            "resolved_at": None
        }
        
        self.incidents.append(incident)
        self._update_security_status()
        
        logger.warning(f"🚨 New security incident: {incident['id']} - {incident_type}")
        
        # Auto-resolve low severity incidents after 5 minutes
        if severity == "low":
            asyncio.create_task(self._auto_resolve_incident(incident["id"], 300))
        
        return incident
    
    async def simulate_attack(self, attack_type: str) -> Dict:
        """Simulate various types of attacks for testing"""
        attack_scenarios = {
            "ddos": {
                "severity": "high",
                "details": {
                    "source_ips": [f"192.168.1.{random.randint(1, 254)}" for _ in range(5)],
                    "request_rate": random.randint(1000, 5000),
                    "target_endpoint": "/api/v1/agents"
                }
            },
            "brute_force": {
                "severity": "medium", 
                "details": {
                    "source_ip": f"192.168.1.{random.randint(1, 254)}",
                    "failed_attempts": random.randint(50, 200),
                    "target_account": "admin"
                }
            },
            "malware": {
                "severity": "high",
                "details": {
                    "file_hash": "abc123def456",
                    "detection_method": "behavioral_analysis",
                    "affected_systems": ["agent-1", "agent-2"]
                }
            },
            "data_breach": {
                "severity": "critical",
                "details": {
                    "data_accessed": "user_credentials",
                    "records_affected": random.randint(100, 1000),
                    "access_method": "sql_injection"
                }
            }
        }
        
        scenario = attack_scenarios.get(attack_type, attack_scenarios["ddos"])
        incident = await self.create_incident(attack_type, scenario["severity"], scenario["details"])
        
        # Simulate automatic response
        await self._initiate_incident_response(incident)
        
        return {
            "status": "attack_simulated",
            "incident_id": incident["id"],
            "type": attack_type,
            "severity": scenario["severity"]
        }
    
    async def _initiate_incident_response(self, incident: Dict):
        """Initiate automated incident response"""
        response_actions = []
        
        # Determine response based on incident type
        if incident["type"] == "ddos":
            response_actions = [
                "activated_ddos_protection",
                "rate_limited_requests",
                "blocked_source_ips",
                "scaled_infrastructure"
            ]
        elif incident["type"] == "brute_force":
            response_actions = [
                "blocked_source_ip",
                "increased_auth_monitoring",
                "alerted_security_team"
            ]
        elif incident["type"] == "malware":
            response_actions = [
                "quarantined_affected_systems", 
                "initiated_malware_scan",
                "updated_security_signatures"
            ]
        elif incident["type"] == "data_breach":
            response_actions = [
                "isolated_affected_database",
                "rotated_access_credentials",
                "initiated_forensic_analysis",
                "notified_compliance_team"
            ]
        
        # Simulate response execution
        for action in response_actions:
            await asyncio.sleep(1)  # Simulate action execution time
            incident["response_actions"].append({
                "action": action,
                "timestamp": datetime.utcnow().isoformat(),
                "status": "completed"
            })
            logger.info(f"✅ Executed response action: {action}")
        
        # Update security status
        self._update_security_status()
    
    async def _auto_resolve_incident(self, incident_id: str, delay_seconds: int):
        """Auto-resolve incident after delay"""
        await asyncio.sleep(delay_seconds)
        
        # Find and resolve incident
        for incident in self.incidents:
            if incident["id"] == incident_id and incident["status"] == "active":
                incident["status"] = "resolved"
                incident["resolved_at"] = datetime.utcnow().isoformat()
                logger.info(f"✅ Auto-resolved incident: {incident_id}")
                break
        
        self._update_security_status()
    
    def _update_security_status(self):
        """Update overall security status"""
        active_incidents = [i for i in self.incidents if i["status"] == "active"]
        
        # Determine threat level
        if any(i["severity"] == "critical" for i in active_incidents):
            threat_level = "critical"
        elif any(i["severity"] == "high" for i in active_incidents):
            threat_level = "high" 
        elif any(i["severity"] == "medium" for i in active_incidents):
            threat_level = "medium"
        else:
            threat_level = "low"
        
        self.security_status.update({
            "threat_level": threat_level,
            "active_incidents": len(active_incidents),
            "last_updated": datetime.utcnow().isoformat()
        })
        
        if active_incidents:
            self.security_status["last_attack"] = max(
                i["created_at"] for i in active_incidents
            )
    
    async def get_security_status(self) -> Dict:
        """Get current security status"""
        return self.security_status
    
    async def get_recent_incidents(self) -> List[Dict]:
        """Get recent security incidents"""
        # Return incidents from last 24 hours
        cutoff_time = datetime.utcnow() - timedelta(days=1)
        recent_incidents = [
            i for i in self.incidents
            if datetime.fromisoformat(i["created_at"]) > cutoff_time
        ]
        
        # Sort by creation time, most recent first
        recent_incidents.sort(key=lambda x: x["created_at"], reverse=True)
        
        return recent_incidents[:50]  # Return last 50 incidents
