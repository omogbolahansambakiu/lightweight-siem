"""Email Notifier"""
import os
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
from jinja2 import Template
import structlog

logger = structlog.get_logger()

class EmailNotifier:
    def __init__(self):
        self.enabled = os.getenv("SMTP_ENABLED", "false").lower() == "true"
        self.smtp_server = os.getenv("SMTP_SERVER")
        self.smtp_port = int(os.getenv("SMTP_PORT", 587))
        self.username = os.getenv("SMTP_USER")
        self.password = os.getenv("SMTP_PASSWORD")
        self.from_addr = os.getenv("SMTP_FROM", "siem@example.com")
        
    def send(self, alert):
        severity = alert.get('rule', {}).get('severity', 'MEDIUM')
        to_addr = os.getenv(f"SMTP_TO_{severity}", "security@example.com")
        
        msg = MIMEMultipart()
        msg['From'] = self.from_addr
        msg['To'] = to_addr
        msg['Subject'] = f"[{severity}] {alert.get('rule', {}).get('name')}"
        
        body = self._render_template(alert)
        msg.attach(MIMEText(body, 'html'))
        
        with smtplib.SMTP(self.smtp_server, self.smtp_port) as server:
            server.starttls()
            server.login(self.username, self.password)
            server.send_message(msg)
    
    def _render_template(self, alert):
        return f"""
        <h2>Security Alert</h2>
        <p><strong>Rule:</strong> {alert.get('rule', {}).get('name')}</p>
        <p><strong>Severity:</strong> {alert.get('rule', {}).get('severity')}</p>
        <p><strong>Description:</strong> {alert.get('rule', {}).get('description')}</p>
        <pre>{json.dumps(alert.get('event', {}), indent=2)}</pre>
        """
