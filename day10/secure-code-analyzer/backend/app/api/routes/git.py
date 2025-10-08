"""
Git integration API routes
"""

from fastapi import APIRouter, HTTPException, Depends, Request
from typing import Dict, Any
import json

from app.services.git_service import GitService
from app.core.config import get_settings

router = APIRouter()

def get_git_service():
    return GitService()

@router.post("/analyze-repository")
async def analyze_repository(
    repo_data: Dict[str, Any],
    git_service: GitService = Depends(get_git_service)
):
    """Analyze entire repository for security issues"""
    repo_url = repo_data.get("repo_url")
    branch = repo_data.get("branch", "main")
    
    if not repo_url:
        raise HTTPException(status_code=400, detail="Repository URL is required")
    
    try:
        analysis = await git_service.analyze_repository(repo_url, branch)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Analysis failed: {str(e)}")

@router.post("/analyze-pr")
async def analyze_pull_request(
    pr_data: Dict[str, Any],
    git_service: GitService = Depends(get_git_service)
):
    """Analyze pull request changes"""
    repo_url = pr_data.get("repo_url")
    base_branch = pr_data.get("base_branch", "main")
    head_branch = pr_data.get("head_branch")
    
    if not all([repo_url, head_branch]):
        raise HTTPException(status_code=400, detail="Repository URL and head branch are required")
    
    try:
        analysis = await git_service.analyze_diff(repo_url, base_branch, head_branch)
        return analysis
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"PR analysis failed: {str(e)}")

@router.post("/webhook")
async def handle_webhook(request: Request):
    """Handle Git webhooks"""
    settings = get_settings()
    git_service = GitService()
    
    # Get headers
    event_type = request.headers.get("X-GitHub-Event", "")
    signature = request.headers.get("X-Hub-Signature-256", "")
    
    # Get payload
    payload = await request.body()
    
    # Verify signature if secret is configured
    if settings.git_webhook_secret:
        if not git_service.verify_webhook_signature(
            payload, signature, settings.git_webhook_secret
        ):
            raise HTTPException(status_code=401, detail="Invalid signature")
    
    # Parse JSON payload
    try:
        payload_json = json.loads(payload.decode())
    except json.JSONDecodeError:
        raise HTTPException(status_code=400, detail="Invalid JSON payload")
    
    # Handle event
    try:
        result = await git_service.handle_webhook_event(event_type, payload_json)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Webhook handling failed: {str(e)}")

@router.get("/repositories")
async def list_repositories():
    """List analyzed repositories"""
    # This would typically come from a database
    return {
        "repositories": [
            {
                "id": 1,
                "name": "security-demo-app",
                "url": "https://github.com/user/security-demo-app",
                "last_scan": "2024-11-20T10:30:00Z",
                "findings": 12,
                "status": "needs_attention"
            },
            {
                "id": 2,
                "name": "web-api-service",
                "url": "https://github.com/user/web-api-service", 
                "last_scan": "2024-11-20T09:15:00Z",
                "findings": 3,
                "status": "clean"
            }
        ]
    }
