#!/bin/bash

echo "🚀 Building Multi-Agent Security System"

# Create Python virtual environment
python3 -m venv venv
source venv/bin/activate

# Install Python dependencies
cd backend
pip install --upgrade pip
pip install -r requirements.txt

# Create .env if it doesn't exist
if [ ! -f .env ]; then
    cp .env .env
    echo "⚠️  Please update .env with your actual API keys"
fi

# Run database migrations
python -c "
from models.database import engine, Base
Base.metadata.create_all(bind=engine)
print('✅ Database tables created')
"

# Install frontend dependencies
cd ../frontend
npm install

echo "✅ Build complete!"
echo "📋 Next steps:"
echo "   1. Update backend/.env with your Gemini API key"
echo "   2. Start PostgreSQL and Redis services"
echo "   3. Run ./start.sh to start the system"
