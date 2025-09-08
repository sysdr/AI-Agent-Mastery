#!/bin/bash

echo "🚀 Building AI Conversation Manager..."

# Create virtual environment for backend
echo "📦 Setting up Python environment..."
python3 -m venv backend/venv
source backend/venv/bin/activate

# Install backend dependencies
cd backend
pip install --upgrade pip
pip install -r requirements.txt

# Download required models
python -c "
import nltk
nltk.download('punkt')
nltk.download('vader_lexicon')
"

echo "✅ Backend dependencies installed"
cd ..

# Install frontend dependencies
echo "📱 Setting up frontend..."
cd frontend
npm install
echo "✅ Frontend dependencies installed"
cd ..

# Run tests
echo "🧪 Running tests..."
cd backend
source venv/bin/activate
python -m pytest tests/ -v
echo "✅ Tests completed"
cd ..

echo "🎉 Build completed successfully!"
echo "💡 Run ./start.sh to start the application"
