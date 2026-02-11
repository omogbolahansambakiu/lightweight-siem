"""Event Model"""
from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime

@dataclass
class Event:
    """Normalized event model"""
    
    timestamp: datetime
    event_type: str
    category: str
    message: str
    
    source: Optional[Dict[str, Any]] = None
    destination: Optional[Dict[str, Any]] = None
    host: Optional[Dict[str, Any]] = None
    user: Optional[Dict[str, Any]] = None
    process: Optional[Dict[str, Any]] = None
    file: Optional[Dict[str, Any]] = None
    network: Optional[Dict[str, Any]] = None
    http: Optional[Dict[str, Any]] = None
    
    metadata: Dict[str, Any] = field(default_factory=dict)
    tags: list = field(default_factory=list)
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            '@timestamp': self.timestamp.isoformat(),
            'event': {
                'type': self.event_type,
                'category': self.category
            },
            'message': self.message,
            'source': self.source,
            'destination': self.destination,
            'host': self.host,
            'user': self.user,
            'process': self.process,
            'file': self.file,
            'network': self.network,
            'http': self.http,
            'tags': self.tags,
            '@metadata': self.metadata
        }
