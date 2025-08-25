#!/bin/bash

echo "🚀 Starting Secure Memory Agent System"
echo "======================================"

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python3 -m venv venv
else
    echo "📦 Using existing Python virtual environment..."
fi

# Activate virtual environment
source venv/bin/activate

# Check if dependencies are already installed
if [ ! -f "venv/.dependencies_installed" ]; then
    echo "📥 Installing Python dependencies..."
    pip install --upgrade pip
    pip install -r backend/requirements.txt
    
    # Download spaCy model for PII detection
    echo "🧠 Downloading spaCy NLP model..."
    python -m spacy download en_core_web_sm
    
    # Mark dependencies as installed
    touch venv/.dependencies_installed
    echo "✅ Dependencies installed successfully!"
else
    echo "📥 Dependencies already installed, skipping..."
fi

# Create log directory
mkdir -p logs

# Start backend
echo "🔧 Starting FastAPI backend..."
cd backend && PYTHONPATH=$PYTHONPATH:. uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 5

# Check if frontend dependencies exist
if [ ! -d "frontend/node_modules" ]; then
    echo "📦 Installing frontend dependencies..."
    cd frontend && npm install
    cd ..
else
    echo "📦 Frontend dependencies already installed, skipping..."
fi

# Start frontend
echo "🎨 Starting React frontend..."
cd frontend && npm run dev &
FRONTEND_PID=$!
cd ..

# Save PIDs for cleanup
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

echo "✅ System started successfully!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔗 Backend API: http://localhost:8000"
echo "📚 API Docs: http://localhost:8000/docs"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for user interrupt
trap 'echo "🛑 Stopping services..."; kill $BACKEND_PID $FRONTEND_PID; exit' INT
wait
