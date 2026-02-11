"""Parser tests"""
from detection_engine.parsers.syslog_parser import SyslogParser

def test_syslog_parser():
    parser = SyslogParser()
    event = {"message": "Jan 15 10:30:00 host sshd[1234]: Failed password"}
    result = parser.parse(event)
    assert result is not None
    assert "process" in result
