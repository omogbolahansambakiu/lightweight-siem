"""Alert Throttling"""
from collections import defaultdict
import time

class AlertThrottler:
    def __init__(self, window_seconds=3600, max_alerts=100):
        self.window_seconds = window_seconds
        self.max_alerts = max_alerts
        self.alert_counts = defaultdict(list)
    
    def should_throttle(self, alert):
        rule_id = alert.get('rule', {}).get('id')
        
        current_time = time.time()
        self.alert_counts[rule_id].append(current_time)
        
        # Clean old timestamps
        cutoff = current_time - self.window_seconds
        self.alert_counts[rule_id] = [
            ts for ts in self.alert_counts[rule_id]
            if ts > cutoff
        ]
        
        return len(self.alert_counts[rule_id]) > self.max_alerts
