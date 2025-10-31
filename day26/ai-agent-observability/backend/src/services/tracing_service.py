from opentelemetry import trace
from opentelemetry.sdk.trace import TracerProvider
from opentelemetry.sdk.trace.export import BatchSpanProcessor
from opentelemetry.exporter.jaeger.thrift import JaegerExporter
from typing import List, Dict, Any, Optional
import asyncio
import json
import time
from datetime import datetime, timedelta
import structlog

logger = structlog.get_logger()

class TracingService:
    def __init__(self):
        # Initialize OpenTelemetry
        trace.set_tracer_provider(TracerProvider())
        tracer = trace.get_tracer(__name__)
        
        jaeger_exporter = JaegerExporter(
            agent_host_name="localhost",
            agent_port=6831,
        )
        
        span_processor = BatchSpanProcessor(jaeger_exporter)
        trace.get_tracer_provider().add_span_processor(span_processor)
        
        self.tracer = tracer
        self.active_traces: Dict[str, Dict] = {}
        self.trace_history: List[Dict] = []

    async def start_trace(self, operation: str, metadata: Dict = None) -> str:
        """Start a new distributed trace"""
        trace_id = f"trace_{int(time.time() * 1000000)}"
        
        with self.tracer.start_as_current_span(operation) as span:
            span.set_attribute("trace.id", trace_id)
            span.set_attribute("service.name", "ai-agent")
            span.set_attribute("operation.name", operation)
            
            if metadata:
                for key, value in metadata.items():
                    span.set_attribute(f"metadata.{key}", str(value))
            
            trace_data = {
                "trace_id": trace_id,
                "operation": operation,
                "start_time": datetime.now().isoformat(),
                "status": "active",
                "spans": [],
                "metadata": metadata or {},
                "security_events": [],
                "performance_metrics": {}
            }
            
            self.active_traces[trace_id] = trace_data
            
            logger.info("Started trace", trace_id=trace_id, operation=operation)
            return trace_id

    async def add_span(self, trace_id: str, span_name: str, 
                      duration_ms: float = None, metadata: Dict = None):
        """Add a span to an existing trace"""
        if trace_id not in self.active_traces:
            logger.warning("Trace not found", trace_id=trace_id)
            return
        
        span_data = {
            "span_id": f"span_{len(self.active_traces[trace_id]['spans'])}",
            "name": span_name,
            "start_time": datetime.now().isoformat(),
            "duration_ms": duration_ms,
            "metadata": metadata or {},
            "status": "completed" if duration_ms else "active"
        }
        
        self.active_traces[trace_id]["spans"].append(span_data)
        
        # Security correlation
        await self._correlate_security_events(trace_id, span_data)
        
        logger.info("Added span", trace_id=trace_id, span_name=span_name)

    async def complete_trace(self, trace_id: str, status: str = "success"):
        """Complete a distributed trace"""
        if trace_id not in self.active_traces:
            logger.warning("Trace not found for completion", trace_id=trace_id)
            return
        
        trace_data = self.active_traces[trace_id]
        trace_data["status"] = status
        trace_data["end_time"] = datetime.now().isoformat()
        trace_data["total_duration_ms"] = self._calculate_total_duration(trace_data)
        
        # Move to history
        self.trace_history.append(trace_data)
        del self.active_traces[trace_id]
        
        # Keep only last 1000 traces in memory
        if len(self.trace_history) > 1000:
            self.trace_history = self.trace_history[-1000:]
        
        logger.info("Completed trace", trace_id=trace_id, status=status)

    async def get_recent_traces(self, limit: int = 50) -> List[Dict]:
        """Get recent traces for dashboard"""
        recent_traces = self.trace_history[-limit:]
        active_traces = list(self.active_traces.values())
        
        all_traces = recent_traces + active_traces
        return sorted(all_traces, key=lambda x: x.get("start_time", ""), reverse=True)

    async def get_trace_details(self, trace_id: str) -> Optional[Dict]:
        """Get detailed information for a specific trace"""
        if trace_id in self.active_traces:
            return self.active_traces[trace_id]
        
        for trace in self.trace_history:
            if trace["trace_id"] == trace_id:
                return trace
        
        return None

    async def _correlate_security_events(self, trace_id: str, span_data: Dict):
        """Correlate spans with security events"""
        # Check for suspicious patterns
        if "auth" in span_data["name"].lower():
            if span_data.get("duration_ms", 0) > 5000:  # Slow auth
                security_event = {
                    "type": "slow_authentication",
                    "timestamp": datetime.now().isoformat(),
                    "span_id": span_data["span_id"],
                    "severity": "medium"
                }
                self.active_traces[trace_id]["security_events"].append(security_event)

    def _calculate_total_duration(self, trace_data: Dict) -> float:
        """Calculate total trace duration"""
        if not trace_data.get("spans"):
            return 0.0
        
        start_time = datetime.fromisoformat(trace_data["start_time"])
        end_time = datetime.fromisoformat(trace_data.get("end_time", datetime.now().isoformat()))
        
        return (end_time - start_time).total_seconds() * 1000

    async def health_check(self) -> Dict:
        """Service health check"""
        return {
            "status": "healthy",
            "active_traces": len(self.active_traces),
            "total_traces": len(self.trace_history)
        }
