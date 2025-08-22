import asyncio
import uuid
import json
import structlog
from datetime import datetime
from typing import Dict, Any, Optional
from pathlib import Path
from cryptography.fernet import Fernet
from sqlalchemy.ext.asyncio import create_async_engine, AsyncSession
from sqlalchemy.orm import sessionmaker
from sqlalchemy import Column, String, DateTime, Text, create_engine
from sqlalchemy.orm import declarative_base
import google.generativeai as genai

from utils.encryption import EncryptionManager
from utils.logger import get_logger
from config.settings import settings

Base = declarative_base()

class AgentState(Base):
    __tablename__ = "agent_states"
    
    id = Column(String, primary_key=True)
    session_id = Column(String, nullable=False)
    encrypted_data = Column(Text, nullable=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

class AgentCore:
    def __init__(self):
        self.agent_id = str(uuid.uuid4())
        self.session_id = str(uuid.uuid4())
        self.state = {}
        self.is_running = False
        self.logger = get_logger(__name__)
        self.encryption_manager = EncryptionManager()
        self.engine = None
        self.session_factory = None
        
        # Configure Gemini
        genai.configure(api_key=settings.gemini_api_key)
        self.model = genai.GenerativeModel('gemini-pro')
        
    async def initialize(self) -> bool:
        """Initialize agent with proper setup and validation"""
        try:
            self.logger.info("Agent initialization started", agent_id=self.agent_id)
            
            # Initialize database
            await self._setup_database()
            
            # Load previous state if exists
            await self._load_state()
            
            # Validate configuration
            await self._validate_config()
            
            self.is_running = True
            self.logger.info("Agent initialization completed successfully", 
                           agent_id=self.agent_id, session_id=self.session_id)
            return True
            
        except Exception as e:
            self.logger.error("Agent initialization failed", error=str(e))
            await self._handle_critical_error("Initialization failed", e)
            return False
    
    async def _setup_database(self):
        """Setup SQLite database with async support"""
        db_url = f"sqlite+aiosqlite:///{settings.db_path}"
        self.engine = create_async_engine(db_url, echo=settings.debug)
        self.session_factory = sessionmaker(
            self.engine, class_=AsyncSession, expire_on_commit=False
        )
        
        # Create tables
        async with self.engine.begin() as conn:
            await conn.run_sync(Base.metadata.create_all)
    
    async def _load_state(self):
        """Load encrypted state from database"""
        try:
            async with self.session_factory() as session:
                result = await session.get(AgentState, self.agent_id)
                if result:
                    decrypted_data = self.encryption_manager.decrypt(result.encrypted_data)
                    self.state = json.loads(decrypted_data)
                    self.logger.info("State loaded successfully", 
                                   state_keys=list(self.state.keys()))
        except Exception as e:
            self.logger.warning("Failed to load previous state", error=str(e))
            self.state = {}
    
    async def _validate_config(self):
        """Validate agent configuration"""
        if not settings.gemini_api_key or settings.gemini_api_key == "your-api-key-here":
            raise ValueError("Gemini API key not configured")
        
        # Test API connection
        try:
            response = await self._generate_response("Test connection")
            self.logger.info("API validation successful")
        except Exception as e:
            raise ValueError(f"API validation failed: {e}")
    
    async def process_request(self, message: str, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """Process user request with error handling and state management"""
        request_id = str(uuid.uuid4())
        
        try:
            self.logger.info("Processing request", request_id=request_id, message=message[:100])
            
            if not self.is_running:
                raise RuntimeError("Agent not initialized")
            
            # Update context in state
            if context:
                self.state.update(context)
            
            # Generate AI response
            response = await self._generate_response(message)
            
            # Update state with interaction
            await self._update_state({
                'last_request': message,
                'last_response': response,
                'last_interaction': datetime.utcnow().isoformat(),
                'request_count': self.state.get('request_count', 0) + 1
            })
            
            result = {
                'request_id': request_id,
                'response': response,
                'status': 'success',
                'timestamp': datetime.utcnow().isoformat()
            }
            
            self.logger.info("Request processed successfully", request_id=request_id)
            return result
            
        except Exception as e:
            error_result = await self._handle_processing_error(request_id, message, e)
            return error_result
    
    async def _generate_response(self, message: str) -> str:
        """Generate AI response using Gemini"""
        try:
            # Add context from state
            context_prompt = ""
            if self.state.get('conversation_history'):
                context_prompt = f"Previous context: {self.state['conversation_history'][-3:]}\n\n"
            
            full_prompt = f"{context_prompt}User: {message}\n\nProvide a helpful response:"
            
            response = self.model.generate_content(full_prompt)
            return response.text
            
        except Exception as e:
            self.logger.error("AI generation failed", error=str(e))
            return "I apologize, but I'm experiencing technical difficulties. Please try again."
    
    async def _update_state(self, updates: Dict[str, Any]):
        """Update and persist agent state"""
        try:
            self.state.update(updates)
            
            # Encrypt and store state
            encrypted_data = self.encryption_manager.encrypt(json.dumps(self.state))
            
            async with self.session_factory() as session:
                state_record = await session.get(AgentState, self.agent_id)
                if state_record:
                    state_record.encrypted_data = encrypted_data
                    state_record.updated_at = datetime.utcnow()
                else:
                    state_record = AgentState(
                        id=self.agent_id,
                        session_id=self.session_id,
                        encrypted_data=encrypted_data
                    )
                    session.add(state_record)
                
                await session.commit()
                
        except Exception as e:
            self.logger.error("State update failed", error=str(e))
    
    async def _handle_processing_error(self, request_id: str, message: str, error: Exception) -> Dict[str, Any]:
        """Handle processing errors with proper logging and recovery"""
        self.logger.error("Request processing failed", 
                         request_id=request_id, error=str(error), message=message[:50])
        
        # Attempt graceful degradation
        fallback_response = "I encountered an error processing your request. Please try rephrasing or try again later."
        
        return {
            'request_id': request_id,
            'response': fallback_response,
            'status': 'error',
            'error_type': type(error).__name__,
            'timestamp': datetime.utcnow().isoformat()
        }
    
    async def _handle_critical_error(self, context: str, error: Exception):
        """Handle critical errors that affect agent stability"""
        self.logger.critical("Critical error occurred", 
                           context=context, error=str(error), agent_id=self.agent_id)
        
        # In production, this would trigger alerts
        # For now, we log and attempt graceful degradation
        self.is_running = False
    
    async def get_status(self) -> Dict[str, Any]:
        """Get current agent status and health metrics"""
        return {
            'agent_id': self.agent_id,
            'session_id': self.session_id,
            'is_running': self.is_running,
            'uptime': datetime.utcnow().isoformat(),
            'state_keys': list(self.state.keys()),
            'request_count': self.state.get('request_count', 0),
            'last_interaction': self.state.get('last_interaction'),
            'health': 'healthy' if self.is_running else 'unhealthy'
        }
    
    async def cleanup(self):
        """Perform graceful cleanup and resource release"""
        try:
            self.logger.info("Starting agent cleanup", agent_id=self.agent_id)
            
            # Save final state
            await self._update_state({
                'shutdown_time': datetime.utcnow().isoformat(),
                'clean_shutdown': True
            })
            
            # Close database connections
            if self.engine:
                await self.engine.dispose()
            
            self.logger.info("Agent cleanup completed successfully")
            
        except Exception as e:
            self.logger.error("Cleanup failed", error=str(e))
        finally:
            # Always ensure agent is marked as not running
            self.is_running = False
