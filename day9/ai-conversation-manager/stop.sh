#!/bin/bash

echo "🛑 Stopping AI Conversation Manager..."

# Stop backend and frontend processes
pkill -f "uvicorn app.main:app"
pkill -f "npm start"
pkill -f "react-scripts start"

# Stop Redis
pkill -f redis-server

echo "✅ All services stopped"
