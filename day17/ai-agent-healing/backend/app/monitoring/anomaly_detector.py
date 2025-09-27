import asyncio
import json
import random
import numpy as np
from datetime import datetime, timedelta
from typing import Dict, List, Optional
import google.generativeai as genai
import structlog
import os

logger = structlog.get_logger()

class AnomalyDetector:
    def __init__(self):
        self.gemini_api_key = os.getenv("GEMINI_API_KEY", "your-gemini-api-key")
        self.demo_mode = self.gemini_api_key in ["demo-key-for-testing", "your-gemini-api-key"]
        
        if not self.demo_mode:
            genai.configure(api_key=self.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            self.model = None
        
        self.baseline_metrics = {
            "request_rate": 100,
            "error_rate": 0.01,
            "response_time": 0.2,
            "cpu_usage": 0.4,
            "memory_usage": 0.6
        }
        
        self.anomaly_threshold = 2.0  # Standard deviations
        self.security_events = []
        
    async def continuous_detection(self):
        """Continuous anomaly detection loop"""
        logger.info("🔍 Starting continuous anomaly detection")
        
        while True:
            try:
                # Collect current metrics
                current_metrics = await self._collect_metrics()
                
                # Detect anomalies
                anomalies = await self._detect_anomalies(current_metrics)
                
                if anomalies:
                    await self._process_anomalies(anomalies)
                
                await asyncio.sleep(5)  # Check every 5 seconds
                
            except Exception as e:
                logger.error(f"Anomaly detection error: {e}")
                await asyncio.sleep(10)
    
    async def _collect_metrics(self) -> Dict:
        """Simulate metric collection with realistic variations"""
        
        # Add some realistic variance and occasional spikes
        variance_factor = 1 + random.gauss(0, 0.1)  # 10% normal variance
        
        # Simulate occasional attack patterns
        is_under_attack = random.random() < 0.05  # 5% chance
        attack_multiplier = 3.0 if is_under_attack else 1.0
        
        metrics = {
            "timestamp": datetime.utcnow().isoformat(),
            "request_rate": self.baseline_metrics["request_rate"] * variance_factor * attack_multiplier,
            "error_rate": min(self.baseline_metrics["error_rate"] * variance_factor * attack_multiplier, 1.0),
            "response_time": self.baseline_metrics["response_time"] * variance_factor * attack_multiplier,
            "cpu_usage": min(self.baseline_metrics["cpu_usage"] * variance_factor * attack_multiplier, 1.0),
            "memory_usage": min(self.baseline_metrics["memory_usage"] * variance_factor, 1.0),
            "failed_auth_attempts": 0 if not is_under_attack else random.randint(50, 200),
            "suspicious_ips": [] if not is_under_attack else [f"192.168.1.{random.randint(1, 254)}" for _ in range(random.randint(1, 5))]
        }
        
        return metrics
    
    async def _detect_anomalies(self, metrics: Dict) -> List[Dict]:
        """Detect anomalies using statistical and AI analysis"""
        anomalies = []
        
        # Statistical anomaly detection
        for metric_name in ["request_rate", "error_rate", "response_time", "cpu_usage"]:
            current_value = metrics[metric_name]
            baseline_value = self.baseline_metrics.get(metric_name, current_value)
            
            # Calculate z-score
            z_score = abs(current_value - baseline_value) / (baseline_value * 0.1)  # Assume 10% std dev
            
            if z_score > self.anomaly_threshold:
                anomalies.append({
                    "type": "statistical",
                    "metric": metric_name,
                    "current_value": current_value,
                    "baseline_value": baseline_value,
                    "z_score": z_score,
                    "severity": "high" if z_score > 3.0 else "medium"
                })
        
        # Security-specific anomaly detection
        if metrics["failed_auth_attempts"] > 20:
            anomalies.append({
                "type": "security",
                "metric": "failed_auth_attempts",
                "current_value": metrics["failed_auth_attempts"],
                "severity": "high",
                "description": "Brute force attack detected"
            })
        
        if len(metrics["suspicious_ips"]) > 0:
            anomalies.append({
                "type": "security", 
                "metric": "suspicious_ips",
                "current_value": len(metrics["suspicious_ips"]),
                "severity": "medium",
                "description": f"Suspicious IP activity: {', '.join(metrics['suspicious_ips'][:3])}"
            })
        
        # Use Gemini AI for context analysis
        if anomalies:
            ai_analysis = await self._ai_anomaly_analysis(metrics, anomalies)
            for anomaly in anomalies:
                anomaly["ai_analysis"] = ai_analysis
        
        return anomalies
    
    async def _ai_anomaly_analysis(self, metrics: Dict, anomalies: List[Dict]) -> str:
        """Use Gemini AI to analyze anomaly context"""
        try:
            if self.demo_mode:
                # Return demo analysis for testing
                return json.dumps({
                    "root_cause": "High system load detected in demo mode",
                    "risk_level": "medium",
                    "actions": ["Scale infrastructure", "Monitor resource usage"],
                    "attack_likely": False
                })
            
            prompt = f"""
            Analyze these system anomalies for an AI agent system:
            
            Current Metrics: {json.dumps(metrics, indent=2)}
            Detected Anomalies: {json.dumps(anomalies, indent=2)}
            
            Provide a concise analysis including:
            1. Root cause assessment
            2. Security risk level (low/medium/high)  
            3. Recommended immediate actions
            4. Whether this appears to be an attack or system issue
            
            Respond in JSON format with keys: root_cause, risk_level, actions, attack_likely
            """
            
            response = await asyncio.to_thread(self.model.generate_content, prompt)
            return response.text.strip()
        except Exception as e:
            logger.error(f"AI analysis error: {e}")
            return f"AI analysis unavailable: {str(e)}"
    
    async def _process_anomalies(self, anomalies: List[Dict]):
        """Process detected anomalies"""
        logger.warning(f"🚨 Detected {len(anomalies)} anomalies")
        
        # Store anomalies for incident management
        self.security_events.extend(anomalies)
        
        # Keep only recent events (last hour)
        cutoff_time = datetime.utcnow() - timedelta(hours=1)
        self.security_events = [
            event for event in self.security_events
            if datetime.fromisoformat(event.get("timestamp", datetime.utcnow().isoformat())) > cutoff_time
        ]
        
        # Trigger recovery for high-severity anomalies
        high_severity = [a for a in anomalies if a.get("severity") == "high"]
        if high_severity:
            logger.critical(f"🔴 High severity anomalies detected: {len(high_severity)}")
            
    async def get_recent_anomalies(self) -> List[Dict]:
        """Get recent anomalies for monitoring dashboard"""
        return self.security_events[-50:]  # Return last 50 events
