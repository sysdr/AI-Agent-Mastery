#!/bin/bash
set -e

echo "🏗️  Building Resilient Agent..."

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
npm run build
cd ..

echo "✅ Build completed successfully!"
echo "📝 Next steps:"
echo "   1. Start Redis: redis-server"
echo "   2. Run: ./start.sh"
echo "   3. Open: http://localhost:3000"
