import google.generativeai as genai
from prometheus_client import Counter, Histogram, Gauge, generate_latest, REGISTRY
import time
import asyncio
from typing import Dict, List, Any
import json
import numpy as np
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger()

_metrics_service_instance = None

class MetricsService:
    def __new__(cls):
        global _metrics_service_instance
        if _metrics_service_instance is None:
            _metrics_service_instance = super().__new__(cls)
        return _metrics_service_instance
    
    def __init__(self):
        # Skip initialization if already initialized
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        
        # Configure Gemini AI
        genai.configure(api_key="AIzaSyDGswqDT4wQw_bd4WZtIgYAawRDZ0Gisn8")
        self.model = genai.GenerativeModel('gemini-pro')
        
        # Create Prometheus metrics - only create if they don't exist
        try:
            self.request_counter = Counter('ai_agent_requests_total', 'Total AI agent requests', ['agent_type', 'status'])
        except ValueError:
            # Metric already exists, find it in registry
            for collector in REGISTRY._collector_to_names.keys():
                if getattr(collector, '_name', None) == 'ai_agent_requests_total':
                    self.request_counter = collector
                    break
        
        try:
            self.response_time_histogram = Histogram('ai_agent_response_time_seconds', 'Response time histogram')
        except ValueError:
            for collector in REGISTRY._collector_to_names.keys():
                if getattr(collector, '_name', None) == 'ai_agent_response_time_seconds':
                    self.response_time_histogram = collector
                    break
        
        try:
            self.confidence_gauge = Gauge('ai_agent_confidence_score', 'Agent confidence score', ['agent_id'])
        except ValueError:
            for collector in REGISTRY._collector_to_names.keys():
                if getattr(collector, '_name', None) == 'ai_agent_confidence_score':
                    self.confidence_gauge = collector
                    break
        
        try:
            self.anomaly_counter = Counter('anomalies_detected_total', 'Total anomalies detected', ['type'])
        except ValueError:
            for collector in REGISTRY._collector_to_names.keys():
                if getattr(collector, '_name', None) == 'anomalies_detected_total':
                    self.anomaly_counter = collector
                    break
        
        # Custom metrics storage
        self.custom_metrics: Dict[str, List[Dict]] = {
            'confidence_scores': [],
            'token_usage': [],
            'model_performance': [],
            'security_scores': []
        }
        
        # Anomaly detection state
        self.baseline_metrics: Dict[str, float] = {}
        self.anomaly_threshold = 2.0  # Standard deviations

    async def record_request(self, agent_type: str, status: str, response_time: float):
        """Record a request metric"""
        self.request_counter.labels(agent_type=agent_type, status=status).inc()
        self.response_time_histogram.observe(response_time)
        
        logger.info("Recorded request metric", 
                   agent_type=agent_type, status=status, response_time=response_time)

    async def record_confidence_score(self, agent_id: str, confidence: float, context: Dict = None):
        """Record AI agent confidence score"""
        self.confidence_gauge.labels(agent_id=agent_id).set(confidence)
        
        metric_data = {
            'timestamp': datetime.now().isoformat(),
            'agent_id': agent_id,
            'confidence': confidence,
            'context': context or {}
        }
        
        self.custom_metrics['confidence_scores'].append(metric_data)
        
        # Keep only last 1000 metrics
        if len(self.custom_metrics['confidence_scores']) > 1000:
            self.custom_metrics['confidence_scores'] = self.custom_metrics['confidence_scores'][-1000:]
        
        # Check for anomalies
        await self._detect_confidence_anomaly(agent_id, confidence)

    async def record_token_usage(self, operation: str, tokens_used: int, cost_estimate: float):
        """Record token usage metrics"""
        metric_data = {
            'timestamp': datetime.now().isoformat(),
            'operation': operation,
            'tokens_used': tokens_used,
            'cost_estimate': cost_estimate
        }
        
        self.custom_metrics['token_usage'].append(metric_data)

    async def get_real_time_metrics(self) -> Dict[str, Any]:
        """Get real-time metrics for dashboard"""
        current_time = datetime.now()
        last_5_min = current_time - timedelta(minutes=5)
        
        # Recent confidence scores
        recent_confidence = [
            m for m in self.custom_metrics['confidence_scores'] 
            if datetime.fromisoformat(m['timestamp']) > last_5_min
        ]
        
        # Recent token usage
        recent_tokens = [
            m for m in self.custom_metrics['token_usage']
            if datetime.fromisoformat(m['timestamp']) > last_5_min
        ]
        
        return {
            'timestamp': current_time.isoformat(),
            'confidence_metrics': {
                'average': np.mean([m['confidence'] for m in recent_confidence]) if recent_confidence else 0,
                'min': np.min([m['confidence'] for m in recent_confidence]) if recent_confidence else 0,
                'max': np.max([m['confidence'] for m in recent_confidence]) if recent_confidence else 0,
                'count': len(recent_confidence)
            },
            'token_metrics': {
                'total_tokens': sum([m['tokens_used'] for m in recent_tokens]),
                'total_cost': sum([m['cost_estimate'] for m in recent_tokens]),
                'operations_count': len(recent_tokens)
            },
            'anomalies_detected': await self._get_recent_anomalies()
        }

    async def _detect_confidence_anomaly(self, agent_id: str, confidence: float):
        """Detect anomalies in confidence scores using Gemini AI"""
        recent_scores = [
            m['confidence'] for m in self.custom_metrics['confidence_scores'][-50:]
            if m['agent_id'] == agent_id
        ]
        
        if len(recent_scores) < 10:
            return  # Need more data points
        
        mean_confidence = np.mean(recent_scores)
        std_confidence = np.std(recent_scores)
        
        if abs(confidence - mean_confidence) > (self.anomaly_threshold * std_confidence):
            # Use Gemini AI for intelligent anomaly analysis
            try:
                prompt = f"""
                Analyze this AI agent confidence anomaly:
                
                Agent ID: {agent_id}
                Current Confidence: {confidence}
                Recent Average: {mean_confidence:.3f}
                Standard Deviation: {std_confidence:.3f}
                Recent Scores: {recent_scores[-10:]}
                
                Determine:
                1. Anomaly severity (low/medium/high)
                2. Possible root causes
                3. Recommended actions
                
                Respond in JSON format with fields: severity, causes, actions
                """
                
                response = await asyncio.to_thread(
                    lambda: self.model.generate_content(prompt)
                )
                
                analysis = json.loads(response.text.strip().replace('```json', '').replace('```', ''))
                
                anomaly_data = {
                    'type': 'confidence_anomaly',
                    'timestamp': datetime.now().isoformat(),
                    'agent_id': agent_id,
                    'confidence': confidence,
                    'baseline': mean_confidence,
                    'deviation': abs(confidence - mean_confidence),
                    'analysis': analysis
                }
                
                self.anomaly_counter.labels(type='confidence').inc()
                
                if not hasattr(self, 'detected_anomalies'):
                    self.detected_anomalies = []
                
                self.detected_anomalies.append(anomaly_data)
                
                logger.warning("Confidence anomaly detected", 
                              agent_id=agent_id, confidence=confidence, analysis=analysis)
                
            except Exception as e:
                logger.error("Error in anomaly analysis", error=str(e))

    async def _get_recent_anomalies(self) -> List[Dict]:
        """Get recent anomalies for dashboard"""
        if not hasattr(self, 'detected_anomalies'):
            return []
        
        last_hour = datetime.now() - timedelta(hours=1)
        recent_anomalies = [
            a for a in self.detected_anomalies
            if datetime.fromisoformat(a['timestamp']) > last_hour
        ]
        
        return recent_anomalies[-10:]  # Last 10 anomalies

    async def get_prometheus_metrics(self) -> str:
        """Get metrics in Prometheus format"""
        return generate_latest()

    async def health_check(self) -> Dict:
        """Service health check"""
        return {
            "status": "healthy",
            "metrics_count": sum(len(metrics) for metrics in self.custom_metrics.values()),
            "anomalies_detected": len(getattr(self, 'detected_anomalies', []))
        }
