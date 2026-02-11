"""Parser Engine - Orchestrates log parsing"""
import json
from typing import Dict, Any, Optional
import structlog

from parsers.syslog_parser import SyslogParser
from parsers.windows_parser import WindowsParser
from parsers.apache_parser import ApacheParser
from parsers.json_parser import JSONParser
from parsers.firewall_parser import FirewallParser

logger = structlog.get_logger()

class ParserEngine:
    """Main parser engine that routes logs to appropriate parsers"""
    
    def __init__(self):
        self.logger = logger.bind(component="parser-engine")
        
        # Initialize parsers
        self.parsers = {
            'syslog': SyslogParser(),
            'windows': WindowsParser(),
            'apache': ApacheParser(),
            'web_access': ApacheParser(),
            'json': JSONParser(),
            'firewall': FirewallParser()
        }
    
    def parse(self, raw_event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse raw event based on source type"""
        try:
            # Determine parser to use
            source_type = raw_event.get('source_type') or raw_event.get('log_type', 'json')
            
            parser = self.parsers.get(source_type, self.parsers['json'])
            
            # Parse
            parsed = parser.parse(raw_event)
            
            if parsed:
                # Add metadata
                parsed['@metadata'] = {
                    'parser': parser.__class__.__name__,
                    'source_type': source_type
                }
                
                return parsed
            
        except Exception as e:
            self.logger.error("Parsing failed", error=str(e), event=raw_event)
        
        return None
