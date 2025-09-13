from collections import defaultdict, deque
from datetime import datetime, timedelta
import threading

class MetricsCollector:
    def __init__(self):
        self.interaction_counts = defaultdict(int)
        self.bias_alerts = deque(maxlen=1000)
        self.privacy_usage = defaultdict(float)
        self.recommendation_metrics = defaultdict(list)
        self.lock = threading.Lock()
    
    def record_interaction(self, interaction_type: str):
        with self.lock:
            self.interaction_counts[interaction_type] += 1
    
    def record_bias_alert(self, severity: str):
        with self.lock:
            self.bias_alerts.append({
                'timestamp': datetime.utcnow(),
                'severity': severity
            })
    
    def get_interaction_rate(self) -> dict:
        with self.lock:
            return dict(self.interaction_counts)
    
    def get_bias_alerts(self) -> int:
        with self.lock:
            return len(self.bias_alerts)
    
    def get_privacy_usage(self) -> dict:
        with self.lock:
            return dict(self.privacy_usage)
    
    def get_recommendation_metrics(self) -> dict:
        with self.lock:
            return dict(self.recommendation_metrics)
