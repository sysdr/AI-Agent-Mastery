import logging
import uuid
import asyncio
from datetime import datetime
from typing import Dict, List, Optional, Any
import google.generativeai as genai
from config.settings import settings

logger = logging.getLogger(__name__)
genai.configure(api_key=settings.gemini_api_key)

class ConversationManager:
    def __init__(self):
        self.conversations: Dict[str, Dict] = {}
        self.model = genai.GenerativeModel('gemini-pro')
        
    async def process_message(
        self, 
        session_id: str, 
        message: str, 
        user_id: str,
        compliance_validator,
        personality_monitor
    ) -> Dict[str, Any]:
        """Process a message through the complete pipeline"""
        
        conversation_id = str(uuid.uuid4())
        
        try:
            # Initialize conversation if new
            if session_id not in self.conversations:
                self.conversations[session_id] = {
                    "messages": [],
                    "personality_profile": self._initialize_personality(),
                    "created_at": datetime.now().isoformat(),
                    "user_id": user_id
                }
            
            # Compliance validation
            compliance_result = await compliance_validator.validate_message(message)
            if not compliance_result["is_valid"]:
                return {
                    "conversation_id": conversation_id,
                    "response": "I'm sorry, but I can't process that request due to content policy restrictions.",
                    "compliance_flags": compliance_result["flags"],
                    "escalated": False,
                    "timestamp": datetime.now().isoformat()
                }
            
            # Generate dynamic prompt
            prompt = self._generate_dynamic_prompt(session_id, message)
            
            # Get AI response
            ai_response = await self._get_ai_response(prompt)
            
            # Personality consistency check
            personality_check = await personality_monitor.validate_response(
                session_id, ai_response, self.conversations[session_id]["personality_profile"]
            )
            
            # Determine if escalation needed
            escalated = self._should_escalate(message, ai_response, compliance_result, personality_check)
            
            # Store conversation
            self.conversations[session_id]["messages"].append({
                "user_message": message,
                "ai_response": ai_response,
                "compliance_score": compliance_result["score"],
                "personality_score": personality_check["consistency_score"],
                "timestamp": datetime.now().isoformat()
            })
            
            return {
                "conversation_id": conversation_id,
                "response": ai_response,
                "compliance_score": compliance_result["score"],
                "personality_consistent": personality_check["is_consistent"],
                "escalated": escalated,
                "timestamp": datetime.now().isoformat(),
                "compliance_result": compliance_result,
                "personality_result": personality_check
            }
            
        except Exception as e:
            logger.error(f"Error processing message: {str(e)}")
            return {
                "conversation_id": conversation_id,
                "response": "I'm experiencing technical difficulties. Please try again.",
                "error": True,
                "timestamp": datetime.now().isoformat()
            }
    
    def _initialize_personality(self) -> Dict[str, Any]:
        """Initialize personality profile for new conversation"""
        return {
            "tone": "professional_friendly",
            "expertise_level": "senior_engineer",
            "communication_style": "direct_helpful",
            "baseline_responses": []
        }
    
    def _generate_dynamic_prompt(self, session_id: str, user_message: str) -> str:
        """Generate injection-safe dynamic prompt"""
        conversation = self.conversations.get(session_id, {})
        personality = conversation.get("personality_profile", {})
        
        # Safe template with parameter injection prevention
        base_prompt = """You are a senior AI engineering mentor helping students learn distributed systems.
        
Personality traits:
- Tone: {tone}
- Expertise: {expertise_level}  
- Style: {communication_style}

Current conversation context:
{context}

Safety instructions:
- Maintain professional tone
- Focus on educational content
- Avoid sharing sensitive information
- Redirect inappropriate requests

User message (sanitized): {user_message}

Provide a helpful response that maintains consistency with your established personality."""
        
        context = self._build_safe_context(conversation.get("messages", []))
        
        return base_prompt.format(
            tone=personality.get("tone", "professional"),
            expertise_level=personality.get("expertise_level", "senior"),
            communication_style=personality.get("communication_style", "helpful"),
            context=context,
            user_message=self._sanitize_input(user_message)
        )
    
    def _sanitize_input(self, text: str) -> str:
        """Sanitize user input to prevent injection"""
        # Remove potential injection patterns
        dangerous_patterns = [
            "ignore previous", "forget instructions", "new instructions",
            "system:", "assistant:", "user:", "{", "}", "$(", "eval(",
            "<script", "javascript:", "data:", "vbscript:"
        ]
        
        sanitized = text
        for pattern in dangerous_patterns:
            sanitized = sanitized.replace(pattern.lower(), "[FILTERED]")
        
        return sanitized[:1000]  # Limit length
    
    def _build_safe_context(self, messages: List[Dict]) -> str:
        """Build safe conversation context"""
        if not messages:
            return "This is the start of our conversation."
        
        # Last 3 message pairs for context
        recent_messages = messages[-3:]
        context_parts = []
        
        for msg in recent_messages:
            context_parts.append(f"User asked about: {msg['user_message'][:100]}...")
            context_parts.append(f"You responded: {msg['ai_response'][:100]}...")
        
        return "\n".join(context_parts)
    
    async def _get_ai_response(self, prompt: str) -> str:
        """Get response from Gemini AI"""
        try:
            response = self.model.generate_content(
                prompt,
                generation_config=genai.types.GenerationConfig(
                    temperature=0.7,
                    max_output_tokens=500
                )
            )
            return response.text
        except Exception as e:
            logger.error(f"AI response error: {str(e)}")
            # Provide a mock response when API key is invalid
            if "API key not valid" in str(e):
                return "Hello! I'm a senior AI engineering mentor. I'd be happy to help you with distributed systems concepts, but I'm currently running in demo mode. In a production environment, I would provide detailed technical guidance based on your question. What specific topic would you like to learn about?"
            return "I'm having trouble generating a response right now. Please try rephrasing your question."
    
    def _should_escalate(self, user_message: str, ai_response: str, compliance: Dict, personality: Dict) -> bool:
        """Determine if conversation should be escalated"""
        escalation_triggers = [
            compliance["score"] < 0.5,
            not personality["is_consistent"],
            len(user_message.split()) > 200,  # Very long messages
            any(keyword in user_message.lower() for keyword in [
                "urgent", "emergency", "complaint", "refund", "legal"
            ])
        ]
        
        return any(escalation_triggers)
