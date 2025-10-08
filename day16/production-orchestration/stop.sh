#!/bin/bash

# Production Orchestration System - Stop Script

echo "🛑 Stopping Production Orchestration System..."

# Stop backend
if [ -f backend.pid ]; then
    BACKEND_PID=$(cat backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo "🔧 Stopping backend server..."
        kill $BACKEND_PID
    fi
    rm backend.pid
fi

# Stop frontend
if [ -f frontend.pid ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo "🎨 Stopping frontend server..."
        kill $FRONTEND_PID
    fi
    rm frontend.pid
fi

# Kill any remaining processes
pkill -f "python main.py" 2>/dev/null || true
pkill -f "npm start" 2>/dev/null || true

echo "✅ System stopped successfully!"
