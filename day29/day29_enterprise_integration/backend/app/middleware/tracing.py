from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
import uuid
import time

class TracingMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Generate or extract correlation ID
        correlation_id = request.headers.get("X-Correlation-ID", str(uuid.uuid4()))
        request.state.correlation_id = correlation_id
        
        # Add trace context
        request.state.trace_id = str(uuid.uuid4())
        request.state.span_id = str(uuid.uuid4())
        request.state.start_time = time.time()
        
        response = await call_next(request)
        
        # Add tracing headers to response
        response.headers["X-Correlation-ID"] = correlation_id
        response.headers["X-Trace-ID"] = request.state.trace_id
        
        return response
