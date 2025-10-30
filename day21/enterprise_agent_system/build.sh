#!/bin/bash

echo "🏗️ Building Enterprise Multi-Agent System..."

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv enterprise_env
source enterprise_env/bin/activate

# Install Python dependencies
echo "🐍 Installing Python dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install Node.js dependencies
echo "⚛️ Installing Node.js dependencies..."
cd frontend
npm install
cd ..

# Build React frontend
echo "🚀 Building React frontend..."
cd frontend
npm run build
cd ..

echo "✅ Build completed successfully!"
echo "📝 Next steps:"
echo "1. Set your Gemini API key in backend/.env"
echo "2. Run ./start.sh to start the system"
echo "3. Access dashboard at http://localhost:3000"
