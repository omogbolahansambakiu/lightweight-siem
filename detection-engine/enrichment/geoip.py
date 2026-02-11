"""GeoIP Enrichment"""
import geoip2.database
import os
import structlog
from typing import Dict, Any, Optional

logger = structlog.get_logger()

class GeoIPEnricher:
    """Enriches events with GeoIP data"""
    
    def __init__(self, db_path="/app/config/geoip/GeoLite2-City.mmdb"):
        self.logger = logger.bind(component="geoip-enricher")
        self.db_path = db_path
        self.reader = None
        
        try:
            self.reader = geoip2.database.Reader(db_path)
            self.logger.info("GeoIP database loaded", path=db_path)
        except Exception as e:
            self.logger.warning("GeoIP database not available", error=str(e))
    
    def enrich(self, event: Dict[str, Any]) -> Dict[str, Any]:
        """Add GeoIP data to event"""
        if not self.reader:
            return event
        
        # Enrich source IP
        if 'source' in event and 'ip' in event['source']:
            geo = self._lookup_ip(event['source']['ip'])
            if geo:
                event['source']['geo'] = geo
        
        # Enrich destination IP
        if 'destination' in event and 'ip' in event['destination']:
            geo = self._lookup_ip(event['destination']['ip'])
            if geo:
                event['destination']['geo'] = geo
        
        return event
    
    def _lookup_ip(self, ip: str) -> Optional[Dict[str, Any]]:
        """Lookup IP in GeoIP database"""
        try:
            response = self.reader.city(ip)
            
            return {
                'city_name': response.city.name,
                'country_name': response.country.name,
                'country_iso_code': response.country.iso_code,
                'continent_name': response.continent.name,
                'location': {
                    'lat': response.location.latitude,
                    'lon': response.location.longitude
                },
                'postal_code': response.postal.code,
                'timezone': response.location.time_zone
            }
        except Exception:
            return None
