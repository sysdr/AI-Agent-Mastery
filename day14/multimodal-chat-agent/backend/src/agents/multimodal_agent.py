"""
Multi-Modal Chat Agent
Handles text, image, and document processing with Gemini AI
"""

import asyncio
import io
import os
import base64
from typing import Dict, Any, Optional
import structlog
import google.generativeai as genai
from PIL import Image
import PyPDF2
import docx
from utils.redis_client import RedisClient
from models.schemas import ChatResponse

logger = structlog.get_logger()

class MultiModalAgent:
    def __init__(self):
        """Initialize multimodal agent with Gemini AI"""
        genai.configure(api_key=os.getenv("GEMINI_API_KEY"))
        self.model = genai.GenerativeModel('gemini-pro')
        self.vision_model = genai.GenerativeModel('gemini-pro-vision')
        self.redis_client = RedisClient()
        
    async def process_message(
        self, 
        content: str, 
        user_id: str, 
        conversation_id: Optional[str] = None
    ) -> ChatResponse:
        """Process text message with conversation context"""
        try:
            # Get conversation history
            history = await self._get_conversation_history(conversation_id) if conversation_id else []
            
            # Generate response
            response = await self._generate_text_response(content, history)
            
            # Store in conversation history
            if conversation_id:
                await self._store_conversation_turn(conversation_id, content, response)
            
            # Count tokens (approximation)
            tokens_used = len(content.split()) + len(response.split())
            
            return ChatResponse(
                content=response,
                conversation_id=conversation_id or f"conv_{user_id}_{asyncio.get_event_loop().time()}",
                tokens_used=tokens_used,
                model_used="gemini-pro"
            )
            
        except Exception as e:
            logger.error("Text processing error", error=str(e))
            raise

    async def process_file_message(
        self,
        file,
        message: str,
        user_id: str
    ) -> ChatResponse:
        """Process file upload with message"""
        try:
            file_content = await file.read()
            file_type = file.content_type
            
            if file_type.startswith('image/'):
                response = await self._process_image(file_content, message)
            elif file_type == 'application/pdf':
                response = await self._process_pdf(file_content, message)
            elif file_type.startswith('application/vnd.openxmlformats-officedocument'):
                response = await self._process_docx(file_content, message)
            else:
                response = f"Unsupported file type: {file_type}"
            
            tokens_used = len(message.split()) + len(response.split()) + 100  # File processing overhead
            
            return ChatResponse(
                content=response,
                conversation_id=f"file_{user_id}_{asyncio.get_event_loop().time()}",
                tokens_used=tokens_used,
                model_used="gemini-pro-vision" if file_type.startswith('image/') else "gemini-pro"
            )
            
        except Exception as e:
            logger.error("File processing error", error=str(e))
            raise

    async def _generate_text_response(self, content: str, history: list) -> str:
        """Generate text response using Gemini"""
        try:
            # Build prompt with history
            prompt = self._build_prompt_with_history(content, history)
            
            response = await asyncio.get_event_loop().run_in_executor(
                None, 
                lambda: self.model.generate_content(prompt)
            )
            
            return response.text
            
        except Exception as e:
            logger.error("Text generation error", error=str(e))
            return "I apologize, but I encountered an error processing your request."

    async def _process_image(self, image_data: bytes, message: str) -> str:
        """Process image with vision model"""
        try:
            # Convert bytes to PIL Image
            image = Image.open(io.BytesIO(image_data))
            
            # Prepare prompt
            prompt = f"Analyze this image and respond to: {message}" if message else "Describe this image in detail."
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.vision_model.generate_content([prompt, image])
            )
            
            return response.text
            
        except Exception as e:
            logger.error("Image processing error", error=str(e))
            return "Error processing image."

    async def _process_pdf(self, pdf_data: bytes, message: str) -> str:
        """Extract text from PDF and process"""
        try:
            pdf_reader = PyPDF2.PdfReader(io.BytesIO(pdf_data))
            text_content = ""
            
            for page in pdf_reader.pages:
                text_content += page.extract_text() + "\n"
            
            # Truncate if too long
            if len(text_content) > 10000:
                text_content = text_content[:10000] + "... (truncated)"
            
            prompt = f"Based on this PDF content:\n\n{text_content}\n\nPlease respond to: {message}"
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.model.generate_content(prompt)
            )
            
            return response.text
            
        except Exception as e:
            logger.error("PDF processing error", error=str(e))
            return "Error processing PDF document."

    async def _process_docx(self, docx_data: bytes, message: str) -> str:
        """Extract text from DOCX and process"""
        try:
            doc = docx.Document(io.BytesIO(docx_data))
            text_content = "\n".join([paragraph.text for paragraph in doc.paragraphs])
            
            # Truncate if too long
            if len(text_content) > 10000:
                text_content = text_content[:10000] + "... (truncated)"
            
            prompt = f"Based on this document content:\n\n{text_content}\n\nPlease respond to: {message}"
            
            response = await asyncio.get_event_loop().run_in_executor(
                None,
                lambda: self.model.generate_content(prompt)
            )
            
            return response.text
            
        except Exception as e:
            logger.error("DOCX processing error", error=str(e))
            return "Error processing Word document."

    def _build_prompt_with_history(self, content: str, history: list) -> str:
        """Build prompt with conversation history"""
        if not history:
            return content
        
        prompt = "Previous conversation:\n"
        for turn in history[-5:]:  # Last 5 turns
            prompt += f"User: {turn['user']}\nAssistant: {turn['assistant']}\n\n"
        
        prompt += f"Current message: {content}"
        return prompt

    async def _get_conversation_history(self, conversation_id: str) -> list:
        """Get conversation history from Redis"""
        try:
            history = await self.redis_client.get(f"conv_history:{conversation_id}")
            return history or []
        except:
            return []

    async def _store_conversation_turn(self, conversation_id: str, user_message: str, assistant_response: str):
        """Store conversation turn in Redis"""
        try:
            history = await self._get_conversation_history(conversation_id)
            history.append({
                "user": user_message,
                "assistant": assistant_response,
                "timestamp": asyncio.get_event_loop().time()
            })
            
            # Keep only last 20 turns
            history = history[-20:]
            
            await self.redis_client.set(
                f"conv_history:{conversation_id}",
                history,
                expire=3600  # 1 hour
            )
        except Exception as e:
            logger.error("Conversation storage error", error=str(e))
