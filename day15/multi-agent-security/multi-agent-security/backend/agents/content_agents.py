from .base_agent import BaseAgent
from typing import Dict, Any, Optional
from models.database import SessionLocal, ContentItem, Agent

class WriterAgent(BaseAgent):
    """Agent specialized for content creation"""
    
    async def create_content(self, title: str, topic: str, length: int = 500) -> Optional[Dict[str, Any]]:
        """Create new content piece"""
        if not self.has_capability("content.create"):
            await self._log_audit("create_content", "DENIED", {"title": title}, False)
            return None
        
        # Generate content using Gemini
        prompt = f"""
        Create a {length}-word article about: {topic}
        Title: {title}
        
        Write in a professional, engaging style suitable for publication.
        Focus on practical insights and actionable information.
        """
        
        content = await self.call_gemini_api(prompt, max_tokens=length * 2)
        if not content:
            return None
        
        # Store in database
        db = SessionLocal()
        try:
            content_item = ContentItem(
                title=title,
                content=content,
                status="draft",
                writer_agent_id=self.agent_id
            )
            db.add(content_item)
            db.commit()
            db.refresh(content_item)
            
            await self._log_audit("create_content", "SUCCESS", {
                "content_id": content_item.id,
                "title": title
            }, True)
            
            return {
                "id": content_item.id,
                "title": title,
                "content": content,
                "status": "draft"
            }
            
        finally:
            db.close()

class EditorAgent(BaseAgent):
    """Agent specialized for content editing and approval"""
    
    async def review_content(self, content_id: int) -> Optional[Dict[str, Any]]:
        """Review and edit content"""
        if not self.has_capability("workflow.approve"):
            await self._log_audit("review_content", "DENIED", {"content_id": content_id}, False)
            return None
        
        db = SessionLocal()
        try:
            content = db.query(ContentItem).filter(ContentItem.id == content_id).first()
            if not content:
                return None
            
            # Generate review using Gemini
            prompt = f"""
            Review this article for quality, accuracy, and readability:
            
            Title: {content.title}
            Content: {content.content}
            
            Provide:
            1. Overall quality score (1-10)
            2. Specific suggestions for improvement
            3. Decision: APPROVE or NEEDS_REVISION
            
            Format as JSON with keys: score, suggestions, decision
            """
            
            review = await self.call_gemini_api(prompt, max_tokens=500)
            if not review:
                return None
            
            # Update content status based on review
            try:
                import json
                review_data = json.loads(review)
                if review_data.get("decision") == "APPROVE":
                    content.status = "approved"
                    content.editor_agent_id = self.agent_id
                else:
                    content.status = "needs_revision"
                    
                db.commit()
                
                await self._log_audit("review_content", "SUCCESS", {
                    "content_id": content_id,
                    "decision": review_data.get("decision")
                }, True)
                
                return {
                    "content_id": content_id,
                    "review": review_data,
                    "new_status": content.status
                }
                
            except json.JSONDecodeError:
                return None
                
        finally:
            db.close()

class ReviewerAgent(BaseAgent):
    """Agent specialized for final review and publishing"""
    
    async def final_review(self, content_id: int) -> Optional[Dict[str, Any]]:
        """Perform final review for publishing"""
        if not self.has_capability("workflow.publish"):
            await self._log_audit("final_review", "DENIED", {"content_id": content_id}, False)
            return None
        
        db = SessionLocal()
        try:
            content = db.query(ContentItem).filter(ContentItem.id == content_id).first()
            if not content or content.status != "approved":
                return None
            
            # Final quality check
            prompt = f"""
            Perform final publication readiness check:
            
            Title: {content.title}
            Content: {content.content}
            
            Check for:
            1. Grammar and spelling
            2. Factual accuracy
            3. Legal/compliance issues
            4. Brand consistency
            
            Decision: PUBLISH or REJECT
            Provide brief reasoning.
            
            Format as JSON with keys: decision, reasoning
            """
            
            review = await self.call_gemini_api(prompt, max_tokens=300)
            if not review:
                return None
            
            try:
                import json
                review_data = json.loads(review)
                if review_data.get("decision") == "PUBLISH":
                    content.status = "published"
                    content.reviewer_agent_id = self.agent_id
                else:
                    content.status = "rejected"
                    
                db.commit()
                
                await self._log_audit("final_review", "SUCCESS", {
                    "content_id": content_id,
                    "decision": review_data.get("decision")
                }, True)
                
                return {
                    "content_id": content_id,
                    "decision": review_data.get("decision"),
                    "reasoning": review_data.get("reasoning"),
                    "final_status": content.status
                }
                
            except json.JSONDecodeError:
                return None
                
        finally:
            db.close()

class CoordinatorAgent(BaseAgent):
    """Agent that orchestrates the content creation workflow"""
    
    async def assign_content_task(self, topic: str, priority: str = "normal") -> Optional[Dict[str, Any]]:
        """Assign content creation task to writer agent"""
        if not self.has_capability("workflow.assign"):
            await self._log_audit("assign_task", "DENIED", {"topic": topic}, False)
            return None
        
        # Find available writer agent
        db = SessionLocal()
        try:
            writer = db.query(Agent).filter(
                Agent.agent_type == "writer",
                Agent.status == "active"
            ).first()
            
            if not writer:
                return None
            
            # Send task assignment message
            task_message = f"""
            Content Assignment:
            Topic: {topic}
            Priority: {priority}
            
            Please create a comprehensive article on this topic.
            """
            
            success = await self.send_message(
                writer.id,
                task_message,
                "task_assignment"
            )
            
            if success:
                await self._log_audit("assign_task", "SUCCESS", {
                    "topic": topic,
                    "writer_id": writer.id
                }, True)
                
                return {
                    "assigned_to": writer.name,
                    "topic": topic,
                    "priority": priority
                }
            
            return None
            
        finally:
            db.close()
