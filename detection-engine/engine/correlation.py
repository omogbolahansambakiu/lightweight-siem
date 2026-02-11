"""Correlation Engine - Detects correlated events"""
from collections import defaultdict
from datetime import datetime, timedelta
from typing import Dict, List, Any
import structlog

logger = structlog.get_logger()

class CorrelationEngine:
    """Correlates events across time windows"""
    
    def __init__(self):
        self.event_buffer = defaultdict(list)
        self.logger = logger.bind(component="correlation")
    
    def check(self, rule: Dict[str, Any], event: Dict[str, Any]) -> bool:
        """Check if correlation condition is met"""
        correlation = rule.get("correlation", {})
        timeframe = correlation.get("timeframe", "5m")
        min_events = correlation.get("min_events", 2)
        group_by = correlation.get("group_by", [])
        
        # Get grouping key
        key = self._get_group_key(event, group_by)
        
        # Add to buffer
        self.event_buffer[key].append({
            "timestamp": datetime.utcnow(),
            "event": event
        })
        
        # Clean old events
        self._cleanup_old_events(key, timeframe)
        
        # Check threshold
        return len(self.event_buffer[key]) >= min_events
    
    def _get_group_key(self, event: Dict, fields: List[str]) -> str:
        """Generate grouping key from event fields"""
        values = []
        for field in fields:
            value = self._get_nested_value(event, field)
            values.append(str(value) if value else "null")
        return ":".join(values)
    
    def _get_nested_value(self, obj: Dict, key: str) -> Any:
        """Get nested dict value"""
        keys = key.split(".")
        value = obj
        for k in keys:
            if isinstance(value, dict):
                value = value.get(k)
            else:
                return None
        return value
    
    def _cleanup_old_events(self, key: str, timeframe: str):
        """Remove events outside time window"""
        minutes = int(timeframe.rstrip('m'))
        cutoff = datetime.utcnow() - timedelta(minutes=minutes)
        
        self.event_buffer[key] = [
            e for e in self.event_buffer[key]
            if e["timestamp"] > cutoff
        ]
