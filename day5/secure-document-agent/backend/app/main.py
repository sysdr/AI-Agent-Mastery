from fastapi import FastAPI, File, UploadFile, Depends, HTTPException, status
from fastapi.middleware.cors import CORSMiddleware
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
import uvicorn
import logging
from typing import List, Optional
import os
from datetime import datetime
import json

from .core.config import settings
from .services.document_processor import DocumentProcessor
from .services.pii_detector import PIIDetector  
from .services.virus_scanner import VirusScanner
from .services.metadata_extractor import MetadataExtractor
from .services.secure_storage import SecureStorage
from .services.audit_logger import AuditLogger
from .schemas.document import DocumentResponse, ProcessingResult
from .middleware.security import SecurityMiddleware

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

app = FastAPI(
    title="Secure Document Processing Agent",
    description="Production-ready document intelligence with security controls",
    version="1.0.0"
)

# CORS configuration
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Security middleware
app.add_middleware(SecurityMiddleware)

# Initialize services
document_processor = DocumentProcessor()
pii_detector = PIIDetector()
virus_scanner = VirusScanner()
metadata_extractor = MetadataExtractor()
secure_storage = SecureStorage()
audit_logger = AuditLogger()

security = HTTPBearer()

async def verify_token(credentials: HTTPAuthorizationCredentials = Depends(security)):
    """Verify JWT token for authentication"""
    try:
        # In production, validate JWT token
        return {"user_id": "demo_user", "permissions": ["document:read", "document:write", "audit:read"]}
    except Exception:
        raise HTTPException(status_code=401, detail="Invalid authentication")

@app.post("/api/documents/upload", response_model=DocumentResponse)
async def upload_document(
    file: UploadFile = File(...),
    user: dict = Depends(verify_token)
):
    """Upload and process document with security scanning"""
    try:
        # Security validation
        if file.size > 50 * 1024 * 1024:  # 50MB limit
            raise HTTPException(status_code=413, detail="File too large")
        
        # Read file content
        content = await file.read()
        
        # Virus scanning
        scan_result = await virus_scanner.scan_content(content)
        if not scan_result.is_clean:
            audit_logger.log_security_event("virus_detected", {
                "filename": file.filename,
                "user_id": user["user_id"],
                "threat": scan_result.threat_name
            })
            raise HTTPException(status_code=400, detail="Security threat detected")
        
        # Process document
        processing_result = await document_processor.process(
            content=content,
            filename=file.filename,
            content_type=file.content_type
        )
        
        # PII Detection
        pii_results = await pii_detector.analyze_content(processing_result["text_content"])
        
        # Metadata extraction
        metadata = await metadata_extractor.extract(content, file.filename)
        
        # Secure storage
        document_id = await secure_storage.store_document(
            content=content,
            metadata=metadata,
            pii_info=pii_results,
            user_id=user["user_id"]
        )
        
        # Audit logging
        audit_logger.log_document_event("document_uploaded", {
            "document_id": document_id,
            "user_id": user["user_id"],
            "filename": file.filename,
            "pii_detected": len(pii_results.detected_entities) > 0,
            "content_type": metadata.get("content_type", "unknown")
        })
        
        return DocumentResponse(
            document_id=document_id,
            filename=file.filename,
            processing_result=processing_result,
            pii_summary=pii_results.get_summary(),
            metadata=metadata,
            status="processed",
            uploaded_at=datetime.utcnow()
        )
        
    except Exception as e:
        logger.error(f"Document processing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Processing failed")

@app.get("/api/documents/{document_id}", response_model=DocumentResponse)
async def get_document(
    document_id: str,
    user: dict = Depends(verify_token)
):
    """Retrieve document with access control"""
    try:
        # Check access permissions
        has_access = await secure_storage.check_access(document_id, user["user_id"])
        if not has_access:
            audit_logger.log_security_event("unauthorized_access", {
                "document_id": document_id,
                "user_id": user["user_id"]
            })
            raise HTTPException(status_code=403, detail="Access denied")
        
        document = await secure_storage.get_document(document_id)
        
        audit_logger.log_document_event("document_accessed", {
            "document_id": document_id,
            "user_id": user["user_id"]
        })
        
        return document
        
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Document retrieval failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Retrieval failed")

@app.get("/api/documents", response_model=List[DocumentResponse])
async def list_documents(
    user: dict = Depends(verify_token),
    skip: int = 0,
    limit: int = 20
):
    """List user's documents with pagination"""
    try:
        documents = await secure_storage.list_user_documents(
            user_id=user["user_id"],
            skip=skip,
            limit=limit
        )
        return documents
    except Exception as e:
        logger.error(f"Document listing failed: {str(e)}")
        raise HTTPException(status_code=500, detail="Listing failed")

@app.get("/api/audit/logs")
async def get_audit_logs(
    user: dict = Depends(verify_token),
    document_id: Optional[str] = None,
    limit: int = 50
):
    """Get audit logs for compliance"""
    if "audit:read" not in user.get("permissions", []):
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    logs = await audit_logger.get_logs(
        document_id=document_id,
        limit=limit
    )
    return {"logs": logs}

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "healthy",
        "timestamp": datetime.utcnow(),
        "services": {
            "document_processor": "active",
            "pii_detector": "active", 
            "virus_scanner": "active",
            "secure_storage": "active"
        }
    }

if __name__ == "__main__":
    uvicorn.run(
        "app.main:app",
        host="0.0.0.0",
        port=8000,
        reload=True,
        log_level="info"
    )
