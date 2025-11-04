#!/bin/bash

echo "Stopping Day 28 DR System..."

if [ -f .backend.pid ]; then
    kill $(cat .backend.pid) 2>/dev/null || true
    rm .backend.pid
fi

if [ -f .frontend.pid ]; then
    kill $(cat .frontend.pid) 2>/dev/null || true
    rm .frontend.pid
fi

# Kill any remaining processes
pkill -f "uvicorn main:app" || true
pkill -f "npm start" || true
pkill -f "react-scripts start" || true

echo "✅ All services stopped"
