#!/bin/bash
set -e

echo "🚀 Building AI Agent Learning & Compliance System"
echo "================================================"

# Create Python virtual environment
echo "📦 Creating virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
echo "📦 Installing Python dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install Node.js dependencies
echo "📦 Installing Node.js dependencies..."
cd frontend
npm install
cd ..

# Start services
echo "🚀 Starting services..."
docker-compose up -d postgres redis

# Wait for services to be ready
echo "⏳ Waiting for services..."
sleep 10

# Run tests
echo "🧪 Running tests..."
cd backend
export PYTHONPATH=$(pwd)
python -m pytest ../tests/ -v
cd ..

# Build frontend
echo "🏗️ Building frontend..."
cd frontend
npm run build
cd ..

echo "✅ Build completed successfully!"
echo "Run './start.sh' to start the application"
