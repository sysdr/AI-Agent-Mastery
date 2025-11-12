from locust import HttpUser, task, between
import random

class AIAgentUser(HttpUser):
    wait_time = between(1, 3)
    
    @task(3)
    def chat_query(self):
        queries = [
            "What is artificial intelligence?",
            "Explain machine learning",
            "How does deep learning work?",
            "What are neural networks?",
            "Describe natural language processing"
        ]
        
        self.client.post("/api/v1/agent/chat", json={
            "query": random.choice(queries),
            "agent_type": "technical"
        })
    
    @task(1)
    def system_metrics(self):
        self.client.get("/api/v1/metrics/system")
    
    @task(1)
    def business_metrics(self):
        self.client.get("/api/v1/metrics/business")
    
    @task(1)
    def health_check(self):
        self.client.get("/health")
