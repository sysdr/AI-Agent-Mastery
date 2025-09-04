#!/bin/bash

set -e

echo "🔧 Setting up Enterprise Chat Agent..."

# Create Python virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "📦 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Start services
echo "🚀 Starting Redis and PostgreSQL with Docker..."
cd docker
docker-compose up -d postgres redis
cd ..

# Wait for services
echo "⏳ Waiting for services to start..."
sleep 10

# Run tests
echo "🧪 Running tests..."
cd backend
python -m pytest ../tests/backend/ -v
cd ..

# Build frontend
echo "🏗️ Building frontend..."
cd frontend
npm run build
cd ..

echo "✅ Build completed successfully!"
echo ""
echo "Next steps:"
echo "1. Set your GEMINI_API_KEY in .env file"
echo "2. Run ./start.sh to start all services"
echo "3. Open http://localhost:3000 to access the application"
