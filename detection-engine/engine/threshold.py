"""Threshold Tracker - Tracks event counts for threshold detection"""
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, Any
import structlog

logger = structlog.get_logger()

class ThresholdTracker:
    """Tracks event counts for threshold-based detection"""
    
    def __init__(self):
        self.counters = defaultdict(list)
        self.logger = logger.bind(component="threshold")
    
    def check(self, rule: Dict[str, Any], event: Dict[str, Any]) -> bool:
        """Check if threshold is exceeded"""
        detection = rule.get("detection", {})
        condition = detection.get("condition", "")
        timeframe = detection.get("timeframe", "5m")
        group_by = detection.get("groupby", [])
        
        # Parse condition (e.g., "count > 5")
        threshold = self._parse_threshold(condition)
        
        # Get grouping key
        key = f"{rule.get('id')}:{self._get_group_key(event, group_by)}"
        
        # Add event
        self.counters[key].append(datetime.utcnow())
        
        # Clean old events
        self._cleanup_old_counts(key, timeframe)
        
        # Check threshold
        return len(self.counters[key]) > threshold
    
    def _parse_threshold(self, condition: str) -> int:
        """Parse threshold from condition string"""
        # Simple parsing: "count > 5" -> 5
        parts = condition.split()
        if len(parts) >= 3:
            return int(parts[2])
        return 0
    
    def _get_group_key(self, event: Dict, fields: list) -> str:
        """Generate grouping key"""
        values = []
        for field in fields:
            value = self._get_nested_value(event, field)
            values.append(str(value) if value else "null")
        return ":".join(values)
    
    def _get_nested_value(self, obj: Dict, key: str) -> Any:
        """Get nested dictionary value"""
        keys = key.split(".")
        value = obj
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return None
        return value
    
    def _cleanup_old_counts(self, key: str, timeframe: str):
        """Remove old timestamps"""
        minutes = int(timeframe.rstrip('m'))
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        
        self.counters[key] = [
            ts for ts in self.counters[key]
            if ts > cutoff
        ]
