#!/bin/bash
echo "🛑 Stopping all services..."

# Kill processes by name
pkill -f "uvicorn app.main:app"
pkill -f "react-scripts"
pkill -f "node.*react-scripts"

# Kill processes by port
lsof -ti:8000 | xargs kill -9 2>/dev/null
lsof -ti:3000 | xargs kill -9 2>/dev/null

echo "✅ All services stopped"
echo ""
echo "⏳ Waiting 3 seconds..."
sleep 3
echo ""
echo "🚀 Starting fresh..."
./start.sh


