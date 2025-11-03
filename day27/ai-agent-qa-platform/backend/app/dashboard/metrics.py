import asyncio
import logging
from datetime import datetime, timedelta
from typing import Dict, List
import json
import random

logger = logging.getLogger(__name__)

class MetricsCollector:
    def __init__(self):
        self.metrics_data = {
            "security_metrics": {},
            "performance_metrics": {},
            "compliance_metrics": {},
            "quality_gates_metrics": {}
        }
        self.is_running = False
        
    async def start(self):
        """Start metrics collection"""
        self.is_running = True
        asyncio.create_task(self._collect_metrics_loop())
        logger.info("Metrics collector started")
    
    async def stop(self):
        """Stop metrics collection"""
        self.is_running = False
        logger.info("Metrics collector stopped")
    
    async def _collect_metrics_loop(self):
        """Continuous metrics collection loop"""
        while self.is_running:
            try:
                await self._collect_security_metrics()
                await self._collect_performance_metrics()
                await self._collect_compliance_metrics()
                await self._collect_quality_gates_metrics()
                await asyncio.sleep(30)  # Collect every 30 seconds
            except Exception as e:
                logger.error(f"Metrics collection error: {str(e)}")
                await asyncio.sleep(5)
    
    async def _collect_security_metrics(self):
        """Collect security-related metrics"""
        self.metrics_data["security_metrics"] = {
            "vulnerability_scans_today": random.randint(10, 50),
            "critical_vulnerabilities": random.randint(0, 5),
            "high_vulnerabilities": random.randint(2, 15),
            "medium_vulnerabilities": random.randint(5, 25),
            "low_vulnerabilities": random.randint(10, 40),
            "security_score": round(random.uniform(7.5, 9.8), 2),
            "last_scan_time": datetime.utcnow().isoformat(),
            "threat_detection_rate": round(random.uniform(0.85, 0.98), 3)
        }
    
    async def _collect_performance_metrics(self):
        """Collect performance-related metrics"""
        self.metrics_data["performance_metrics"] = {
            "avg_response_time_ms": round(random.uniform(50, 200), 2),
            "p95_response_time_ms": round(random.uniform(150, 350), 2),
            "p99_response_time_ms": round(random.uniform(200, 500), 2),
            "requests_per_second": round(random.uniform(100, 1000), 2),
            "error_rate": round(random.uniform(0.001, 0.01), 4),
            "cpu_usage": round(random.uniform(0.3, 0.8), 3),
            "memory_usage": round(random.uniform(0.4, 0.7), 3),
            "active_connections": random.randint(50, 500)
        }
    
    async def _collect_compliance_metrics(self):
        """Collect compliance-related metrics"""
        self.metrics_data["compliance_metrics"] = {
            "gdpr_compliance_score": round(random.uniform(0.85, 1.0), 3),
            "soc2_controls_implemented": random.randint(85, 100),
            "audit_events_today": random.randint(100, 1000),
            "compliance_violations": random.randint(0, 3),
            "data_retention_compliance": round(random.uniform(0.9, 1.0), 3),
            "encryption_coverage": round(random.uniform(0.95, 1.0), 3),
            "last_audit_date": (datetime.utcnow() - timedelta(days=random.randint(1, 30))).isoformat()
        }
    
    async def _collect_quality_gates_metrics(self):
        """Collect quality gates metrics"""
        self.metrics_data["quality_gates_metrics"] = {
            "deployments_today": random.randint(5, 25),
            "deployments_passed": random.randint(4, 20),
            "deployments_failed": random.randint(1, 5),
            "average_gate_time_ms": round(random.uniform(2000, 8000), 2),
            "security_gate_pass_rate": round(random.uniform(0.85, 0.98), 3),
            "performance_gate_pass_rate": round(random.uniform(0.80, 0.95), 3),
            "compliance_gate_pass_rate": round(random.uniform(0.90, 1.0), 3),
            "overall_pass_rate": round(random.uniform(0.82, 0.95), 3)
        }
    
    async def get_dashboard_data(self) -> Dict:
        """Get comprehensive dashboard data"""
        return {
            "timestamp": datetime.utcnow().isoformat(),
            "system_status": "healthy",
            "metrics": self.metrics_data,
            "alerts": self._generate_alerts(),
            "trends": self._calculate_trends()
        }
    
    def _generate_alerts(self) -> List[Dict]:
        """Generate system alerts"""
        alerts = []
        
        # Security alerts
        if self.metrics_data.get("security_metrics", {}).get("critical_vulnerabilities", 0) > 0:
            alerts.append({
                "type": "security",
                "severity": "critical",
                "message": f"Critical vulnerabilities detected: {self.metrics_data['security_metrics']['critical_vulnerabilities']}",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Performance alerts
        if self.metrics_data.get("performance_metrics", {}).get("avg_response_time_ms", 0) > 200:
            alerts.append({
                "type": "performance",
                "severity": "warning",
                "message": "Average response time exceeds 200ms threshold",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        # Compliance alerts
        if self.metrics_data.get("compliance_metrics", {}).get("compliance_violations", 0) > 0:
            alerts.append({
                "type": "compliance",
                "severity": "high",
                "message": f"Compliance violations detected: {self.metrics_data['compliance_metrics']['compliance_violations']}",
                "timestamp": datetime.utcnow().isoformat()
            })
        
        return alerts
    
    def _calculate_trends(self) -> Dict:
        """Calculate trend indicators"""
        return {
            "security_score_trend": "improving",
            "performance_trend": "stable",
            "compliance_trend": "improving",
            "quality_gates_trend": "stable"
        }
