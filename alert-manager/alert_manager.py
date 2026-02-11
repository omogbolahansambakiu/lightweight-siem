"""Alert Manager Core"""

import json
import threading
import time
from typing import Dict, Any
import structlog
import redis
import os

from notifications.email import EmailNotifier
from notifications.slack import SlackNotifier
from notifications.pagerduty import PagerDutyNotifier
from notifications.webhook import WebhookNotifier
from utils.deduplication import AlertDeduplicator
from utils.throttling import AlertThrottler

logger = structlog.get_logger()

class AlertManager:
    def __init__(self):
        self.logger = logger.bind(component="alert-manager")
        self.running = False
        self.threads = []
        
        # Redis connection
        self.redis_client = redis.Redis(
            host=os.getenv("REDIS_HOST", "redis"),
            port=int(os.getenv("REDIS_PORT", 6379)),
            db=0,
            decode_responses=True
        )
        
        # Notifiers
        self.notifiers = {
            'email': EmailNotifier(),
            'slack': SlackNotifier(),
            'pagerduty': PagerDutyNotifier(),
            'webhook': WebhookNotifier()
        }
        
        # Utils
        self.deduplicator = AlertDeduplicator()
        self.throttler = AlertThrottler()
        
        self.logger.info("Alert Manager initialized")
    
    def start(self):
        self.running = True
        
        num_workers = int(os.getenv("ALERT_WORKERS", 2))
        for i in range(num_workers):
            thread = threading.Thread(target=self._worker, name=f"AlertWorker-{i}")
            thread.start()
            self.threads.append(thread)
    
    def stop(self):
        self.running = False
        for thread in self.threads:
            thread.join(timeout=5)
    
    def _worker(self):
        while self.running:
            try:
                alert_json = self.redis_client.rpop("alerts:queue")
                
                if not alert_json:
                    time.sleep(1)
                    continue
                
                alert = json.loads(alert_json)
                self._process_alert(alert)
                
            except Exception as e:
                self.logger.error("Worker error", error=str(e))
    
    def _process_alert(self, alert: Dict[str, Any]):
        # Deduplicate
        if self.deduplicator.is_duplicate(alert):
            self.logger.debug("Duplicate alert suppressed", rule=alert.get('rule', {}).get('name'))
            return
        
        # Throttle
        if self.throttler.should_throttle(alert):
            self.logger.debug("Alert throttled", rule=alert.get('rule', {}).get('name'))
            return
        
        # Send notifications
        severity = alert.get('rule', {}).get('severity', 'MEDIUM')
        
        if severity == "CRITICAL":
            self._notify(['pagerduty', 'slack', 'email'], alert)
        elif severity == "HIGH":
            self._notify(['slack', 'email'], alert)
        elif severity == "MEDIUM":
            self._notify(['email'], alert)
        else:
            # LOW - add to digest
            pass
        
        self.logger.info("Alert processed", rule=alert.get('rule', {}).get('name'), severity=severity)
    
    def _notify(self, channels: list, alert: Dict[str, Any]):
        for channel in channels:
            notifier = self.notifiers.get(channel)
            if notifier and notifier.enabled:
                try:
                    notifier.send(alert)
                except Exception as e:
                    self.logger.error(f"{channel} notification failed", error=str(e))
