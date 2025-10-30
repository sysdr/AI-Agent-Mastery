#!/bin/bash
echo "🔄 Restarting backend only (frontend will stay running)..."
killall -9 uvicorn 2>/dev/null
lsof -ti:8000 | xargs kill -9 2>/dev/null
sleep 2
cd backend
source venv/bin/activate
python -m uvicorn app.main:app --reload --host 0.0.0.0 --port 8000 > /tmp/backend.log 2>&1 &
echo "✅ Backend restarted with CORS fix"
echo "🌐 Your frontend at http://localhost:3000 should now work!"
echo "📊 Backend logs: tail -f /tmp/backend.log"


