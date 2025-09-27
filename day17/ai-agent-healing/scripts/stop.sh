#!/bin/bash

# AI Agent Self-Healing System - Stop Script

echo "🛑 Stopping AI Agent Self-Healing System..."

# Kill backend processes
pkill -f "python -m app.main" || true
pkill -f "uvicorn" || true

# Kill frontend processes
pkill -f "react-scripts start" || true
pkill -f "npm start" || true

# Kill any remaining processes on ports 8000 and 3000
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:3000 | xargs kill -9 2>/dev/null || true

echo "✅ All services stopped"
