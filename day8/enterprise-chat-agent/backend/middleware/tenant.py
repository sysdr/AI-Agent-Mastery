from fastapi import Request, HTTPException
from starlette.middleware.base import BaseHTTPMiddleware
import structlog

logger = structlog.get_logger()

class TenantMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next):
        # Add tenant context to request
        if hasattr(request.state, 'tenant_id'):
            logger.info("Request with tenant context", 
                       tenant_id=request.state.tenant_id,
                       path=request.url.path)
        
        response = await call_next(request)
        
        # Add tenant isolation headers
        if hasattr(request.state, 'tenant_id'):
            response.headers["X-Tenant-ID"] = request.state.tenant_id
        
        return response
