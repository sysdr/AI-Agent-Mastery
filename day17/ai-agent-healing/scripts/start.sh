#!/bin/bash

# AI Agent Self-Healing System - Start Script

set -e

echo "🚀 Starting AI Agent Self-Healing System..."

# Check if GEMINI_API_KEY is set
if [ -z "$GEMINI_API_KEY" ]; then
    echo "⚠️  Warning: GEMINI_API_KEY not set. Using default placeholder."
    export GEMINI_API_KEY="your-gemini-api-key"
fi

# Function to cleanup processes on exit
cleanup() {
    echo ""
    echo "🛑 Shutting down AI Agent Self-Healing System..."
    if [ ! -z "$BACKEND_PID" ]; then
        kill $BACKEND_PID 2>/dev/null || true
    fi
    if [ ! -z "$FRONTEND_PID" ]; then
        kill $FRONTEND_PID 2>/dev/null || true
    fi
    exit 0
}

# Set trap for cleanup
trap cleanup SIGINT SIGTERM

# Start backend
echo "🔧 Starting backend server..."
source venv/bin/activate
cd backend
export PYTHONPATH=$(pwd)
python -m app.main &
BACKEND_PID=$!
cd ..

# Wait for backend to start
echo "⏳ Waiting for backend to start..."
sleep 5

# Check if backend is running
if ! curl -f http://localhost:8000/health > /dev/null 2>&1; then
    echo "❌ Backend failed to start"
    cleanup
    exit 1
fi

echo "✅ Backend started successfully"

# Start frontend
echo "🎨 Starting frontend server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo ""
echo "🎉 AI Agent Self-Healing System is running!"
echo ""
echo "📊 Frontend Dashboard: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📋 API Documentation: http://localhost:8000/docs"
echo "💓 Health Check: http://localhost:8000/health"
echo ""
echo "Press Ctrl+C to stop all services"

# Wait for processes
wait
