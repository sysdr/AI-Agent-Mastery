#!/bin/bash
echo "🏗️ Building AI Agent Observability Platform..."

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
echo "📦 Installing backend dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
echo "🎨 Installing frontend dependencies..."
cd frontend
npm install
npm run build
cd ..

# Run tests
echo "🧪 Running tests..."
cd backend
python -m pytest tests/ -v
cd ../frontend
npm test -- --coverage --watchAll=false
cd ..

echo "✅ Build complete!"
echo "🚀 Run './start.sh' to start the application"
