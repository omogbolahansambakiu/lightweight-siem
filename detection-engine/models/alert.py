"""Alert Model"""
from dataclasses import dataclass, field
from typing import Dict, Any
from datetime import datetime

@dataclass
class Alert:
    """Security alert model"""
    
    rule_id: str
    rule_name: str
    severity: str
    description: str
    
    event: Dict[str, Any]
    timestamp: datetime = field(default_factory=datetime.utcnow)
    status: str = "new"
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary"""
        return {
            '@timestamp': self.timestamp.isoformat(),
            'rule': {
                'id': self.rule_id,
                'name': self.rule_name,
                'description': self.description,
                'severity': self.severity
            },
            'alert': {
                'status': self.status,
                'generated_at': self.timestamp.isoformat()
            },
            'event': self.event
        }
