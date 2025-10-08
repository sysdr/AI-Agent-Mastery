#!/bin/bash

set -e

echo "🔧 Building Expert Agent System..."

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

# Initialize database
cd backend
python init_db.py
cd ..

echo "✅ Build completed successfully!"
echo "Next steps:"
echo "1. Set your GEMINI_API_KEY in backend/.env"
echo "2. Run './start.sh' to start the system"
