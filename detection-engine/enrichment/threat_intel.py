"""Threat Intelligence Enrichment"""
import json
import os
from typing import Dict, Any, Set
import structlog

logger = structlog.get_logger()

class ThreatIntelEnricher:
    """Enriches events with threat intelligence data"""
    
    def __init__(self, feeds_path="/app/config/threat-intel/indicators.json"):
        self.logger = logger.bind(component="threat-intel")
        self.feeds_path = feeds_path
        
        # IOC sets
        self.malicious_ips: Set[str] = set()
        self.malicious_domains: Set[str] = set()
        self.malicious_hashes: Set[str] = set()
        
        self._load_feeds()
    
    def _load_feeds(self):
        """Load threat intelligence feeds"""
        if not os.path.exists(self.feeds_path):
            self.logger.warning("Threat intel feed not found", path=self.feeds_path)
            return
        
        try:
            with open(self.feeds_path, 'r') as f:
                feeds = json.load(f)
                
                self.malicious_ips = set(feeds.get('ips', []))
                self.malicious_domains = set(feeds.get('domains', []))
                self.malicious_hashes = set(feeds.get('hashes', []))
                
            self.logger.info(
                "Threat intel loaded",
                ips=len(self.malicious_ips),
                domains=len(self.malicious_domains),
                hashes=len(self.malicious_hashes)
            )
        except Exception as e:
            self.logger.error("Failed to load threat intel", error=str(e))
    
    def enrich(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Add threat intelligence to event"""
        threat_indicators = []
        
        # Check source IP
        if 'source' in event and 'ip' in event['source']:
            if event['source']['ip'] in self.malicious_ips:
                threat_indicators.append({
                    'type': 'ip',
                    'value': event['source']['ip'],
                    'field': 'source.ip'
                })
        
        # Check destination IP
        if 'destination' in event and 'ip' in event['destination']:
            if event['destination']['ip'] in self.malicious_ips:
                threat_indicators.append({
                    'type': 'ip',
                    'value': event['destination']['ip'],
                    'field': 'destination.ip'
                })
        
        # Check domain
        if 'dns' in event and 'question' in event['dns']:
            domain = event['dns']['question'].get('name')
            if domain in self.malicious_domains:
                threat_indicators.append({
                    'type': 'domain',
                    'value': domain,
                    'field': 'dns.question.name'
                })
        
        # Add threat data to event
        if threat_indicators:
            event['threat'] = {
                'indicators': threat_indicators,
                'matched': True
            }
        
        return event
