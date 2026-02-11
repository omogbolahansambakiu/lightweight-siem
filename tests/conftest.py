"""Pytest configuration"""
import pytest

@pytest.fixture
def sample_event():
    return {
        "@timestamp": "2024-01-15T10:30:00Z",
        "source": {"ip": "192.168.1.100"},
        "event": {"category": "authentication"}
    }
