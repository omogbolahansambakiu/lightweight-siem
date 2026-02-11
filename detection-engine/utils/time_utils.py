"""Time utilities"""
from datetime import datetime, timedelta
from typing import Union

def parse_timeframe(timeframe: str) -> timedelta:
    """Parse timeframe string (e.g., '5m', '1h', '30s')"""
    
    unit = timeframe[-1]
    value = int(timeframe[:-1])
    
    if unit == 's':
        return timedelta(seconds=value)
    elif unit == 'm':
        return timedelta(minutes=value)
    elif unit == 'h':
        return timedelta(hours=value)
    elif unit == 'd':
        return timedelta(days=value)
    else:
        raise ValueError(f"Unknown time unit: {unit}")

def format_timestamp(dt: Union[datetime, str]) -> str:
    """Format timestamp to ISO format"""
    if isinstance(dt, str):
        return dt
    return dt.isoformat()
