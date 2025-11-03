#!/bin/bash
python3 -m venv qa_env
source qa_env/bin/activate
pip install --upgrade pip
pip install fastapi uvicorn pytest requests aiohttp sqlalchemy psycopg2-binary
pip install prometheus-client grafana-api pydantic python-multipart
pip install google-generativeai python-jose[cryptography] passlib[bcrypt]
pip install locust bandit safety semgrep docker redis celery
pip install pytest-asyncio pytest-cov httpx
pip install psutil schedule APScheduler asyncpg
echo "Virtual environment setup complete!"
