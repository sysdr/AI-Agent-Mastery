# AI Conversation Manager - Day 9 Implementation

Advanced conversation management system with compliance validation, personality monitoring, and intelligent routing.

## Quick Start

### Without Docker
```bash
./build.sh    # Install dependencies and run tests
./start.sh    # Start all services
./stop.sh     # Stop all services
```

### With Docker
```bash
docker-compose up --build
```

## Features

- **Real-time Chat Interface** with WebSocket support
- **Compliance Validation** with injection prevention
- **Personality Monitoring** with consistency tracking
- **Intelligent Routing** with escalation protocols
- **Production Monitoring** with real-time metrics

## Architecture

- **Backend**: FastAPI + Python 3.11
- **Frontend**: React 18 + Material-UI
- **Database**: Redis for session storage
- **AI**: Google Gemini API
- **Monitoring**: Prometheus metrics

## API Endpoints

- `GET /` - Health check
- `WS /ws/{session_id}` - WebSocket chat
- `GET /api/monitoring/compliance/stats` - Compliance metrics
- `GET /api/monitoring/personality/consistency` - Personality metrics

## Testing

```bash
cd backend
source venv/bin/activate
pytest tests/ -v
```

## Configuration

Set environment variables in `backend/.env`:
- `GEMINI_API_KEY`: Your Google Gemini API key
- `REDIS_URL`: Redis connection URL
- `SECRET_KEY`: JWT secret key
