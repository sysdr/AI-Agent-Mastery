#!/bin/bash
echo "🎬 Running AI Agent Observability Demo..."

source venv/bin/activate

# Generate demo data
python3 << 'PYTHON'
import asyncio
import httpx
import random
import time

async def generate_demo_data():
    async with httpx.AsyncClient() as client:
        try:
            # Start some traces
            for i in range(5):
                response = await client.post(
                    "http://localhost:8000/api/traces/start",
                    params={"operation": f"ai_inference_{i}"}
                )
                if response.status_code == 200:
                    trace_id = response.json()["trace_id"]
                    
                    # Add spans
                    await client.post(
                        f"http://localhost:8000/api/traces/{trace_id}/spans",
                        params={
                            "span_name": "model_loading",
                            "duration_ms": random.uniform(100, 500)
                        }
                    )
                    
                    # Record confidence
                    await client.post(
                        "http://localhost:8000/api/metrics/confidence",
                        params={
                            "agent_id": f"agent_{i}",
                            "confidence": random.uniform(0.7, 0.95)
                        }
                    )
                    
                    # Record request
                    await client.post(
                        "http://localhost:8000/api/metrics/request",
                        params={
                            "agent_type": "text_generation",
                            "status": "success",
                            "response_time": random.uniform(0.1, 2.0)
                        }
                    )
                    
                    time.sleep(1)
            
            print("✅ Demo data generated successfully!")
            
        except Exception as e:
            print(f"⚠️ Error generating demo data: {e}")

asyncio.run(generate_demo_data())
PYTHON

echo "🎯 Demo data generated!"
echo "🌐 Open http://localhost:3000 to see the dashboard"
