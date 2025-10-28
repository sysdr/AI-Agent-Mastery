# AI Security Platform - Quick Start

## How to Start the Application

### Option 1: Quick Restart (Recommended)
```bash
chmod +x quick_restart.sh
./quick_restart.sh
```

### Option 2: Manual Start
```bash
chmod +x start.sh
./start.sh
```

### Option 3: If you get port conflicts
```bash
# Kill everything first
pkill -f uvicorn
pkill -f react-scripts
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9

# Then start
./start.sh
```

## Once Running

- **Frontend**: http://localhost:3000
- **Backend API**: http://localhost:8000
- **API Docs**: http://localhost:8000/docs

## Login Credentials

- Email: `admin@example.com`
- Password: `admin123`

## To Stop the Services

Press `Ctrl+C` in the terminal where you ran `./start.sh`

## What Was Fixed

1. ✅ CORS configuration - Backend now accepts requests from localhost:3000
2. ✅ Database creation - Automatic creation of `ai_security` database
3. ✅ Missing frontend files - Created index.html, index.tsx, tsconfig.json
4. ✅ Dependencies - Added pydantic-settings, grpcio, google-auth

## Troubleshooting

If you still see CORS errors:
```bash
# Check if backend is running
curl http://localhost:8000/health

# If not, manually start backend
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000
```


