#!/bin/bash

echo "🏗️ Building AI Gateway Project"
echo "=============================="

# Create virtual environment
echo "📦 Creating Python virtual environment..."
python3 -m venv gateway-env
source gateway-env/bin/activate

# Install Python dependencies
echo "📚 Installing Python dependencies..."
cd backend
pip install -r requirements.txt
cd ..

# Install Node.js dependencies
echo "📚 Installing Node.js dependencies..."
cd frontend
npm install
cd ..

echo "✅ Build completed successfully!"
echo ""
echo "Next steps:"
echo "1. Run './start.sh' to start all services"
echo "2. Visit http://localhost:3000 for the dashboard"
echo "3. Login with admin/admin123 or user/user123"
