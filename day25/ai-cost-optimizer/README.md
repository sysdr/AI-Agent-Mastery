# AI Agent Cost Optimization & Performance Engineering Platform

Enterprise-grade cost optimization and performance monitoring platform for AI agents at scale.

## Features

- 💰 **Cost Tracking**: Real-time cost monitoring for AI requests
- 📊 **Performance Monitoring**: System metrics and performance analysis  
- 🔮 **Cost Forecasting**: Predictive cost analysis with confidence intervals
- 🎯 **Optimization Engine**: Automated cost optimization recommendations
- 📱 **Modern Dashboard**: Responsive web interface with real-time updates

## Quick Start

### Prerequisites

- Python 3.11+
- Node.js 18+
- Redis Server
- Gemini API Key

### 1. Clone and Setup

```bash
git clone <repository-url>
cd ai-cost-optimizer
chmod +x *.sh
```

### 2. Build

```bash
./build.sh
```

### 3. Configure Environment

```bash
cp .env.example .env
# Edit .env with your GEMINI_API_KEY
export GEMINI_API_KEY="your-api-key-here"
```

### 4. Start Application

```bash
./start.sh
```

### 5. Access Dashboard

- 🌐 **Web Dashboard**: http://localhost:3000
- 🔧 **API Docs**: http://localhost:8000/docs
- 📊 **Health Check**: http://localhost:8000/health

### 6. Run Demo

```bash
python demo.py
```

## Docker Deployment

```bash
# Set environment variable
export GEMINI_API_KEY="your-api-key-here"

# Start with Docker Compose
docker-compose up -d

# Scale services
docker-compose up -d --scale backend=3
```

## API Endpoints

### Cost Management
- `POST /api/cost/request` - Make tracked AI request
- `GET /api/cost/summary/{agent_id}` - Get cost summary
- `GET /api/cost/optimization/{agent_id}` - Get optimization opportunities

### Performance Monitoring  
- `GET /api/performance/summary/{agent_id}` - Get performance metrics
- `POST /api/performance/start/{agent_id}` - Start monitoring
- `POST /api/performance/stop/{agent_id}` - Stop monitoring

### Forecasting
- `GET /api/forecast/costs/{agent_id}` - Get cost forecast

## Architecture

The platform uses a microservices architecture with:

- **FastAPI Backend**: Handles API requests and business logic
- **Redis**: Real-time data storage and caching
- **React Frontend**: Modern responsive dashboard
- **Gemini AI**: LLM API integration with cost tracking

## Testing

```bash
# Backend tests
cd backend && python -m pytest tests/ -v

# Frontend tests  
cd frontend && npm test

# Integration tests
python -m pytest backend/tests/test_integration.py -v
```

## Monitoring

The platform provides comprehensive monitoring including:

- Real-time cost tracking per request
- Performance metrics (CPU, memory, response times)
- Error rates and success metrics
- Predictive cost forecasting
- Optimization recommendations

## Production Deployment

For production deployment:

1. Configure environment variables
2. Set up SSL/TLS certificates
3. Configure load balancing
4. Set up monitoring and alerting
5. Configure backup strategies for Redis data

## Stop Application

```bash
./stop.sh
```

---

Built with ❤️ for the AI Agent Mastery Course - Day 25
