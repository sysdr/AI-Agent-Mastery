#!/bin/bash
# AI Cost Optimizer - Stop Script

echo "🛑 Stopping AI Agent Cost Optimization Platform..."

# Kill backend processes
pkill -f "uvicorn app.main:app" || true

# Kill frontend processes  
pkill -f "react-scripts start" || true
pkill -f "node.*react-scripts" || true

# Stop Redis
redis-cli shutdown 2>/dev/null || true

# Kill any remaining processes on our ports
lsof -ti:3000 | xargs kill -9 2>/dev/null || true
lsof -ti:8000 | xargs kill -9 2>/dev/null || true
lsof -ti:6379 | xargs kill -9 2>/dev/null || true

echo "✅ All services stopped"
