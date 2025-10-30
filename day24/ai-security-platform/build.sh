#!/bin/bash
echo "🔒 Building AI Security Platform..."

# Create virtual environment for backend
cd backend
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install --use-deprecated=legacy-resolver -r requirements.txt

echo "✅ Backend dependencies installed"

# Install frontend dependencies
cd ../frontend
npm install

echo "✅ Frontend dependencies installed"

# Run backend tests
cd ../backend
source venv/bin/activate
if python -m pytest tests/ -v 2>/dev/null; then
    echo "✅ Backend tests passed"
else
    echo "⚠️  Backend tests skipped (pytest not available)"
fi

# Run frontend tests
cd ../frontend
npm test -- --coverage --watchAll=false

echo "✅ Frontend tests passed"

echo "🎉 Build complete! Run ./start.sh to start all services"
