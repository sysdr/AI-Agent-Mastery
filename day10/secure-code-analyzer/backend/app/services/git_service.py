"""
Git Integration Service - Repository analysis and webhook handling
"""

import os
import tempfile
import shutil
from typing import List, Dict, Any, Optional
from pathlib import Path
import git
from git import Repo
import hmac
import hashlib

from app.services.security_engine import SecurityEngine, SecurityFinding

class GitService:
    """Git integration for repository analysis"""
    
    def __init__(self):
        self.security_engine = SecurityEngine()
        self.temp_dirs = []
    
    async def analyze_repository(self, repo_url: str, branch: str = "main") -> Dict[str, Any]:
        """Clone and analyze entire repository"""
        temp_dir = tempfile.mkdtemp()
        self.temp_dirs.append(temp_dir)
        
        try:
            # Clone repository
            repo = Repo.clone_from(repo_url, temp_dir, branch=branch)
            
            # Analyze all supported files
            findings = []
            file_count = 0
            
            for root, dirs, files in os.walk(temp_dir):
                # Skip .git directory
                if '.git' in dirs:
                    dirs.remove('.git')
                
                for file in files:
                    if self._is_supported_file(file):
                        file_path = os.path.join(root, file)
                        relative_path = os.path.relpath(file_path, temp_dir)
                        
                        try:
                            with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                                content = f.read()
                                file_findings = await self.security_engine.analyze_code(
                                    content, relative_path
                                )
                                findings.extend(file_findings)
                                file_count += 1
                        except Exception as e:
                            continue
            
            return {
                "repository": repo_url,
                "branch": branch,
                "files_analyzed": file_count,
                "total_findings": len(findings),
                "findings": [self._serialize_finding(f) for f in findings],
                "summary": self._create_summary(findings)
            }
            
        finally:
            # Cleanup temp directory
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    async def analyze_diff(self, repo_url: str, base_branch: str, head_branch: str) -> Dict[str, Any]:
        """Analyze only changed files in a pull request"""
        temp_dir = tempfile.mkdtemp()
        self.temp_dirs.append(temp_dir)
        
        try:
            repo = Repo.clone_from(repo_url, temp_dir)
            
            # Get diff between branches
            base_commit = repo.refs[f'origin/{base_branch}'].commit
            head_commit = repo.refs[f'origin/{head_branch}'].commit
            
            diff = base_commit.diff(head_commit)
            
            findings = []
            changed_files = []
            
            for diff_item in diff:
                if diff_item.a_path and self._is_supported_file(diff_item.a_path):
                    file_path = os.path.join(temp_dir, diff_item.a_path)
                    
                    if os.path.exists(file_path):
                        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
                            content = f.read()
                            file_findings = await self.security_engine.analyze_code(
                                content, diff_item.a_path
                            )
                            findings.extend(file_findings)
                            changed_files.append(diff_item.a_path)
            
            return {
                "base_branch": base_branch,
                "head_branch": head_branch,
                "changed_files": changed_files,
                "findings": [self._serialize_finding(f) for f in findings],
                "approval_status": self._determine_approval_status(findings)
            }
            
        finally:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
    
    def verify_webhook_signature(self, payload: bytes, signature: str, secret: str) -> bool:
        """Verify GitHub webhook signature"""
        expected_signature = hmac.new(
            secret.encode('utf-8'),
            payload,
            hashlib.sha256
        ).hexdigest()
        
        return hmac.compare_digest(f"sha256={expected_signature}", signature)
    
    async def handle_webhook_event(self, event_type: str, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle different webhook events"""
        if event_type == "pull_request":
            return await self._handle_pull_request(payload)
        elif event_type == "push":
            return await self._handle_push(payload)
        
        return {"status": "ignored", "event_type": event_type}
    
    async def _handle_pull_request(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle pull request webhook"""
        pr = payload.get("pull_request", {})
        repo_url = pr.get("head", {}).get("repo", {}).get("clone_url", "")
        base_branch = pr.get("base", {}).get("ref", "main")
        head_branch = pr.get("head", {}).get("ref", "feature")
        
        if repo_url:
            analysis = await self.analyze_diff(repo_url, base_branch, head_branch)
            return {
                "status": "analyzed",
                "pr_number": pr.get("number"),
                "analysis": analysis
            }
        
        return {"status": "error", "message": "Invalid PR payload"}
    
    async def _handle_push(self, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Handle push webhook"""
        repo_url = payload.get("repository", {}).get("clone_url", "")
        branch = payload.get("ref", "refs/heads/main").replace("refs/heads/", "")
        
        if repo_url:
            analysis = await self.analyze_repository(repo_url, branch)
            return {
                "status": "analyzed",
                "branch": branch,
                "analysis": analysis
            }
        
        return {"status": "error", "message": "Invalid push payload"}
    
    def _is_supported_file(self, filename: str) -> bool:
        """Check if file is supported for analysis"""
        supported_extensions = {'.py', '.js', '.ts', '.java', '.cpp', '.c', '.php', '.rb', '.go'}
        return Path(filename).suffix in supported_extensions
    
    def _serialize_finding(self, finding: SecurityFinding) -> Dict[str, Any]:
        """Convert finding to dictionary"""
        return {
            "rule_id": finding.rule_id,
            "severity": finding.severity.value,
            "message": finding.message,
            "file_path": finding.file_path,
            "line_number": finding.line_number,
            "column": finding.column,
            "code_snippet": finding.code_snippet,
            "recommendation": finding.recommendation,
            "cwe_id": finding.cwe_id
        }
    
    def _create_summary(self, findings: List[SecurityFinding]) -> Dict[str, int]:
        """Create summary of findings by severity"""
        summary = {"critical": 0, "high": 0, "medium": 0, "low": 0, "info": 0}
        
        for finding in findings:
            summary[finding.severity.value] += 1
        
        return summary
    
    def _determine_approval_status(self, findings: List[SecurityFinding]) -> str:
        """Determine if PR should be approved based on findings"""
        critical_count = sum(1 for f in findings if f.severity.value == "critical")
        high_count = sum(1 for f in findings if f.severity.value == "high")
        
        if critical_count > 0:
            return "blocked"
        elif high_count > 5:
            return "requires_review"
        else:
            return "approved"
    
    def cleanup(self):
        """Clean up temporary directories"""
        for temp_dir in self.temp_dirs:
            if os.path.exists(temp_dir):
                shutil.rmtree(temp_dir, ignore_errors=True)
        self.temp_dirs.clear()
