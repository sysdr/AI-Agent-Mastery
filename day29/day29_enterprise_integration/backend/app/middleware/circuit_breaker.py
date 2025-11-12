from starlette.middleware.base import BaseHTTPMiddleware
from fastapi import Request
from fastapi.responses import JSONResponse
import time
from collections import defaultdict
import os

class CircuitBreakerMiddleware(BaseHTTPMiddleware):
    def __init__(self, app):
        super().__init__(app)
        self.circuits = defaultdict(lambda: {
            "state": "CLOSED",
            "failure_count": 0,
            "success_count": 0,
            "last_failure_time": 0,
            "opened_at": 0
        })
        self.threshold = int(os.getenv("CIRCUIT_BREAKER_THRESHOLD", "5"))
        self.timeout = int(os.getenv("CIRCUIT_BREAKER_TIMEOUT", "60"))
    
    async def dispatch(self, request: Request, call_next):
        service = self._get_service_name(request)
        circuit = self.circuits[service]
        current_time = time.time()
        
        # Check circuit state
        if circuit["state"] == "OPEN":
            if current_time - circuit["opened_at"] >= self.timeout:
                circuit["state"] = "HALF_OPEN"
                circuit["failure_count"] = 0
            else:
                # Create response with CORS headers
                response = JSONResponse(
                    status_code=503,
                    content={
                        "detail": "Service unavailable - Circuit breaker is OPEN",
                        "service": service,
                        "retry_after": self.timeout - (current_time - circuit["opened_at"])
                    }
                )
                # Add CORS headers manually since we're returning early
                origin = request.headers.get("origin")
                if origin and origin in ["http://localhost:3000", "http://localhost:5173"]:
                    response.headers["Access-Control-Allow-Origin"] = origin
                    response.headers["Access-Control-Allow-Credentials"] = "true"
                    response.headers["Access-Control-Allow-Methods"] = "*"
                    response.headers["Access-Control-Allow-Headers"] = "*"
                return response
        
        try:
            response = await call_next(request)
            
            if response.status_code < 500:
                circuit["success_count"] += 1
                if circuit["state"] == "HALF_OPEN" and circuit["success_count"] >= 3:
                    circuit["state"] = "CLOSED"
                    circuit["failure_count"] = 0
            else:
                self._record_failure(circuit, current_time)
            
            return response
            
        except Exception as e:
            self._record_failure(circuit, current_time)
            raise
    
    def _get_service_name(self, request: Request) -> str:
        path_parts = request.url.path.split("/")
        if len(path_parts) > 3:
            return path_parts[3]
        return "unknown"
    
    def _record_failure(self, circuit, current_time):
        circuit["failure_count"] += 1
        circuit["last_failure_time"] = current_time
        
        if circuit["failure_count"] >= self.threshold:
            circuit["state"] = "OPEN"
            circuit["opened_at"] = current_time
