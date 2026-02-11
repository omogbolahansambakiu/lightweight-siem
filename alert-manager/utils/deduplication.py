"""Alert Deduplication"""
import hashlib
import time
from collections import defaultdict

class AlertDeduplicator:
    def __init__(self, window_seconds=300):
        self.window_seconds = window_seconds
        self.seen_alerts = defaultdict(float)
    
    def is_duplicate(self, alert):
        alert_hash = self._hash_alert(alert)
        
        current_time = time.time()
        last_seen = self.seen_alerts.get(alert_hash, 0)
        
        if current_time - last_seen < self.window_seconds:
            return True
        
        self.seen_alerts[alert_hash] = current_time
        self._cleanup_old()
        
        return False
    
    def _hash_alert(self, alert):
        key_fields = [
            alert.get('rule', {}).get('id'),
            alert.get('event', {}).get('source', {}).get('ip'),
            alert.get('event', {}).get('destination', {}).get('ip')
        ]
        
        key_string = ':'.join(str(f) for f in key_fields)
        return hashlib.md5(key_string.encode()).hexdigest()
    
    def _cleanup_old(self):
        current_time = time.time()
        cutoff = current_time - (self.window_seconds * 2)
        
        to_remove = [k for k, v in self.seen_alerts.items() if v < cutoff]
        for k in to_remove:
            del self.seen_alerts[k]
