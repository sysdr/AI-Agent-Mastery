#!/bin/bash
set -e

echo "=== Building Enterprise AI Agent Platform ==="

# Create virtual environment
echo "Creating virtual environment..."
cd backend
python3 -m venv venv
source venv/bin/activate

# Install dependencies
echo "Installing Python dependencies..."
pip install --upgrade pip
pip install -r requirements.txt

# Run tests
echo "Running tests..."
export GEMINI_API_KEY=your-gemini-api-key
export PYTHONPATH="${PYTHONPATH}:$(pwd)"
pytest tests/ -v

cd ../frontend
echo "Installing Node dependencies..."
npm install

echo "=== Build Complete ==="
echo "Next steps:"
echo "1. Run: ./start.sh   # Start all services"
echo "2. Open: http://localhost:3000 (Frontend)"
echo "3. Open: http://localhost:8000/docs (API Docs)"
echo "4. Open: http://localhost:9090 (Prometheus)"
echo "5. Open: http://localhost:3001 (Grafana)"
