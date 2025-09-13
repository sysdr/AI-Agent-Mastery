# AI Agent Learning & Compliance System

A production-ready AI agent learning system with privacy protection, bias detection, A/B testing, and explainable recommendations.

## Features

- **Privacy-Preserving Learning**: Differential privacy for user preference learning
- **Real-time Bias Detection**: Continuous monitoring for fairness violations
- **A/B Testing Framework**: Statistical significance testing with privacy preservation
- **Explainable Recommendations**: Full audit trails and reasoning for every recommendation
- **Interactive Dashboard**: Real-time monitoring and management interface

## Quick Start

1. **Build the system:**
   ```bash
   ./build.sh
   ```

2. **Start all services:**
   ```bash
   ./start.sh
   ```

3. **Generate demo data:**
   ```bash
   python scripts/generate_demo_data.py
   ```

4. **Access the dashboard:**
   - Frontend: http://localhost:3000
   - API: http://localhost:8000
   - API Docs: http://localhost:8000/docs

## Architecture

The system consists of four main services:
- **Preference Learning Service**: Privacy-preserving user preference modeling
- **Bias Detection Engine**: Real-time fairness monitoring
- **A/B Testing Framework**: Statistical experimentation platform
- **Recommendation Engine**: Explainable recommendation generation

## Testing

Run the test suite:
```bash
cd backend && python -m pytest ../tests/ -v
```

## Docker Deployment

```bash
docker-compose up -d
```

## Environment Variables

Set these in `backend/.env`:
- `GEMINI_API_KEY`: Your Gemini AI API key
- `DATABASE_URL`: PostgreSQL connection string
- `REDIS_URL`: Redis connection string

## Stopping the System

```bash
./stop.sh
```
