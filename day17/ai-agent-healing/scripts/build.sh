#!/bin/bash

# AI Agent Self-Healing System - Build Script

set -e

echo "🚀 Building AI Agent Self-Healing System..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "📦 Creating Python virtual environment..."
    python -m venv venv
fi

# Activate virtual environment
echo "🔌 Activating virtual environment..."
source venv/bin/activate

# Install backend dependencies
echo "📥 Installing backend dependencies..."
pip install --upgrade pip
pip install -r backend/requirements.txt

# Install frontend dependencies
echo "📥 Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Build frontend
echo "🔨 Building frontend..."
cd frontend
npm run build
cd ..

# Run tests
echo "🧪 Running tests..."
python -m pytest tests/ -v

# Frontend tests
echo "🧪 Running frontend tests..."
cd frontend
npm test -- --watchAll=false --coverage
cd ..

echo "✅ Build completed successfully!"
echo ""
echo "Next steps:"
echo "  1. Set GEMINI_API_KEY environment variable"
echo "  2. Run: ./scripts/start.sh"
echo "  3. Open http://localhost:3000 for frontend"
echo "  4. Open http://localhost:8000 for backend API"
