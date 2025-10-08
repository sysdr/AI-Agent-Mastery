#!/bin/bash

# Production Orchestration System - Build Script

set -e

echo "🏗️ Building Production Orchestration System..."

# Create Python virtual environment
echo "📦 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
echo "📥 Installing backend dependencies..."
cd backend
pip install --upgrade pip
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "📥 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Set environment variables
cat > .env << 'ENVEOF'
GEMINI_API_KEY=demo_key
DATABASE_URL=sqlite:///./orchestration.db
REDIS_URL=redis://localhost:6379/0
SECRET_KEY=demo_secret_key_change_in_production
DEBUG=true
ENVEOF

echo "✅ Build completed successfully!"
echo "🚀 Run './start.sh' to start the system"
