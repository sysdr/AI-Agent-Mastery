#!/bin/bash

echo "🛑 Stopping Enterprise Agent System..."

# Kill backend if running
if [ -f ".backend.pid" ]; then
    BACKEND_PID=$(cat .backend.pid)
    if ps -p $BACKEND_PID > /dev/null; then
        kill $BACKEND_PID
        echo "🔧 Backend stopped (PID: $BACKEND_PID)"
    fi
    rm .backend.pid
fi

# Kill frontend if running
if [ -f ".frontend.pid" ]; then
    FRONTEND_PID=$(cat .frontend.pid)
    if ps -p $FRONTEND_PID > /dev/null; then
        kill $FRONTEND_PID
        echo "🌐 Frontend stopped (PID: $FRONTEND_PID)"
    fi
    rm .frontend.pid
fi

# Kill any remaining processes
pkill -f "uvicorn api:app" 2>/dev/null
pkill -f "npm start" 2>/dev/null
pkill -f "react-scripts start" 2>/dev/null

# Final cleanup
echo "🧹 Performing cleanup..."
if [ -f "backend/logs/agent.log" ]; then
    echo "📊 Final log summary:"
    tail -3 backend/logs/agent.log
fi

echo "✅ System stopped successfully"
echo "💾 Agent state and logs preserved in backend/data/ and backend/logs/"
