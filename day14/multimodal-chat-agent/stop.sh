#!/bin/bash

echo "🛑 Stopping Multi-Modal Chat Agent..."

# Kill all related processes
pkill -f "python src/simple_main.py"
pkill -f "npm start"
pkill -f "uvicorn"
pkill -f "react-scripts"

echo "✅ All services stopped"
