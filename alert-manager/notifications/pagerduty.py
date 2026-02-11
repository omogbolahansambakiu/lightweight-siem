"""PagerDuty Notifier"""
import os
import requests
import structlog

logger = structlog.get_logger()

class PagerDutyNotifier:
    def __init__(self):
        self.enabled = os.getenv("PAGERDUTY_ENABLED", "false").lower() == "true"
        self.api_key = os.getenv("PAGERDUTY_API_KEY")
        self.service_key = os.getenv("PAGERDUTY_SERVICE_KEY")
    
    def send(self, alert):
        severity = alert.get('rule', {}).get('severity', 'MEDIUM')
        threshold = os.getenv("PAGERDUTY_SEVERITY_THRESHOLD", "HIGH")
        
        severity_levels = ['LOW', 'MEDIUM', 'HIGH', 'CRITICAL']
        
        if severity_levels.index(severity) < severity_levels.index(threshold):
            return
        
        payload = {
            "routing_key": self.service_key,
            "event_action": "trigger",
            "payload": {
                "summary": f"{alert.get('rule', {}).get('name')}",
                "severity": severity.lower(),
                "source": "SIEM",
                "custom_details": alert.get('event', {})
            }
        }
        
        requests.post("https://events.pagerduty.com/v2/enqueue", json=payload)
