#!/bin/bash
set -e

echo "🚀 Building Day 20: Production Learning & Optimization"

# Create virtual environment
echo "📦 Setting up Python virtual environment..."
python -m venv venv
source venv/bin/activate || source venv/Scripts/activate

# Install backend dependencies
echo "📚 Installing backend dependencies..."
cd backend
pip install --upgrade pip
pip install -r requirements.txt

# Run tests
echo "🧪 Running backend tests..."
python -m pytest tests/ -v

cd ../frontend

# Install frontend dependencies
echo "🎨 Installing frontend dependencies..."
npm install

# Build frontend
echo "🏗️ Building frontend..."
npm run build

cd ..

echo "✅ Build completed successfully!"
echo ""
echo "🚀 Next steps:"
echo "1. Set your GEMINI_API_KEY in backend/.env"
echo "2. Run './start.sh' to start all services"
echo "3. Open http://localhost:3000 to access the dashboard"
