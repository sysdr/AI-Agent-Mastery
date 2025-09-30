# Expert Agent System - Quick Start Guide

## 🚀 System is Currently Running!

### Access Points:
- **Dashboard:** http://localhost:3000
- **API:** http://localhost:8000
- **API Docs:** http://localhost:8000/docs

---

## 📊 Current Status

✅ **Backend:** Running on port 8000  
✅ **Frontend:** Running on port 3000  
✅ **Database:** Initialized with 8 knowledge entries  
✅ **Tests:** All 4 tests passed  
✅ **Dashboard Metrics:** All domains showing non-zero values

---

## 🎯 Quick Commands

### View Services
```bash
# Check running services
lsof -i :8000 -i :3000

# Check health
curl http://localhost:8000/health
```

### Stop Services
```bash
cd /home/systemdr/git/AI-Agent-Mastery/day18/expert_agent_system
./stop.sh
```

### Restart Services
```bash
cd /home/systemdr/git/AI-Agent-Mastery/day18/expert_agent_system
./start.sh
```

### Run Tests
```bash
cd /home/systemdr/git/AI-Agent-Mastery/day18/expert_agent_system
source venv/bin/activate
cd backend
python -m pytest tests/test_expert_agent.py -v
```

### Run Demo
```bash
cd /home/systemdr/git/AI-Agent-Mastery/day18/expert_agent_system
python demo_test.py
```

---

## 📁 Project Structure

```
expert_agent_system/
├── backend/
│   ├── app/
│   │   ├── agents/        # Expert agent logic
│   │   ├── core/          # Models & database
│   │   ├── knowledge/     # Knowledge management
│   │   └── validation/    # Source validation
│   ├── config/            # Settings
│   ├── tests/             # Unit tests
│   └── expert_agent.db    # SQLite database
├── frontend/
│   ├── src/
│   │   ├── components/    # React components
│   │   └── App.js         # Main app
│   └── package.json
├── build.sh               # Build script
├── start.sh               # Start script
├── stop.sh                # Stop script
└── demo_test.py          # Demo & validation
```

---

## 🔧 Configuration

### Set Gemini API Key (Optional for full AI features)
```bash
cd /home/systemdr/git/AI-Agent-Mastery/day18/expert_agent_system/backend
nano .env
# Set: GEMINI_API_KEY=your_actual_key_here
```

---

## 📈 Dashboard Features

### Domain Statistics
- View expertise stats for each domain
- See validation rates and confidence scores
- Monitor knowledge base entries

### Expert Query Interface
- Select domain (Technology, Medical, Legal, Finance, Science)
- Submit expert-level queries
- Adjust confidence thresholds
- View validation results

### Validation Results
- Confidence scores with visual indicators
- Expertise level classification
- Processing time metrics
- Source validation details
- Escalation warnings

### Audit Trail
- Query ID tracking
- Validation step breakdown
- Processing time analysis
- Timestamp logging

---

## 🧪 Test Coverage

✅ Domain expertise checking  
✅ Confidence calculation  
✅ Expertise level determination  
✅ Explanation generation  

---

## 📊 Current Metrics (Non-Zero ✅)

| Domain     | Entries | Validated | Rate  | Avg Confidence |
|------------|---------|-----------|-------|----------------|
| Technology | 2       | 2         | 100%  | 92.5%          |
| Medical    | 1       | 1         | 100%  | 92.0%          |
| Finance    | 1       | 1         | 100%  | 88.0%          |
| Science    | 2       | 2         | 100%  | 92.0%          |
| Legal      | 2       | 2         | 100%  | 89.5%          |

---

## 🎓 Usage Examples

### API Query Example
```bash
curl -X POST http://localhost:8000/query/technology \
  -H "Content-Type: application/json" \
  -d '{"query": "What are REST API best practices?", "required_confidence": 0.7}'
```

### Get Domain Stats
```bash
curl http://localhost:8000/stats/technology | python -m json.tool
```

---

## 🛠️ Troubleshooting

### Services Not Starting
```bash
# Kill any stuck processes
pkill -f uvicorn
pkill -f "npm start"

# Restart
./start.sh
```

### Port Already in Use
```bash
# Find and kill process using port
lsof -ti:8000 | xargs kill -9
lsof -ti:3000 | xargs kill -9
```

### Database Issues
```bash
cd backend
rm expert_agent.db
python init_db.py
```

---

## 📝 Notes

- System works without Gemini API key (uses mock responses)
- All core features are functional
- Dashboard metrics are live and updating
- No duplicate services running
- All validation tests passed

---

**Last Updated:** September 30, 2025
