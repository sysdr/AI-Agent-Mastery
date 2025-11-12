#!/bin/bash

echo "🛑 Stopping Enterprise Integration Platform..."

# Kill backend
if [ -f backend.pid ]; then
    kill $(cat backend.pid) 2>/dev/null
    rm backend.pid
fi

# Kill frontend
if [ -f frontend.pid ]; then
    kill $(cat frontend.pid) 2>/dev/null
    rm frontend.pid
fi

# Kill any remaining processes
pkill -f "uvicorn app.main:app"
pkill -f "vite"

echo "✅ All services stopped"
