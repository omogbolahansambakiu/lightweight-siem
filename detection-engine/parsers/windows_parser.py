"""Windows Event Log Parser"""
from typing import Dict, Any, Optional

class WindowsParser:
    """Parse Windows Event Logs"""
    
    def parse(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse Windows event"""
        
        parsed = {
            'event': {
                'code': event.get('winlog', {}).get('event_id'),
                'provider': event.get('winlog', {}).get('provider_name'),
                'category': self._map_event_category(event.get('winlog', {}))
            },
            'host': {
                'hostname': event.get('host', {}).get('name'),
                'os': {
                    'platform': 'windows'
                }
            },
            'user': {
                'name': event.get('winlog', {}).get('event_data', {}).get('TargetUserName'),
                'domain': event.get('winlog', {}).get('event_data', {}).get('TargetDomainName')
            },
            'message': event.get('message', ''),
            '@timestamp': event.get('@timestamp')
        }
        
        return parsed
    
    def _map_event_category(self, winlog: Dict) -> str:
        """Map event ID to category"""
        event_id = winlog.get('event_id')
        
        auth_events = [4624, 4625, 4648, 4672, 4776]
        account_events = [4720, 4722, 4724, 4732, 4740, 4756]
        
        if event_id in auth_events:
            return 'authentication'
        elif event_id in account_events:
            return 'iam'
        
        return 'system'
