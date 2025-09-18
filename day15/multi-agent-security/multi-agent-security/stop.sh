#!/bin/bash

echo "🛑 Stopping Multi-Agent Security System"

pkill -f "uvicorn main:app"
pkill -f "npm start"
pkill -f "react-scripts start"

echo "✅ All services stopped"
