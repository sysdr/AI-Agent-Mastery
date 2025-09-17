from locust import HttpUser, task, between

class ChatUser(HttpUser):
    wait_time = between(1, 5)
    
    def on_start(self):
        self.headers = {"Authorization": "Bearer demo-token"}
    
    @task
    def send_chat_message(self):
        self.client.post("/chat", 
            json={"content": "Hello, how are you?"}, 
            headers=self.headers
        )
    
    @task
    def check_health(self):
        self.client.get("/health")
    
    @task
    def get_metrics(self):
        self.client.get("/metrics")
