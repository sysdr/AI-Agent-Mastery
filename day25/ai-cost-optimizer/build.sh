#!/bin/bash
# AI Cost Optimizer - Build Script

set -e

echo "🔧 Building AI Agent Cost Optimization Platform..."

# Check if virtual environment exists, create if not
if [ ! -d "venv" ]; then
    echo "Creating Python virtual environment..."
    python3 -m venv venv
fi

# Activate virtual environment
source venv/bin/activate

# Install backend dependencies
echo "Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "Installing frontend dependencies..."
cd frontend
npm install
cd ..

# Build frontend
echo "Building frontend..."
cd frontend
npm run build
cd ..

# Run tests
echo "Running backend tests..."
cd backend
# Ensure imports like `from backend.app...` resolve by including project root
PYTHONPATH="$(pwd)/.." python -m pytest tests/ -v
cd ..

# Run frontend tests
echo "Running frontend tests..."
cd frontend
npm test -- --coverage --watchAll=false --passWithNoTests
cd ..

echo "✅ Build completed successfully!"
echo ""
echo "Next steps:"
echo "1. Set GEMINI_API_KEY environment variable"
echo "2. Start Redis: redis-server"
echo "3. Run ./start.sh to start the application"
