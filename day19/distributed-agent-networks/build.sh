#!/bin/bash

set -e
echo "🏗️ Building Distributed Agent Networks Project..."

# Create virtual environment
echo "📦 Setting up Python virtual environment..."
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
echo "🐍 Installing Python dependencies..."
cd backend
pip install --upgrade pip
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "⚛️ Installing React dependencies..."
cd frontend
npm install
cd ..

# Run backend tests
echo "🧪 Running backend tests..."
source venv/bin/activate
cd backend
python -m pytest tests/ -v
cd ..

# Build frontend
echo "📦 Building React frontend..."
cd frontend
npm run build
cd ..

echo "✅ Build completed successfully!"
echo "📋 Next steps:"
echo "   1. Run './start.sh' to start all services"
echo "   2. Open http://localhost:3000 in your browser"
echo "   3. Watch the distributed agents collaborate in real-time!"
