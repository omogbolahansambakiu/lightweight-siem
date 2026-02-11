#!/usr/bin/env python3
"""Alert Manager - Handles alert notifications"""

import os
import sys
import signal
import time
import structlog
from dotenv import load_dotenv

sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from alert_manager import AlertManager

load_dotenv()

structlog.configure(
    processors=[
        structlog.processors.TimeStamper(fmt="iso"),
        structlog.stdlib.add_log_level,
        structlog.processors.JSONRenderer()
    ]
)

logger = structlog.get_logger()

class SIEMAlertManager:
    def __init__(self):
        self.running = False
        self.logger = logger.bind(component="alert-manager")
        self.alert_manager = AlertManager()
    
    def start(self):
        self.logger.info("Starting Alert Manager...")
        self.running = True
        
        signal.signal(signal.SIGINT, self._signal_handler)
        signal.signal(signal.SIGTERM, self._signal_handler)
        
        try:
            self.alert_manager.start()
            
            while self.running:
                time.sleep(1)
        except KeyboardInterrupt:
            pass
        finally:
            self.stop()
    
    def stop(self):
        self.logger.info("Stopping Alert Manager...")
        self.running = False
        self.alert_manager.stop()
    
    def _signal_handler(self, signum, frame):
        self.running = False

if __name__ == "__main__":
    manager = SIEMAlertManager()
    manager.start()
