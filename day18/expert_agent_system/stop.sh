#!/bin/bash

echo "🛑 Stopping Expert Agent System..."

if [ -f backend.pid ]; then
    kill $(cat backend.pid) 2>/dev/null
    rm backend.pid
fi

if [ -f frontend.pid ]; then
    kill $(cat frontend.pid) 2>/dev/null  
    rm frontend.pid
fi

# Kill any remaining processes
pkill -f "uvicorn app.main:app"
pkill -f "npm start"

echo "✅ All services stopped"
