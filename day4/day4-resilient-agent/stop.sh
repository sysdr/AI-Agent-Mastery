#!/bin/bash

echo "🛑 Stopping Resilient Agent services..."

# Kill processes by port
pkill -f "uvicorn app.main:app" || true
pkill -f "vite" || true

echo "✅ All services stopped"
