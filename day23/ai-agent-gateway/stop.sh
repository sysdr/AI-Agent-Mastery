#!/bin/bash

echo "🛑 Stopping AI Gateway Services"
echo "==============================="

# Kill Python processes
pkill -f "python main.py"

# Kill Node processes
pkill -f "react-scripts start"

# Stop Redis
redis-cli shutdown 2>/dev/null || echo "Redis not running"

echo "✅ All services stopped"
