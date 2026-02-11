"""Syslog Parser"""
import re
from datetime import datetime
from typing import Dict, Any, Optional

class SyslogParser:
    """Parse syslog format messages"""
    
    # Syslog regex pattern
    PATTERN = re.compile(
        r'^(?P<timestamp>\w{3}\s+\d{1,2}\s+\d{2}:\d{2}:\d{2})\s+'
        r'(?P<hostname>\S+)\s+'
        r'(?P<process>\S+?)(\[(?P<pid>\d+)\])?:\s+'
        r'(?P<message>.*)$'
    )
    
    def parse(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse syslog message"""
        message = event.get('message', '')
        
        match = self.PATTERN.match(message)
        if not match:
            return None
        
        parsed = {
            'timestamp': match.group('timestamp'),
            'host': {
                'hostname': match.group('hostname')
            },
            'process': {
                'name': match.group('process'),
                'pid': match.group('pid')
            },
            'message': match.group('message'),
            'log': {
                'level': self._extract_level(match.group('message'))
            }
        }
        
        return parsed
    
    def _extract_level(self, message: str) -> str:
        """Extract log level from message"""
        message_lower = message.lower()
        
        if 'error' in message_lower or 'failed' in message_lower:
            return 'error'
        elif 'warning' in message_lower or 'warn' in message_lower:
            return 'warning'
        elif 'info' in message_lower:
            return 'info'
        else:
            return 'notice'
