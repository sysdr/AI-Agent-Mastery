#!/bin/bash

echo "🏗️  Building Agent Communication Security System"

# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install backend dependencies
cd backend
pip install -r requirements.txt
cd ..

# Install frontend dependencies
cd frontend
npm install
cd ..

echo "✅ Build completed successfully"
echo "Run ./start.sh to start the system"
