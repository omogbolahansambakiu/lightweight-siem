"""Slack Notifier"""
import os
import requests
import json
import structlog

logger = structlog.get_logger()

class SlackNotifier:
    def __init__(self):
        self.enabled = os.getenv("SLACK_ENABLED", "false").lower() == "true"
        self.webhook_url = os.getenv("SLACK_WEBHOOK_URL")
    
    def send(self, alert):
        severity = alert.get('rule', {}).get('severity', 'MEDIUM')
        
        color_map = {
            'CRITICAL': 'danger',
            'HIGH': 'warning',
            'MEDIUM': '#FFA500',
            'LOW': 'good'
        }
        
        payload = {
            "attachments": [{
                "color": color_map.get(severity, '#808080'),
                "title": f"[{severity}] {alert.get('rule', {}).get('name')}",
                "text": alert.get('rule', {}).get('description'),
                "fields": [
                    {"title": "Source IP", "value": alert.get('event', {}).get('source', {}).get('ip', 'N/A'), "short": True},
                    {"title": "Severity", "value": severity, "short": True}
                ],
                "footer": "SIEM Alert",
                "ts": alert.get('@timestamp')
            }]
        }
        
        requests.post(self.webhook_url, json=payload)
