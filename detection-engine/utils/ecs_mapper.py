"""ECS (Elastic Common Schema) Mapper"""
from typing import Dict, Any
from datetime import datetime

class ECSMapper:
    """Maps parsed events to ECS format"""
    
    def map(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Map event to ECS format"""
        
        ecs_event = {
            '@timestamp': event.get('@timestamp', datetime.utcnow().isoformat()),
            'ecs': {
                'version': '8.0.0'
            }
        }
        
        # Map fields to ECS
        if 'event' in event:
            ecs_event['event'] = event['event']
        
        if 'source' in event:
            ecs_event['source'] = event['source']
        
        if 'destination' in event:
            ecs_event['destination'] = event['destination']
        
        if 'host' in event:
            ecs_event['host'] = event['host']
        
        if 'user' in event:
            ecs_event['user'] = event['user']
        
        if 'process' in event:
            ecs_event['process'] = event['process']
        
        if 'network' in event:
            ecs_event['network'] = event['network']
        
        if 'http' in event:
            ecs_event['http'] = event['http']
        
        if 'url' in event:
            ecs_event['url'] = event['url']
        
        if 'file' in event:
            ecs_event['file'] = event['file']
        
        if 'dns' in event:
            ecs_event['dns'] = event['dns']
        
        # Preserve message
        if 'message' in event:
            ecs_event['message'] = event['message']
        
        # Add tags
        if 'tags' in event:
            ecs_event['tags'] = event['tags']
        
        # Preserve metadata
        if '@metadata' in event:
            ecs_event['@metadata'] = event['@metadata']
        
        return ecs_event
