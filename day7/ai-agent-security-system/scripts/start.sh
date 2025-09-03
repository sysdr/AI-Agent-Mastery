#!/bin/bash

set -e

echo "🚀 Starting AI Agent Security Assessment System..."

# Load environment variables
if [ -f .env ]; then
    export $(cat .env | grep -v '#' | xargs)
fi

# Start with Docker Compose
if command -v docker-compose &> /dev/null; then
    echo "🐳 Starting with Docker Compose..."
    cd docker
    docker-compose up -d
    cd ..
    
    echo "⏳ Waiting for services to be healthy..."
    sleep 30
    
    echo "✅ Services started!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔌 Backend API: http://localhost:8000"
    echo "📊 API Docs: http://localhost:8000/docs"
else
    echo "🔧 Starting in development mode..."
    
    # Start backend
    echo "🐍 Starting Python backend..."
    source venv/bin/activate
    cd backend
    python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 &
    BACKEND_PID=$!
    cd ..
    
    # Start frontend
    echo "⚛️ Starting React frontend..."
    cd frontend
    npm start &
    FRONTEND_PID=$!
    cd ..
    
    echo "✅ Services started!"
    echo "🌐 Frontend: http://localhost:3000"
    echo "🔌 Backend API: http://localhost:8000"
    
    # Save PIDs for stop script
    echo $BACKEND_PID > backend.pid
    echo $FRONTEND_PID > frontend.pid
fi

echo "🔒 Security Assessment System is running!"
