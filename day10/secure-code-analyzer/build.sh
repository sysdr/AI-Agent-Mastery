#!/bin/bash

echo "🏗️  Building Secure Code Analysis Agent..."

# Create and activate virtual environment
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

echo "✅ Build completed successfully!"
echo ""
echo "Next steps:"
echo "1. Set your Gemini API key in backend/.env"
echo "2. Run './start.sh' to start the application"
echo "3. Visit http://localhost:3000 for the dashboard"
