import google.generativeai as genai
from typing import List, Dict, Any, Optional
import structlog
from config.settings import Settings
import asyncio
import json

logger = structlog.get_logger()
settings = Settings()

class GeminiService:
    def __init__(self):
        if settings.gemini_api_key:
            genai.configure(api_key=settings.gemini_api_key)
            self.model = genai.GenerativeModel('gemini-pro')
        else:
            logger.warning("Gemini API key not configured")
            self.model = None
    
    async def generate_response(
        self, 
        messages: List[Dict[str, Any]], 
        tenant_config: Dict[str, Any]
    ) -> str:
        """Generate AI response using Gemini"""
        try:
            if not self.model:
                return "AI service not configured. Please provide GEMINI_API_KEY."
            
            # Format conversation for Gemini
            conversation_text = self._format_conversation(messages)
            
            # Add system context based on tenant configuration
            system_prompt = self._build_system_prompt(tenant_config)
            full_prompt = f"{system_prompt}\n\nConversation:\n{conversation_text}\n\nAssistant:"
            
            # Generate response
            response = await asyncio.create_task(
                self._generate_async(full_prompt)
            )
            
            return response
            
        except Exception as e:
            logger.error("Gemini generation error", error=str(e))
            return "I apologize, but I'm experiencing technical difficulties. Please try again."
    
    async def _generate_async(self, prompt: str) -> str:
        """Async wrapper for Gemini generation"""
        try:
            response = self.model.generate_content(prompt)
            return response.text
        except Exception as e:
            logger.error("Gemini API error", error=str(e))
            raise e
    
    def _format_conversation(self, messages: List[Dict[str, Any]]) -> str:
        """Format conversation messages for Gemini"""
        formatted = []
        
        for msg in messages[-10:]:  # Keep last 10 messages for context
            role = msg.get("role", "user")
            content = msg.get("content", "")
            
            if role == "user":
                formatted.append(f"User: {content}")
            elif role == "assistant":
                formatted.append(f"Assistant: {content}")
        
        return "\n".join(formatted)
    
    def _build_system_prompt(self, tenant_config: Dict[str, Any]) -> str:
        """Build system prompt based on tenant configuration"""
        base_prompt = """You are a helpful customer support assistant. 
Provide accurate, professional, and empathetic responses to customer inquiries."""
        
        # Add tenant-specific customizations
        if tenant_config.get("brand_name"):
            base_prompt += f" You represent {tenant_config['brand_name']}."
        
        if tenant_config.get("response_tone"):
            base_prompt += f" Use a {tenant_config['response_tone']} tone."
        
        if tenant_config.get("compliance_requirements"):
            base_prompt += f" Follow these compliance requirements: {tenant_config['compliance_requirements']}"
        
        return base_prompt
