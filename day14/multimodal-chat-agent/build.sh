#!/bin/bash

echo "🚀 Building Multi-Modal Chat Agent..."

# Create virtual environment
echo "📦 Setting up Python environment..."
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "🎨 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Create required directories
mkdir -p logs uploads

# Set environment variables
export GEMINI_API_KEY="your_gemini_api_key_here"

echo "✅ Build complete!"
echo "Next steps:"
echo "1. Set your GEMINI_API_KEY in backend/.env"
echo "2. Run ./start.sh to start all services"
echo "3. Visit http://localhost:3000 for the chat interface"
