#!/bin/bash

set -e
echo "🚀 Starting Distributed Agent Networks..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run './build.sh' first."
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Start backend server
echo "🐍 Starting Python backend server..."
cd backend
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload &
BACKEND_PID=$!
cd ..

# Wait for backend to start
sleep 3

# Start frontend development server
echo "⚛️ Starting React frontend..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

echo "✅ All services started!"
echo "📋 Services running:"
echo "   Backend API: http://localhost:8000"
echo "   Frontend UI: http://localhost:3000"
echo "   WebSocket: ws://localhost:8000/ws/dashboard"
echo ""
echo "🛑 To stop all services, run './stop.sh' or press Ctrl+C"

# Store PIDs for cleanup
echo $BACKEND_PID > .backend.pid
echo $FRONTEND_PID > .frontend.pid

# Wait for interrupt
trap 'kill $BACKEND_PID $FRONTEND_PID 2>/dev/null; exit' INT TERM
wait
