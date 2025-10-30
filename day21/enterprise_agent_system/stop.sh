#!/bin/bash

echo "🛑 Stopping Enterprise Multi-Agent System..."

# Kill all Python processes for this app
pkill -f "uvicorn app.main:app"

# Kill all Node.js processes for this app
pkill -f "react-scripts start"

echo "✅ System stopped successfully!"
