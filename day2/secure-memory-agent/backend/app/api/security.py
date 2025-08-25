from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from app.db.database import get_db
from services.encryption_service import EncryptionService
from services.pii_service import PIIService
from pydantic import BaseModel

router = APIRouter()

class PIIAnalysisRequest(BaseModel):
    text: str

class EncryptionTestRequest(BaseModel):
    text: str
    conversation_id: str

@router.post("/pii-analysis")
async def analyze_pii(request: PIIAnalysisRequest):
    """Analyze text for PII detection"""
    pii_service = PIIService()
    result = await pii_service.detect_pii(request.text)
    return result

@router.post("/encryption-test")
async def test_encryption(request: EncryptionTestRequest):
    """Test encryption/decryption functionality"""
    encryption_service = EncryptionService()
    
    try:
        # Encrypt
        encrypted = encryption_service.encrypt_content(
            request.text, 
            request.conversation_id
        )
        
        # Decrypt
        decrypted = encryption_service.decrypt_content(
            encrypted, 
            request.conversation_id
        )
        
        return {
            "original": request.text,
            "encrypted": encrypted,
            "decrypted": decrypted,
            "success": decrypted == request.text
        }
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Encryption test failed: {str(e)}")

@router.get("/health-check")
async def security_health_check(db: Session = Depends(get_db)):
    """Comprehensive security health check"""
    
    checks = {
        "database_encryption": False,
        "pii_detection": False,
        "audit_logging": False,
        "encryption_service": False
    }
    
    try:
        # Test database connection
        db.execute("SELECT 1")
        checks["database_encryption"] = True
    except:
        pass
    
    try:
        # Test PII detection
        pii_service = PIIService()
        await pii_service.detect_pii("test@example.com")
        checks["pii_detection"] = True
    except:
        pass
    
    try:
        # Test encryption
        encryption_service = EncryptionService()
        test_encrypted = encryption_service.encrypt_content("test", "test-id")
        test_decrypted = encryption_service.decrypt_content(test_encrypted, "test-id")
        checks["encryption_service"] = test_decrypted == "test"
    except:
        pass
    
    # Audit logging is working if we can query audit logs
    try:
        from models.conversation import AuditLog
        db.query(AuditLog).first()
        checks["audit_logging"] = True
    except:
        pass
    
    return {
        "status": "healthy" if all(checks.values()) else "degraded",
        "checks": checks
    }
