#!/bin/bash

# Production Orchestration System - Start Script

set -e

echo "🚀 Starting Production Orchestration System..."

# Check if built
if [ ! -d "venv" ]; then
    echo "❌ System not built. Run './build.sh' first"
    exit 1
fi

# Activate virtual environment
source venv/bin/activate

# Start backend in background
echo "🔧 Starting backend server..."
cd backend/src
python main.py &
BACKEND_PID=$!
cd ../..

# Start frontend in background  
echo "🎨 Starting frontend server..."
cd frontend
npm start &
FRONTEND_PID=$!
cd ..

# Save PIDs for cleanup
echo $BACKEND_PID > backend.pid
echo $FRONTEND_PID > frontend.pid

echo "✅ System started successfully!"
echo "🌐 Frontend: http://localhost:3000"
echo "🔧 Backend API: http://localhost:8000"
echo "📊 API Docs: http://localhost:8000/docs"
echo ""
echo "🛑 Run './stop.sh' to stop the system"

# Keep script running
wait
