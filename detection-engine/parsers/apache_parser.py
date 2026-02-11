"""Apache/Nginx Web Server Log Parser"""
import re
from typing import Dict, Any, Optional
from urllib.parse import urlparse, parse_qs

class ApacheParser:
    """Parse Apache/Nginx access logs"""
    
    # Combined log format
    PATTERN = re.compile(
        r'^(?P<client>\S+)\s+\S+\s+(?P<userid>\S+)\s+'
        r'\[(?P<datetime>[^\]]+)\]\s+'
        r'"(?P<method>\S+)\s+(?P<path>\S+)\s+(?P<protocol>\S+)"\s+'
        r'(?P<status>\d{3})\s+'
        r'(?P<size>\S+)\s+'
        r'"(?P<referrer>[^"]*)"\s+'
        r'"(?P<user_agent>[^"]*)"'
    )
    
    def parse(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse Apache/Nginx log"""
        message = event.get('message', '')
        
        match = self.PATTERN.match(message)
        if not match:
            return None
        
        url_path = match.group('path')
        parsed_url = urlparse(url_path)
        
        parsed = {
            'source': {
                'ip': match.group('client')
            },
            'http': {
                'request': {
                    'method': match.group('method'),
                    'referrer': match.group('referrer')
                },
                'response': {
                    'status_code': int(match.group('status')),
                    'body': {
                        'bytes': int(match.group('size')) if match.group('size') != '-' else 0
                    }
                },
                'version': match.group('protocol')
            },
            'url': {
                'path': parsed_url.path,
                'query': parsed_url.query,
                'full': url_path
            },
            'user_agent': {
                'original': match.group('user_agent')
            },
            'event': {
                'category': 'web',
                'type': 'access'
            }
        }
        
        return parsed
