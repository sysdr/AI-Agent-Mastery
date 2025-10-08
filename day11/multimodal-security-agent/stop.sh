#!/bin/bash

echo "🛑 Stopping Multi-Modal Security Agent..."

# Kill backend processes
pkill -f "uvicorn app.main:app"

# Kill frontend processes  
pkill -f "vite"

echo "✅ All services stopped"
