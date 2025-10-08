from fastapi import FastAPI, UploadFile, File, HTTPException, Depends, BackgroundTasks
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import os
import uuid
import asyncio
from typing import List, Optional
import json
from datetime import datetime

from .services.security_service import SecurityService
from .services.image_service import ImageSecurityService  
from .services.document_service import DocumentSecurityService
from .services.audio_service import AudioSecurityService
from .models.schemas import SecurityAnalysisResult, ContentModerationRequest

app = FastAPI(title="Multi-Modal Security Agent", version="1.0.0")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize services
security_service = SecurityService()
image_service = ImageSecurityService()
document_service = DocumentSecurityService()
audio_service = AudioSecurityService()

@app.get("/")
async def root():
    return {"message": "Multi-Modal Security Agent API", "status": "active"}

@app.post("/api/analyze/image", response_model=SecurityAnalysisResult)
async def analyze_image(file: UploadFile = File(...)):
    """Analyze uploaded image for security threats and content moderation"""
    if not file.content_type.startswith('image/'):
        raise HTTPException(status_code=400, detail="File must be an image")
    
    file_id = str(uuid.uuid4())
    file_path = f"uploads/images/{file_id}_{file.filename}"
    
    # Save uploaded file
    os.makedirs("uploads/images", exist_ok=True)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    try:
        # Analyze image
        result = await image_service.analyze_image(file_path, file.filename)
        result.file_id = file_id
        result.timestamp = datetime.utcnow()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/analyze/document", response_model=SecurityAnalysisResult)
async def analyze_document(file: UploadFile = File(...)):
    """Analyze uploaded document for PII and sensitive content"""
    allowed_types = ['application/pdf', 'text/plain', 'application/msword', 
                     'application/vnd.openxmlformats-officedocument.wordprocessingml.document']
    
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Unsupported document type")
    
    file_id = str(uuid.uuid4())
    file_path = f"uploads/documents/{file_id}_{file.filename}"
    
    os.makedirs("uploads/documents", exist_ok=True)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    try:
        result = await document_service.analyze_document(file_path, file.filename)
        result.file_id = file_id
        result.timestamp = datetime.utcnow()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.post("/api/analyze/audio", response_model=SecurityAnalysisResult)
async def analyze_audio(file: UploadFile = File(...)):
    """Analyze uploaded audio for content moderation and speech recognition"""
    allowed_types = ['audio/mpeg', 'audio/wav', 'audio/mp4', 'audio/ogg']
    
    if file.content_type not in allowed_types:
        raise HTTPException(status_code=400, detail="Unsupported audio type")
    
    file_id = str(uuid.uuid4())
    file_path = f"uploads/audio/{file_id}_{file.filename}"
    
    os.makedirs("uploads/audio", exist_ok=True)
    with open(file_path, "wb") as f:
        content = await file.read()
        f.write(content)
    
    try:
        result = await audio_service.analyze_audio(file_path, file.filename)
        result.file_id = file_id
        result.timestamp = datetime.utcnow()
        
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@app.get("/api/reports/summary")
async def get_moderation_summary():
    """Get summary of all moderation activities"""
    return await security_service.get_moderation_summary()

@app.get("/api/reports/detailed/{file_id}")
async def get_detailed_report(file_id: str):
    """Get detailed analysis report for specific file"""
    return await security_service.get_detailed_report(file_id)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
