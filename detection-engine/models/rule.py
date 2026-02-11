"""Rule Model"""
from dataclasses import dataclass, field
from typing import Dict, Any, List, Optional

@dataclass
class DetectionRule:
    """Detection rule model"""
    
    id: str
    name: str
    description: str
    severity: str
    category: str
    
    detection: Dict[str, Any]
    enabled: bool = True
    
    actions: List[str] = field(default_factory=list)
    tags: List[str] = field(default_factory=list)
    metadata: Dict[str, Any] = field(default_factory=dict)
    
    def matches(self, event: Dict[str, Any]) -> bool:
        """Check if event matches rule"""
        # Implementation in detection_engine.py
        pass
