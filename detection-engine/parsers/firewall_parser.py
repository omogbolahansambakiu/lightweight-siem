"""Firewall Log Parser"""
import re
from typing import Dict, Any, Optional

class FirewallParser:
    """Parse firewall logs (iptables, pfSense, etc.)"""
    
    def parse(self, event: Dict[str, Any]) -> Optional[Dict[str, Any]]:
        """Parse firewall log"""
        message = event.get('message', '')
        
        parsed = {
            'event': {
                'category': 'network',
                'type': 'denied' if 'DENY' in message or 'DROP' in message else 'allowed'
            }
        }
        
        # Extract common firewall fields
        src_ip = self._extract_field(message, r'SRC=(\S+)')
        dst_ip = self._extract_field(message, r'DST=(\S+)')
        src_port = self._extract_field(message, r'SPT=(\d+)')
        dst_port = self._extract_field(message, r'DPT=(\d+)')
        proto = self._extract_field(message, r'PROTO=(\S+)')
        
        if src_ip:
            parsed['source'] = {'ip': src_ip, 'port': int(src_port) if src_port else None}
        if dst_ip:
            parsed['destination'] = {'ip': dst_ip, 'port': int(dst_port) if dst_port else None}
        if proto:
            parsed['network'] = {'protocol': proto.lower()}
        
        parsed['message'] = message
        
        return parsed
    
    def _extract_field(self, message: str, pattern: str) -> Optional[str]:
        """Extract field using regex"""
        match = re.search(pattern, message)
        return match.group(1) if match else None
