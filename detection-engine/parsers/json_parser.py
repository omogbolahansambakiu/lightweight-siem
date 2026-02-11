"""JSON Log Parser"""
import json
from typing import Dict, Any, Optional

class JSONParser:
    """Parse JSON formatted logs"""
    
    def parse(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse JSON event"""
        
        # If already parsed, return as-is
        if isinstance(event, dict) and '@timestamp' in event:
            return event
        
        # Try to parse message field as JSON
        message = event.get('message', '')
        if isinstance(message, str):
            try:
                parsed = json.loads(message)
                return parsed
            except json.JSONDecodeError:
                pass
        
        # Return event as-is
        return event
