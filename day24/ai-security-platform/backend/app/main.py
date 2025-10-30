from fastapi import FastAPI, Depends, HTTPException, status, Request
from fastapi.security import HTTPBearer, HTTPAuthorizationCredentials
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
from sqlalchemy.orm import Session
from .database import get_db, engine
from .models import models
from .auth.auth_service import auth_service
from .audit.audit_service import audit_service
from .compliance.compliance_service import compliance_service
from .security.security_service import security_service
from .config import settings
import uvicorn
from datetime import datetime, timedelta
from typing import Optional
import structlog

# Create tables
models.Base.metadata.create_all(bind=engine)

app = FastAPI(title="AI Security Platform", version="1.0.0")
security = HTTPBearer()
logger = structlog.get_logger()

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Dependency to get current user
async def get_current_user(
    credentials: HTTPAuthorizationCredentials = Depends(security),
    db: Session = Depends(get_db)
):
    token = credentials.credentials
    payload = auth_service.verify_token(token)
    if not payload:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="Invalid authentication credentials"
        )
    
    user = db.query(models.User).filter(models.User.id == payload.get("sub")).first()
    if not user:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="User not found"
        )
    return user

# Authentication endpoints
@app.post("/auth/register")
async def register(
    request: Request,
    user_data: dict,
    db: Session = Depends(get_db)
):
    # Check if user exists
    if db.query(models.User).filter(models.User.email == user_data["email"]).first():
        raise HTTPException(status_code=400, detail="Email already registered")
    
    # Create user
    hashed_password = auth_service.get_password_hash(user_data["password"])
    user = models.User(
        email=user_data["email"],
        username=user_data["username"],
        hashed_password=hashed_password,
        role=user_data.get("role", "user")
    )
    db.add(user)
    db.commit()
    db.refresh(user)
    
    # Create audit log
    audit_service.create_audit_log(
        db, user.id, "user_registered", "user_account",
        {"email": user.email}, request.client.host, request.headers.get("user-agent", "")
    )
    
    return {"message": "User registered successfully", "user_id": user.id}

@app.post("/auth/login")
async def login(
    request: Request,
    credentials: dict,
    db: Session = Depends(get_db)
):
    user = auth_service.authenticate_user(db, credentials["email"], credentials["password"])
    
    if not user:
        # Log failed login attempt (no user_id since login failed)
        try:
            audit_service.create_audit_log(
                db, None, "login_failed", "authentication",
                {"email": credentials["email"], "reason": "invalid_credentials"},
                request.client.host, request.headers.get("user-agent", "")
            )
        except Exception as e:
            logger.error("Failed to create audit log", error=str(e))
        raise HTTPException(status_code=401, detail="Invalid credentials")
    
    # Rate limiting check
    if not security_service.rate_limit_check(user.id, "login", 10, 3600):
        raise HTTPException(status_code=429, detail="Too many login attempts")
    
    # Create access token
    access_token_expires = timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    access_token = auth_service.create_access_token(
        data={"sub": str(user.id), "email": user.email, "role": user.role},
        expires_delta=access_token_expires
    )
    
    # Log successful login
    audit_service.create_audit_log(
        db, user.id, "login_success", "authentication",
        {"email": user.email}, request.client.host, request.headers.get("user-agent", "")
    )
    
    return {
        "access_token": access_token,
        "token_type": "bearer",
        "user": {
            "id": user.id,
            "email": user.email,
            "username": user.username,
            "role": user.role
        }
    }

# Security dashboard endpoints
@app.get("/security/dashboard")
async def security_dashboard(
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["admin", "security"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    dashboard_data = security_service.get_security_dashboard_data(db)
    return dashboard_data

@app.get("/security/incidents")
async def get_security_incidents(
    skip: int = 0,
    limit: int = 100,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["admin", "security"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    incidents = db.query(models.SecurityIncident).offset(skip).limit(limit).all()
    return incidents

@app.post("/security/incidents")
async def create_incident(
    incident_data: dict,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["admin", "security"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    incident = security_service.create_security_incident(
        db,
        incident_data["severity"],
        incident_data["type"],
        incident_data["description"],
        incident_data.get("user_id"),
        incident_data.get("details", {})
    )
    
    return {"message": "Incident created", "incident_id": incident.id}

# Compliance endpoints
@app.get("/compliance/report")
async def compliance_report(
    compliance_type: Optional[str] = None,
    days: int = 30,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["admin", "compliance"]:
        raise HTTPException(status_code=403, detail="Insufficient permissions")
    
    report = compliance_service.generate_compliance_report(db, compliance_type, days)
    return report

@app.get("/audit/logs")
async def get_audit_logs(
    skip: int = 0,
    limit: int = 100,
    user_id: Optional[int] = None,
    current_user: models.User = Depends(get_current_user),
    db: Session = Depends(get_db)
):
    if current_user.role not in ["admin", "audit"]:
        # Users can only see their own logs
        user_id = current_user.id
    
    logs = audit_service.get_audit_trail(db, user_id, limit)
    return logs

# Health check
@app.get("/health")
async def health_check():
    return {"status": "healthy", "timestamp": datetime.utcnow().isoformat()}

if __name__ == "__main__":
    uvicorn.run(app, host="0.0.0.0", port=8000)
