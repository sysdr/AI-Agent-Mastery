from fastapi import FastAPI, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse
import google.generativeai as genai
import os
from datetime import datetime
from .api.learning_routes import router as learning_router
from .models.learning import Base
from .models.user import Base as UserBase
from .utils.database import engine

# Configure Gemini AI (with fallback)
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# We'll try Gemini if API key exists, but always have fallback ready
if GEMINI_API_KEY and len(GEMINI_API_KEY) > 20:
    try:
        genai.configure(api_key=GEMINI_API_KEY)
        print("ℹ️  Gemini API key configured. Will try Gemini first, with fallback available.")
    except Exception as e:
        print(f"⚠️  Gemini configuration warning: {e}")
else:
    print("ℹ️  No GEMINI_API_KEY found. Using fallback chatbot only.")

# Create database tables
Base.metadata.create_all(bind=engine)
UserBase.metadata.create_all(bind=engine)

app = FastAPI(
    title="Production Learning & Optimization API",
    description="Day 20: AI Agent Production Learning System",
    version="1.0.0"
)

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:3000", "http://127.0.0.1:3000"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include routers
app.include_router(learning_router, prefix="/api/learning", tags=["learning"])

@app.get("/")
async def root():
    return {
        "message": "Production Learning & Optimization API",
        "version": "1.0.0",
        "day": "20",
        "topic": "Online learning with bias detection and privacy protection"
    }

def fallback_chatbot(message: str) -> str:
    """Simple rule-based fallback chatbot when Gemini is unavailable"""
    message_lower = message.lower()
    
    # Greetings
    if any(word in message_lower for word in ['hello', 'hi', 'hey', 'greetings']):
        return "Hello! I'm a production learning AI agent. I'm currently running in fallback mode. How can I assist you today?"
    
    # Date/Time queries
    if any(word in message_lower for word in ['date', 'today', 'time', 'day']):
        now = datetime.utcnow()
        return f"Today is {now.strftime('%A, %B %d, %Y')}. The current UTC time is {now.strftime('%H:%M:%S')}."
    
    # System information
    if any(word in message_lower for word in ['what are you', 'who are you', 'about']):
        return "I'm an AI agent in a production learning system designed to provide helpful responses while monitoring for bias and fairness. I'm currently running in fallback mode (without external AI API)."
    
    # Bias/Learning queries
    if any(word in message_lower for word in ['bias', 'fairness', 'learning']):
        return "This system implements online learning with bias detection and privacy protection. It continuously learns from feedback while maintaining fairness across different user groups."
    
    # Help
    if any(word in message_lower for word in ['help', 'what can you do']):
        return "I can help answer questions about this production learning system, provide information about bias detection, online learning, and general queries. Note: I'm currently in fallback mode."
    
    # Math operations
    if '+' in message or 'plus' in message_lower:
        try:
            parts = message.replace('plus', '+').split('+')
            if len(parts) == 2:
                result = float(parts[0].strip()) + float(parts[1].strip())
                return f"The sum is {result}"
        except:
            pass
    
    # Default response
    return f"I received your message: '{message}'. I'm currently in fallback mode (no external AI API connected). For full AI capabilities, please configure a valid GEMINI_API_KEY. I can still answer basic questions about dates, greetings, and system information!"

@app.get("/api/agent/chat")
async def chat_with_agent(message: str, user_id: str = "demo_user"):
    """Chat with AI agent (uses Gemini AI with fallback)"""
    # Try Gemini first if API key is configured
    if GEMINI_API_KEY and len(GEMINI_API_KEY) > 20:
        try:
            model = genai.GenerativeModel('gemini-pro')
            
            # Add context about production learning
            system_prompt = """You are an AI agent in a production learning system. 
            Provide helpful responses while being mindful of bias and fairness. 
            Your responses will be analyzed for bias detection and used for online learning."""
            
            response = model.generate_content(f"{system_prompt}\n\nUser: {message}")
            
            return {
                "response": response.text,
                "agent_id": "production-agent-v1-gemini",
                "response_id": f"resp_{hash(message + user_id) % 10000}",
                "timestamp": datetime.utcnow().isoformat(),
                "mode": "gemini"
            }
        except Exception as gemini_error:
            print(f"Gemini API error: {gemini_error}. Using fallback chatbot.")
            # Fall through to fallback below
    
    # Use fallback chatbot (either no API key or Gemini failed)
    response_text = fallback_chatbot(message)
    
    return {
        "response": response_text,
        "agent_id": "production-agent-v1-fallback",
        "response_id": f"resp_{hash(message + user_id) % 10000}",
        "timestamp": datetime.utcnow().isoformat(),
        "mode": "fallback",
        "note": "Using rule-based fallback. Configure valid GEMINI_API_KEY for full AI capabilities."
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=8000)
