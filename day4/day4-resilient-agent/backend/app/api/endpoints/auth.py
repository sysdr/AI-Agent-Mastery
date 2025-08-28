from fastapi import APIRouter, Request, Response, HTTPException, Form
from ...core.session_manager import SessionManager
import redis.asyncio as redis

router = APIRouter()

async def get_session_manager():
    redis_client = redis.from_url("redis://localhost:6379")
    return SessionManager(redis_client)

@router.post("/login")
async def login(
    request: Request,
    response: Response,
    username: str = Form(...),
    password: str = Form(...)
):
    """Secure login with session management"""
    # Simplified authentication - in production, use proper password hashing
    if username == "admin" and password == "password":
        session_manager = await get_session_manager()
        
        user_data = {
            "username": username,
            "role": "admin",
            "permissions": ["read", "write", "admin"]
        }
        
        session_id = await session_manager.create_session(user_data, response)
        
        return {
            "success": True,
            "message": "Login successful",
            "session_id": session_id[:8] + "..."  # Don't expose full session ID
        }
    
    raise HTTPException(status_code=401, detail="Invalid credentials")

@router.post("/logout")
async def logout(request: Request, response: Response):
    """Secure logout"""
    session_manager = await get_session_manager()
    success = await session_manager.destroy_session(request, response)
    
    return {
        "success": success,
        "message": "Logout successful"
    }

@router.get("/session")
async def get_session_info(request: Request):
    """Get current session information"""
    session_manager = await get_session_manager()
    session = await session_manager.get_session(request)
    
    if not session:
        raise HTTPException(status_code=401, detail="No active session")
    
    return {
        "user": session.get("user_data", {}),
        "csrf_token": session.get("csrf_token"),
        "last_accessed": session.get("last_accessed")
    }
