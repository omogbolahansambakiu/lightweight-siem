"""DNS Enrichment"""
import socket
import os
from functools import lru_cache
import structlog
from typing import Dict, Any, Optional

logger = structlog.get_logger()

class DNSEnricher:
    """Enriches events with DNS data"""
    
    def __init__(self):
        self.logger = logger.bind(component="dns-enricher")
    
    def enrich(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Add DNS data to event"""
        
        # Reverse lookup for source IP
        if 'source' in event and 'ip' in event['source']:
            hostname = self._reverse_lookup(event['source']['ip'])
            if hostname:
                event['source']['domain'] = hostname
        
        # Reverse lookup for destination IP
        if 'destination' in event and 'ip' in event['destination']:
            hostname = self._reverse_lookup(event['destination']['ip'])
            if hostname:
                event['destination']['domain'] = hostname
        
        return event
    
    @lru_cache(maxsize=5000)
    def _reverse_lookup(self, ip: str) -> Optional[str]:
        """Perform reverse DNS lookup with caching"""
        try:
            hostname, _, _ = socket.gethostbyaddr(ip)
            return hostname
        except Exception:
            return None
