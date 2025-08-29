#!/bin/bash
# Stop script for Secure Document Processing Agent

echo "🛑 Stopping Secure Document Processing Agent..."

# Kill processes
if [ -f backend.pid ]; then
    kill $(cat backend.pid) 2>/dev/null || true
    rm backend.pid
fi

if [ -f frontend.pid ]; then
    kill $(cat frontend.pid) 2>/dev/null || true
    rm frontend.pid
fi

# Kill any remaining processes
pkill -f "uvicorn app.main:app" || true
pkill -f "npm start" || true

echo "✅ Application stopped"
