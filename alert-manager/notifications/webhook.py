"""Webhook Notifier"""
import os
import requests
import structlog

logger = structlog.get_logger()

class WebhookNotifier:
    def __init__(self):
        self.enabled = os.getenv("WEBHOOK_ENABLED", "false").lower() == "true"
        self.url = os.getenv("WEBHOOK_URL")
        self.auth_token = os.getenv("WEBHOOK_AUTH_TOKEN")
    
    def send(self, alert):
        headers = {}
        if self.auth_token:
            headers['Authorization'] = f"Bearer {self.auth_token}"
        
        requests.post(self.url, json=alert, headers=headers, timeout=10)
