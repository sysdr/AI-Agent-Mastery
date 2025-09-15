#!/bin/bash

echo "🛑 Stopping Advanced Tool Orchestration System"

# Kill all processes
pkill -f "python app/main.py"
pkill -f "npm start"
pkill -f "react-scripts"

echo "✅ System stopped!"
